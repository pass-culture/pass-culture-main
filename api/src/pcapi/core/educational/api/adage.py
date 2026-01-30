import json
import logging
import typing
from dataclasses import dataclass
from datetime import datetime
from functools import partial

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from pydantic.v1 import parse_obj_as

from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import models
from pcapi.core.educational import schemas
from pcapi.core.educational.api.venue import get_relative_venues_by_siret
from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional import send_eac_offerer_activation_email
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.cache import get_from_cache
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


def get_cultural_partners(
    *, since_date: datetime | None = None, force_update: bool = False
) -> schemas.AdageCulturalPartners:
    # TODO (jcicurel): once we have updated the adage ids sync logic, we do not need the cache anymore
    # and we can move the parsing as AdageCulturalPartners in the adage client directly

    CULTURAL_PARTNERS_CACHE_KEY = "api:adage_cultural_partner:cache"
    CULTURAL_PARTNERS_CACHE_TIMEOUT = 24 * 60 * 60  # 24h in seconds

    def _get_cultural_partners() -> str:
        adage_data = adage_client.get_cultural_partners()
        return json.dumps(adage_data)

    if not since_date:
        cultural_partners_json = get_from_cache(
            key_template=CULTURAL_PARTNERS_CACHE_KEY,
            retriever=_get_cultural_partners,
            expire=CULTURAL_PARTNERS_CACHE_TIMEOUT,
            return_type=str,
            force_update=force_update,
        )
    else:
        adage_data = adage_client.get_cultural_partners(since_date)
        cultural_partners_json = json.dumps(adage_data)

    cultural_partners_json = typing.cast(str, cultural_partners_json)
    cultural_partners = json.loads(cultural_partners_json)
    return parse_obj_as(schemas.AdageCulturalPartners, {"partners": cultural_partners})


def get_venue_by_siret_for_adage_iframe(
    siret: str, search_relative: bool
) -> tuple[offerers_models.Venue | None, list[int]]:
    relative = []
    venue = None
    if search_relative:
        venues = get_relative_venues_by_siret(siret, permanent_only=False)
        for candidate in venues:
            if candidate.siret == siret:
                venue = candidate
            else:
                relative.append(candidate.id)
    else:
        venue = offerers_repository.find_venue_by_siret_with_address(siret)
    return venue, relative


def get_venue_by_id_for_adage_iframe(
    venue_id: int, search_relative: bool
) -> tuple[offerers_models.Venue | None, list[int]]:
    relative = []
    venue = None
    if search_relative:
        venues = offerers_repository.find_relative_venue_by_id(venue_id)
        for candidate in venues:
            if candidate.id == venue_id:
                venue = candidate
            else:
                relative.append(candidate.id)
    else:
        venue = offerers_repository.find_venue_by_id_with_address(venue_id)
    return venue, relative


