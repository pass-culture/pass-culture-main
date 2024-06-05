from dataclasses import dataclass
from datetime import datetime
from functools import partial
import json
import logging
import typing

from pydantic.v1 import parse_obj_as
import sqlalchemy as sa

from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api import address as address_api
from pcapi.core.educational.api.venue import get_relative_venues_by_siret
from pcapi.core.mails.transactional import send_eac_offerer_activation_email
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offerers.repository import get_emails_by_venue
from pcapi.models import db
from pcapi.repository import atomic
from pcapi.routes.serialization import venues_serialize
from pcapi.utils.cache import get_from_cache
from pcapi.utils.clean_accents import clean_accents


logger = logging.getLogger(__name__)


def find_collective_bookings_for_adage(
    uai_code: str,
    year_id: str,
    redactor_email: str | None = None,
) -> list[educational_models.CollectiveBooking]:
    return educational_repository.find_collective_bookings_for_adage(
        uai_code=uai_code, year_id=year_id, redactor_email=redactor_email
    )


def get_cultural_partners(
    *, timestamp: int | None = None, force_update: bool = False
) -> venues_serialize.AdageCulturalPartners:
    CULTURAL_PARTNERS_CACHE_KEY = "api:adage_cultural_partner:cache"
    CULTURAL_PARTNERS_CACHE_TIMEOUT = 24 * 60 * 60  # 24h in seconds

    def _get_cultural_partners() -> str:
        adage_data = adage_client.get_cultural_partners()
        return json.dumps(adage_data)

    if not timestamp:
        cultural_partners_json = get_from_cache(
            key_template=CULTURAL_PARTNERS_CACHE_KEY,
            retriever=_get_cultural_partners,
            expire=CULTURAL_PARTNERS_CACHE_TIMEOUT,
            return_type=str,
            force_update=force_update,
        )
    else:
        adage_data = adage_client.get_cultural_partners(timestamp)
        cultural_partners_json = json.dumps(adage_data)

    cultural_partners_json = typing.cast(str, cultural_partners_json)
    cultural_partners = json.loads(cultural_partners_json)
    return parse_obj_as(venues_serialize.AdageCulturalPartners, {"partners": cultural_partners})


def get_cultural_partner(siret: str) -> venues_serialize.AdageCulturalPartnerResponseModel:
    return venues_serialize.AdageCulturalPartnerResponseModel.from_orm(adage_client.get_cultural_partner(siret))


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
        venue = offerers_repository.find_venue_by_siret(siret)
    return venue, relative


def get_venue_by_id_for_adage_iframe(
    venue_id: int, search_relative: bool
) -> tuple[offerers_models.Venue | None, list[int]]:
    relative = []
    venue = None
    if search_relative:
        venues = offerers_repository.find_relative_venue_by_id(venue_id, permanent_only=False)
        for candidate in venues:
            if candidate.id == venue_id:
                venue = candidate
            else:
                relative.append(candidate.id)
    else:
        venue = offerers_repository.find_venue_by_id(venue_id)
    return venue, relative


