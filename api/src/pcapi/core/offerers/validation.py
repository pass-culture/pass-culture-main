from decimal import Decimal
from decimal import InvalidOperation

from pcapi.core.finance.models import BusinessUnit
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.models.api_errors import ApiErrors
from pcapi.utils.human_ids import dehumanize


MAX_LONGITUDE = 180
MAX_LATITUDE = 90

VENUE_BANNER_MAX_SIZE = 10_000_000


def check_existing_business_unit(business_unit_id: int, offerer: Offerer):
    business_unit = BusinessUnit.query.filter_by(id=business_unit_id).one_or_none()
    if not business_unit:
        raise ApiErrors(errors={"businessUnitId": ["Ce point de facturation n'existe pas."]})

    if business_unit.siret[:9] != offerer.siren:
        raise ApiErrors(errors={"businessUnitId": ["Ce point de facturation n'est pas un choix valide pour ce lieu."]})


def validate_coordinates(raw_latitude, raw_longitude):
    api_errors = ApiErrors()

    if raw_latitude:
        _validate_latitude(api_errors, raw_latitude)

    if raw_longitude:
        _validate_longitude(api_errors, raw_longitude)

    if api_errors.errors:
        raise api_errors


def check_venue_creation(data):
    offerer_id = dehumanize(data.get("managingOffererId"))
    if not offerer_id:
        raise ApiErrors(errors={"managingOffererId": ["Vous devez choisir une structure pour votre lieu."]})
    offerer = Offerer.query.filter(Offerer.id == offerer_id).one_or_none()
    if not offerer:
        raise ApiErrors(errors={"managingOffererId": ["La structure que vous avez choisie n'existe pas."]})

    if None in [
        data.get("audioDisabilityCompliant"),
        data.get("mentalDisabilityCompliant"),
        data.get("motorDisabilityCompliant"),
        data.get("visualDisabilityCompliant"),
    ]:
        raise ApiErrors(errors={"global": ["L'accessibilité du lieu doit être définie."]})

    business_unit_id = data.get("businessUnitId")
    if business_unit_id:
        check_existing_business_unit(business_unit_id, offerer)


def check_venue_edition(modifications, venue):
    managing_offerer_id = modifications.get("managingOffererId")
    siret = modifications.get("siret")
    business_unit_id = modifications.get("businessUnitId")

    venue_disability_compliance = [
        venue.audioDisabilityCompliant,
        venue.mentalDisabilityCompliant,
        venue.motorDisabilityCompliant,
        venue.visualDisabilityCompliant,
    ]
    modifications_disability_compliance = [
        modifications.get("audioDisabilityCompliant"),
        modifications.get("mentalDisabilityCompliant"),
        modifications.get("motorDisabilityCompliant"),
        modifications.get("visualDisabilityCompliant"),
    ]

    if managing_offerer_id:
        raise ApiErrors(errors={"managingOffererId": ["Vous ne pouvez pas changer la structure d'un lieu"]})
    if siret and venue.siret and siret != venue.siret:
        raise ApiErrors(errors={"siret": ["Vous ne pouvez pas modifier le siret d'un lieu"]})
    if siret:
        venue_with_same_siret = Venue.query.filter_by(siret=siret).one_or_none()
        if venue_with_same_siret:
            raise ApiErrors(errors={"siret": ["Un lieu avec le même siret existe déjà"]})
    if not venue.isVirtual and None in venue_disability_compliance and None in modifications_disability_compliance:
        raise ApiErrors(errors={"global": ["L'accessibilité du lieu doit etre définie."]})

    if business_unit_id:
        check_existing_business_unit(business_unit_id, offerer=venue.managingOfferer)


def _validate_longitude(api_errors, raw_longitude):
    try:
        longitude = Decimal(raw_longitude)
    except InvalidOperation:
        api_errors.add_error("longitude", "Format incorrect")
    else:
        if longitude > MAX_LONGITUDE or longitude < -MAX_LONGITUDE:
            api_errors.add_error("longitude", "La longitude doit être comprise entre -180.0 et +180.0")


def _validate_latitude(api_errors, raw_latitude):
    try:
        latitude = Decimal(raw_latitude)
    except InvalidOperation:
        api_errors.add_error("latitude", "Format incorrect")
    else:
        if latitude > MAX_LATITUDE or latitude < -MAX_LATITUDE:
            api_errors.add_error("latitude", "La latitude doit être comprise entre -90.0 et +90.0")