def synchronize_adage_partners(
    adage_partners: list[schemas.AdageCulturalPartner], apply: bool = False
) -> tuple[set[str], set[str]]:
    from pcapi.core.external.attributes.api import update_external_pro

    adage_id_by_venue_id: dict[int, str] = {}
    active_venue_ids: set[int] = set()
    active_sirens: set[str] = set()
    inactive_adage_ids: set[str] = set()
    inactive_venue_ids: set[int] = set()
    inactive_sirens: set[str] = set()

    ### STEP 1: read the adage partners and fill our containers of adage ids / venue ids / SIRENs
    for partner in adage_partners:
        adage_id = str(partner.id)

        if partner.venueId:
            adage_id_by_venue_id[partner.venueId] = adage_id

        if partner.siret:
            siren = partner.siret[:9]

            if partner.actif == 1:
                active_sirens.add(siren)
            else:
                inactive_sirens.add(siren)

        if adage_id and partner.synchroPass == 1 and partner.actif == 1:
            if partner.venueId:
                active_venue_ids.add(partner.venueId)
        else:
            inactive_adage_ids.add(adage_id)
            if partner.venueId:
                inactive_venue_ids.add(partner.venueId)

    ### STEP 2: fetch the Venues that are not active on Adage side and remove them from eac
    inactive_venues = (
        db.session.query(offerers_models.Venue)
        .filter(
            sa.or_(
                offerers_models.Venue.adageId.in_(inactive_adage_ids),
                offerers_models.Venue.id.in_(inactive_venue_ids),
            )
        )
        .options(sa_orm.joinedload(offerers_models.Venue.managingOfferer))
        .all()
    )
    logger.info(
        "Adage partners sync - %s inactive venues",
        len(inactive_venues),
        extra={"inactive_venues": [v.id for v in inactive_venues]},
    )

    offerer_sirens_with_inactive_venue: set[str] = set()
    for venue in inactive_venues:
        _remove_venue_adage_id(venue)
        offerer_sirens_with_inactive_venue.add(venue.managingOfferer.siren)

    db.session.flush()

    ### STEP 3: fetch the Venues that are active on Adage side and add them to eac
    active_venues = (
        db.session.query(offerers_models.Venue)
        .filter(offerers_models.Venue.id.in_(active_venue_ids))
        .options(sa_orm.joinedload(offerers_models.Venue.managingOfferer))
        .all()
    )
    logger.info(
        "Adage partners sync - %s active venues",
        len(active_venues),
        extra={"active_venues": [v.id for v in active_venues]},
    )

    new_adage_id_by_venue_id: dict[int, str] = {}
    offerer_sirens_with_active_venue: set[str] = set()
    for venue in active_venues:
        # update the external user in case of previous adageId being None
        # this is because we track if the user has an adageId, not the value of the adageId
        if apply and not venue.adageId:
            emails = offerers_repository.get_emails_by_venue(venue)

            for email in emails:
                update_external_pro(email)

            if venue.managingOfferer.isValidated:
                send_eac_offerer_activation_email(venue, list(emails))

        new_adage_id = adage_id_by_venue_id[venue.id]
        if venue.adageId != new_adage_id:
            new_adage_id_by_venue_id[venue.id] = new_adage_id
            _add_venue_adage_id(venue, new_adage_id)
            offerer_sirens_with_active_venue.add(venue.managingOfferer.siren)

    db.session.flush()
    logger.info(
        "Adage partners sync - %s adageId updates",
        len(new_adage_id_by_venue_id),
        extra={"updates": new_adage_id_by_venue_id},
    )

    ### STEP 4: list current allowed Offerers and Offerers that have a Venue with adageId
    allowed_offerers = (
        db.session.query(offerers_models.Offerer)
        .filter(
            offerers_models.Offerer.siren.in_(active_sirens),
            offerers_models.Offerer.allowedOnAdage.is_(True),
        )
        .options(sa_orm.load_only(offerers_models.Offerer.siren))
    )
    allowed_offerer_sirens = {o.siren for o in allowed_offerers}

    offerers_with_venue_adage_id = (
        db.session.query(offerers_models.Offerer)
        .join(offerers_models.Venue)
        .filter(
            offerers_models.Offerer.siren.in_(inactive_sirens | offerer_sirens_with_inactive_venue),
            offerers_models.Venue.adageId.is_not(None),
        )
        .options(sa_orm.load_only(offerers_models.Offerer.siren))
        # some venues with an adageId are soft-deleted, we need to include them so that the offerer keeps allowedOnAdage=True
        .execution_options(include_deleted=True)
    )
    offerer_sirens_with_venue_adage_id = {o.siren for o in offerers_with_venue_adage_id}

    ### STEP 5: compute Offerers to activate / deactivate
    sirens_to_activate = (
        active_sirens  # To activate = SIRENs that are active on Adage side
        | offerer_sirens_with_active_venue  # and the Offerers for which a Venue has just been activated
        - allowed_offerer_sirens  # ignore the already activated Offerers
    )
    sirens_to_deactivate = (
        inactive_sirens  # To deactivate = SIRENs of inactive partners on Adage side
        | offerer_sirens_with_inactive_venue  # and SIRENs for which we deactivated a Venue
        - offerer_sirens_with_venue_adage_id  # do not deactivate an Offerer that has a Venue with adageId
    )

    # STEP 6: for each Offerer to deactivate, first check if there is an active adage partner for this SIREN
    if sirens_to_deactivate:
        offerers_to_check = (
            db.session.query(offerers_models.Offerer)
            .filter(offerers_models.Offerer.siren.in_(sirens_to_deactivate))
            .options(sa_orm.joinedload(offerers_models.Offerer.managedVenues))
            .execution_options(include_deleted=True)
        )
        sirens_to_deactivate = {offerer.siren for offerer in offerers_to_check if _should_deactivate_offerer(offerer)}

    # STEP 7: update the Offerers
    logger.info(
        "Adage partners sync - %s SIRENs to activate",
        len(sirens_to_activate),
        extra={"sirens_to_activate": sirens_to_activate},
    )
    logger.info(
        "Adage partners sync - %s SIRENs to deactivate",
        len(sirens_to_deactivate),
        extra={"sirens_to_deactivate": sirens_to_deactivate},
    )

    db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.siren.in_(sirens_to_activate)).update(
        {offerers_models.Offerer.allowedOnAdage: True}, synchronize_session=False
    )
    db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.siren.in_(sirens_to_deactivate)).update(
        {offerers_models.Offerer.allowedOnAdage: False}, synchronize_session=False
    )

    db.session.flush()

    return sirens_to_activate, sirens_to_deactivate


