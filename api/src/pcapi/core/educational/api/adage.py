from datetime import datetime
from functools import partial
import json
import typing

from pydantic.v1 import parse_obj_as

from pcapi.core.educational import adage_backends as adage_client
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api import address as address_api
from pcapi.core.educational.api.venue import get_relative_venues_by_siret
from pcapi.core.mails.transactional import send_eac_offerer_activation_email
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offerers.repository import get_emails_by_venue
from pcapi.repository import atomic
from pcapi.routes.serialization import venues_serialize
from pcapi.utils.cache import get_from_cache
from pcapi.utils.clean_accents import clean_accents


def find_collective_bookings_for_adage(
    uai_code: str,
    year_id: str,
    redactor_email: str | None = None,
) -> list[educational_models.CollectiveBooking]:
    return educational_repository.find_collective_bookings_for_adage(
        uai_code=uai_code, year_id=year_id, redactor_email=redactor_email
    )


def get_cultural_partners(*, force_update: bool = False) -> venues_serialize.AdageCulturalPartners:
    CULTURAL_PARTNERS_CACHE_KEY = "api:adage_cultural_partner:cache"
    CULTURAL_PARTNERS_CACHE_TIMEOUT = 24 * 60 * 60  # 24h in seconds

    def _get_cultural_partners() -> str:
        adage_data = adage_client.get_cultural_partners()
        return json.dumps(adage_data)

    cultural_partners_json = get_from_cache(
        key_template=CULTURAL_PARTNERS_CACHE_KEY,
        retriever=_get_cultural_partners,
        expire=CULTURAL_PARTNERS_CACHE_TIMEOUT,
        return_type=str,
        force_update=force_update,
    )

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

    offerers_models.Offerer.query.filter(offerers_models.Offerer.siren.in_(list(sirens_to_add))).update(
        {offerers_models.Offerer.allowedOnAdage: True}, synchronize_session=False
    )
    offerers_models.Offerer.query.filter(offerers_models.Offerer.siren.in_(list(sirens_to_delete))).update(
        {offerers_models.Offerer.allowedOnAdage: False}, synchronize_session=False
    )


def synchronize_adage_ids_on_venues() -> None:
    from pcapi.core.external.attributes.api import update_external_pro

    adage_cultural_partners = get_cultural_partners(force_update=True)

    adage_ids_venues = {}  # adage ids as keys, venue ids as values
    filtered_cultural_partner_by_ids = {}  # venue ids as keys, response object as values

    for cultural_partner in adage_cultural_partners.partners:
        if cultural_partner.venueId is not None and (cultural_partner.synchroPass and cultural_partner.actif == 1):
            filtered_cultural_partner_by_ids[cultural_partner.venueId] = cultural_partner
            adage_ids_venues[str(cultural_partner.id)] = cultural_partner.venueId

    deactivated_venues: list[offerers_models.Venue] = (
        educational_repository.get_venue_base_query()
        .filter(
            offerers_models.Venue.id.not_in(filtered_cultural_partner_by_ids.keys()),
            offerers_models.Venue.adageId.is_not(None),
        )
        .all()
    )

    with atomic():
        for venue in deactivated_venues:
            _remove_venue_from_eac(venue)

        venues: list[offerers_models.Venue] = offerers_models.Venue.query.filter(
            offerers_models.Venue.id.in_(filtered_cultural_partner_by_ids.keys())
        ).all()

        for venue in venues:
            if not venue.adageId:
                # Update the users in SiB in case of previous adageId being none
                # This is because we track if the user has an adageId, not the value of the adageId
                emails = get_emails_by_venue(venue)
                for email in emails:
                    update_external_pro(email)
                if venue.managingOfferer.isValidated:
                    send_eac_offerer_activation_email(venue, list(emails))
                venue.adageInscriptionDate = datetime.utcnow()

            venue.adageId = str(filtered_cultural_partner_by_ids[venue.id].id)

        # filter adage_ids_venues rows that are linked to an unexisting
        # venue. This can happen since the base data comes from an
        # external source (`adage_cultural_partners`).
        venue_ids = {venue.id for venue in venues} | {venue.id for venue in deactivated_venues}
        adage_ids_venues = {
            adage_id: venue_id for adage_id, venue_id in adage_ids_venues.items() if venue_id in venue_ids
        }

        address_api.upsert_venues_addresses(adage_ids_venues)
        address_api.unlink_unknown_venue_addresses(adage_ids_venues.keys())


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