def synchronize_adage_ids_on_offerers(partners_from_adage: list[venues_serialize.AdageCulturalPartner]) -> None:
    adage_sirens: set[str] = {p.siret[:9] for p in partners_from_adage if (p.actif == 1 and p.siret)}
    existing_sirens: dict[str, bool] = dict(
        offerers_models.Offerer.query.filter(offerers_models.Offerer.siren != None).with_entities(
            offerers_models.Offerer.siren, offerers_models.Offerer.allowedOnAdage
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
        offerers_models.Offerer.query.join(offerers_models.Venue)
        .filter(
            offerers_models.Offerer.siren != None,
            offerers_models.Venue.adageId.is_not(None),
        )
        .with_entities(offerers_models.Offerer.siren, offerers_models.Offerer.allowedOnAdage)
    )
    sirens_to_delete = sirens_to_delete - set(existing_sirens_from_synchronized_venues)
    sirens_to_add = sirens_to_add | {k for k, v in existing_sirens_from_synchronized_venues.items() if not v}

    logger.info("SIRENs to add: %s", sirens_to_add)
    logger.info("SIRENs to delete: %s", sirens_to_delete)
    logger.info("existing SIRENs from synchronized venues: %s", existing_sirens_from_synchronized_venues)

    offerers_models.Offerer.query.filter(offerers_models.Offerer.siren.in_(list(sirens_to_add))).update(
        {offerers_models.Offerer.allowedOnAdage: True}, synchronize_session=False
    )
    offerers_models.Offerer.query.filter(offerers_models.Offerer.siren.in_(list(sirens_to_delete))).update(
        {offerers_models.Offerer.allowedOnAdage: False}, synchronize_session=False
    )


@dataclass
class CulturalPartner:
    adage_id: str
    venue_id: int | None
    synchro: int | None
    active: int | None


def synchronize_adage_ids_on_venues(debug: bool = False, timestamp: int | None = None) -> None:
    from pcapi.core.external.attributes.api import update_external_pro

    adage_cultural_partners = get_cultural_partners(force_update=True, timestamp=timestamp)

    adage_cps = []
    venue_to_adage_id = {}

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

    deactivated_venues: list[offerers_models.Venue] = offerers_models.Venue.query.filter(
        sa.or_(
            offerers_models.Venue.adageId.in_(deactivated_adage_ids),
            offerers_models.Venue.id.in_(deactivated_venue_ids),
        )
    )

    deactivated_venue_ids = {venue.id for venue in deactivated_venues}

    if debug:
        logger.info(
            "%d deactivated venues",
            len(deactivated_venue_ids),
            extra={"deactivated_venues": deactivated_venue_ids},
        )

    searched_ids = {cp.venue_id for cp in adage_cps} - deactivated_venue_ids
    searched_adage_ids = {cp.adage_id for cp in adage_cps} - deactivated_adage_ids
    venues: list[offerers_models.Venue] = (
        offerers_models.Venue.query.filter(
            sa.or_(
                offerers_models.Venue.adageId.in_(searched_adage_ids),
                offerers_models.Venue.id.in_(searched_ids),
            )
        )
        .options(sa.orm.joinedload(offerers_models.Venue.adage_addresses))
        .all()
    )

    to_update_venue_ids = {venue.id for venue in venues}

    if debug:
        logger.info(
            "%d venues to update",
            len(to_update_venue_ids),
            extra={"to_update_venues": to_update_venue_ids},
        )

    adage_id_updates = {}

    with atomic():
        for venue in deactivated_venues:
            _remove_venue_from_eac(venue)
            db.session.add(venue)

        for venue in venues:
            # Update the users in SiB in case of previous adageId being none
            # This is because we track if the user has an adageId, not the value of the adageId
            if not venue.adageId:
                emails = get_emails_by_venue(venue)
                for email in emails:
                    update_external_pro(email)
                if venue.managingOfferer.isValidated:
                    send_eac_offerer_activation_email(venue, list(emails))
                venue.adageInscriptionDate = datetime.utcnow()

            new_adage_id = venue_to_adage_id.get(venue.id)
            if new_adage_id:
                if venue.adageId != new_adage_id:
                    adage_id_updates[venue.id] = new_adage_id

                venue.adageId = str(new_adage_id)
                db.session.add(venue)
            else:
                logger.warning(
                    "Venue %s is not present in Adage. We could add it to the partner with adage_id %s",
                    venue.id,
                    venue.adageId,
                    extra={"venue.id": venue.id, "adageId": venue.adageId},
                )

        # filter adage_cps rows that are linked to an unexisting
        # venue. This can happen since the base data comes from an
        # external source (`adage_cultural_partners`). Also, ignore
        # deactivated venues.
        venue_ids = {venue.id for venue in venues}
        adage_venues_ids = {cp.adage_id: cp.venue_id for cp in adage_cps if cp.venue_id in venue_ids}
        address_api.upsert_venues_addresses(adage_venues_ids)

        # No need to filter non-existing venue ids:
        deactivated_adage_venues_ids: dict[str, int] = {cp.adage_id: cp.venue_id for cp in deactivated if cp.venue_id}
        unlink_count = address_api.unlink_deactivated_venue_addresses(deactivated_adage_venues_ids)

    if debug:
        logger.info("%d adage ids updates", len(adage_id_updates), extra=adage_id_updates)  # type: ignore
        logger.info("%d adage venue addresses updates", len(adage_venues_ids), extra=adage_venues_ids)
        logger.info("%d unknown adage venue addresses unlinked", unlink_count)


def _remove_venue_from_eac(venue: offerers_models.Venue) -> None:
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
        if unaccented_candidate in f'{redactor["nom"]} {redactor["prenom"]}'.upper():
            result.append(redactor)
            continue
        if unaccented_candidate in f'{redactor["prenom"]} {redactor["nom"]}'.upper():
            result.append(redactor)
            continue
        if use_email and unaccented_candidate in redactor["mail"].upper():
            result.append(redactor)
            continue
    return result