def _add_venue_adage_id(venue: offerers_models.Venue, adage_id: str) -> None:
    if venue.adageId != adage_id:
        history_api.add_action(
            history_models.ActionType.INFO_MODIFIED,
            author=None,
            venue=venue,
            comment="Synchronisation ADAGE",
            modified_info={"adageId": {"old_info": venue.adageId, "new_info": adage_id}},
        )
        venue.adageId = adage_id

    if not venue.adageInscriptionDate:
        venue.adageInscriptionDate = date_utils.get_naive_utc_now()


def _should_deactivate_offerer(offerer: offerers_models.Offerer) -> bool:
    # the Offerer should remain active if
    # - it has one Venue with an adageId
    # OR
    # - there is one active Adage partner corresponding to the SIREN

    for venue in offerer.managedVenues:
        if venue.adageId is not None:
            return False

    adage_partners = adage_client.get_adage_offerer(siren=offerer.siren)
    for partner in adage_partners:
        if partner.actif == 1:
            return False

    return True


def synchronize_adage_ids_on_offerers(partners_from_adage: list[schemas.AdageCulturalPartner]) -> None:
    adage_sirens: set[str] = {p.siret[:9] for p in partners_from_adage if (p.actif == 1 and p.siret)}
    existing_sirens: dict[str, bool] = dict(
        db.session.query(  # type: ignore [arg-type]
            offerers_models.Offerer.siren,
            offerers_models.Offerer.allowedOnAdage,
        ).filter(
            offerers_models.Offerer.siren != None,
        )
    )
    existing_adage_sirens = {k for k, v in existing_sirens.items() if v}

    sirens_to_add = adage_sirens - existing_adage_sirens
    sirens_to_delete = existing_adage_sirens - adage_sirens

    # Tricky part here and hopefully this will be removed at some point.
    # We have some weird cases where the SIRET from Adage does not match the SIRET from
    # our linked venue.

    logger.info("SIRENs to add from SIRET: %s", sirens_to_add)
    logger.info("SIRENs to delete from SIRET: %s", sirens_to_delete)

    # check we don't remove offerers that do have valid venues
    existing_sirens_from_synchronized_venues: dict[str, bool] = dict(
        db.session.query(  # type: ignore [arg-type]
            offerers_models.Offerer.siren,
            offerers_models.Offerer.allowedOnAdage,
        )
        .join(offerers_models.Venue)
        .filter(
            offerers_models.Offerer.siren != None,
            offerers_models.Venue.adageId.is_not(None),
        )
        # some venues with an adageId are soft-deleted, we need to include them so that the offerer keeps allowedOnAdage=True
        .execution_options(include_deleted=True)
    )
    sirens_to_delete = sirens_to_delete - set(existing_sirens_from_synchronized_venues)
    sirens_to_add = sirens_to_add | {k for k, v in existing_sirens_from_synchronized_venues.items() if not v}

    logger.info("SIRENs to add: %s", sirens_to_add)
    logger.info("SIRENs to delete: %s", sirens_to_delete)
    logger.info("existing SIRENs from synchronized venues", extra=existing_sirens_from_synchronized_venues)

    db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.siren.in_(list(sirens_to_add))).update(
        {offerers_models.Offerer.allowedOnAdage: True}, synchronize_session=False
    )
    db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.siren.in_(list(sirens_to_delete))).update(
        {offerers_models.Offerer.allowedOnAdage: False}, synchronize_session=False
    )


@dataclass
class CulturalPartner:
    adage_id: str
    venue_id: int | None
    synchro: int | None
    active: int | None


def synchronize_adage_ids_on_venues(adage_cultural_partners: schemas.AdageCulturalPartners) -> None:
    from pcapi.core.external.attributes.api import update_external_pro

    adage_cps: list[CulturalPartner] = []
    venue_to_adage_id: dict[int, str] = {}

    for cultural_partner in adage_cultural_partners.partners:
        adage_id = str(cultural_partner.id)
        adage_cps.append(
            CulturalPartner(
                adage_id=adage_id,
                venue_id=cultural_partner.venueId,
                synchro=cultural_partner.synchroPass,
                active=cultural_partner.actif,
            )
        )

        if cultural_partner.venueId:
            venue_to_adage_id[cultural_partner.venueId] = adage_id

    deactivated = [row for row in adage_cps if not row.adage_id or row.synchro != 1 or row.active != 1]
    deactivated_adage_ids = {row.adage_id for row in deactivated}
    deactivated_venue_ids = {row.venue_id for row in deactivated if row.venue_id}

    deactivated_venues = (
        db.session.query(offerers_models.Venue)
        .filter(
            sa.or_(
                offerers_models.Venue.adageId.in_(deactivated_adage_ids),
                offerers_models.Venue.id.in_(deactivated_venue_ids),
            )
        )
        .all()
    )

    deactivated_venue_ids = {venue.id for venue in deactivated_venues}

    logger.info(
        "%d deactivated venues",
        len(deactivated_venue_ids),
        extra={"deactivated_venues": deactivated_venue_ids},
    )

    searched_ids = {cp.venue_id for cp in adage_cps} - deactivated_venue_ids
    searched_adage_ids = {cp.adage_id for cp in adage_cps} - deactivated_adage_ids
    venues = (
        db.session.query(offerers_models.Venue)
        .filter(
            sa.or_(
                offerers_models.Venue.adageId.in_(searched_adage_ids),
                offerers_models.Venue.id.in_(searched_ids),
            )
        )
        .all()
    )

    to_update_venue_ids = {venue.id for venue in venues}

    logger.info(
        "%d venues to update",
        len(to_update_venue_ids),
        extra={"to_update_venues": to_update_venue_ids},
    )

    adage_id_updates: dict[int, str] = {}

    with atomic():
        for venue in deactivated_venues:
            _remove_venue_adage_id(venue)
            db.session.add(venue)

        for venue in venues:
            # Update the users in SiB in case of previous adageId being none
            # This is because we track if the user has an adageId, not the value of the adageId
            if not venue.adageId:
                emails = offerers_repository.get_emails_by_venue(venue)
                for email in emails:
                    update_external_pro(email)
                if venue.managingOfferer.isValidated:
                    send_eac_offerer_activation_email(venue, list(emails))

            new_adage_id = venue_to_adage_id.get(venue.id)
            if new_adage_id:
                if venue.adageId != new_adage_id:
                    adage_id_updates[venue.id] = new_adage_id

                    history_api.add_action(
                        history_models.ActionType.INFO_MODIFIED,
                        author=None,
                        venue=venue,
                        comment="Synchronisation ADAGE",
                        modified_info={"adageId": {"old_info": venue.adageId, "new_info": str(new_adage_id)}},
                    )
                venue.adageId = str(new_adage_id)
                venue.adageInscriptionDate = date_utils.get_naive_utc_now()
                db.session.add(venue)
            else:
                logger.warning(
                    "Venue %s is not present in Adage. We could add it to the partner with adage_id %s",
                    venue.id,
                    venue.adageId,
                    extra={"venue.id": venue.id, "adageId": venue.adageId},
                )

    log_extra = {str(venue_id): adage_id for venue_id, adage_id in adage_id_updates.items()}
    logger.info("%d adage ids updates", len(adage_id_updates), extra=log_extra)


def _remove_venue_adage_id(venue: offerers_models.Venue) -> None:
    if venue.adageId:
        history_api.add_action(
            history_models.ActionType.INFO_MODIFIED,
            author=None,
            venue=venue,
            comment="Synchronisation ADAGE",
            modified_info={"adageId": {"old_info": venue.adageId, "new_info": None}},
        )
    venue.adageId = None
    venue.adageInscriptionDate = None


def get_adage_educational_redactors_for_uai(uai: str, *, force_update: bool = False) -> list[dict[str, str]]:
    EDUCATIONAL_REDACTORS_CACHE_TIMEOUT = 60 * 60  # 1h in seconds
    educational_redactors_cache_key = f"api:adage_educational_redactor_for_uai:{uai}"

    def _get_adage_educational_redactors_for_uai(uai_code: str) -> str:
        adage_data = adage_client.get_adage_educational_redactor_from_uai(uai_code)
        return json.dumps(adage_data)

    educational_redactors_json = get_from_cache(
        key_template=educational_redactors_cache_key,
        retriever=partial(_get_adage_educational_redactors_for_uai, uai_code=uai),
        expire=EDUCATIONAL_REDACTORS_CACHE_TIMEOUT,
        return_type=str,
        force_update=force_update,
    )

    educational_redactors_json = typing.cast(str, educational_redactors_json)
    educational_redactors = json.loads(educational_redactors_json)
    return educational_redactors


def autocomplete_educational_redactor_for_uai(
    uai: str, candidate: str, use_email: bool = False
) -> list[dict[str, str]]:
    redactors = get_adage_educational_redactors_for_uai(uai=uai)
    unaccented_candidate = clean_accents(candidate).upper()
    result = []
    for redactor in redactors:
        if unaccented_candidate in f"{redactor['nom']} {redactor['prenom']}".upper():
            result.append(redactor)
            continue
        if unaccented_candidate in f"{redactor['prenom']} {redactor['nom']}".upper():
            result.append(redactor)
            continue
        if use_email and unaccented_candidate in redactor["mail"].upper():
            result.append(redactor)
            continue
    return result


def get_redactor_favorites_count(redactor_id: int) -> int:
    """
    Note: Non-eligible for search templates are ignored.
    """
    redactor = (
        db.session.query(models.EducationalRedactor)
        .filter_by(id=redactor_id)
        .options(
            sa_orm.joinedload(models.EducationalRedactor.favoriteCollectiveOfferTemplates)
            .load_only(
                models.CollectiveOfferTemplate.id,
                models.CollectiveOfferTemplate.venueId,
                models.CollectiveOfferTemplate.validation,
                models.CollectiveOfferTemplate.isActive,
            )
            .joinedload(models.CollectiveOfferTemplate.venue)
            .load_only(
                offerers_models.Venue.managingOffererId,
                offerers_models.Venue.isVirtual,
            )
            .joinedload(offerers_models.Venue.managingOfferer)
            .load_only(offerers_models.Offerer.isActive, offerers_models.Offerer.validationStatus)
        )
        .one()
    )

    favorite_offer_templates = [
        template for template in redactor.favoriteCollectiveOfferTemplates if template.is_eligible_for_search
    ]

    return len(favorite_offer_templates)
