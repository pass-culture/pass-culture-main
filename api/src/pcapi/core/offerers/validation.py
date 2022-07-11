import decimal

import sqlalchemy.orm as sqla_orm

import pcapi.core.finance.models as finance_models
from pcapi.models import feature
from pcapi.models.api_errors import ApiErrors
from pcapi.utils.human_ids import dehumanize

from . import models


MAX_LONGITUDE = 180
MAX_LATITUDE = 90

VENUE_BANNER_MAX_SIZE = 10_000_000


# FUTURE-NEW-BANK-DETAILS: remove when new bank details journey is complete
def check_existing_business_unit(business_unit_id: int, offerer: models.Offerer):  # type: ignore [no-untyped-def]
    business_unit = finance_models.BusinessUnit.query.filter_by(id=business_unit_id).one_or_none()
    if not business_unit:
        raise ApiErrors(errors={"businessUnitId": ["Ce point de facturation n'existe pas."]})

    if business_unit.siret[:9] != offerer.siren:
        raise ApiErrors(errors={"businessUnitId": ["Ce point de facturation n'est pas un choix valide pour ce lieu."]})


def validate_coordinates(raw_latitude, raw_longitude):  # type: ignore [no-untyped-def]
    api_errors = ApiErrors()

    if raw_latitude:
        _validate_latitude(api_errors, raw_latitude)

    if raw_longitude:
        _validate_longitude(api_errors, raw_longitude)

    if api_errors.errors:
        raise api_errors


# FUTURE-NEW-BANK-DETAILS: cleanup ifs when new bank details journey is complete
def check_venue_creation(data):  # type: ignore [no-untyped-def]
    offerer_id = dehumanize(data.get("managingOffererId"))
    if not offerer_id:
        raise ApiErrors(errors={"managingOffererId": ["Vous devez choisir une structure pour votre lieu."]})
    offerer = models.Offerer.query.filter(models.Offerer.id == offerer_id).one_or_none()
    if not offerer:
        raise ApiErrors(errors={"managingOffererId": ["La structure que vous avez choisie n'existe pas."]})

    if None in [
        data.get("audioDisabilityCompliant"),
        data.get("mentalDisabilityCompliant"),
        data.get("motorDisabilityCompliant"),
        data.get("visualDisabilityCompliant"),
    ]:
        raise ApiErrors(errors={"global": ["L'accessibilité du lieu doit être définie."]})
    if not feature.FeatureToggle.ENABLE_NEW_BANK_INFORMATIONS_CREATION.is_active():
        business_unit_id = data.get("businessUnitId")
        if business_unit_id:
            check_existing_business_unit(business_unit_id, offerer)


def check_venue_edition(modifications, venue):  # type: ignore [no-untyped-def]
    managing_offerer_id = modifications.get("managingOffererId")
    siret = modifications.get("siret")
    business_unit_id = modifications.get("businessUnitId")
    reimbursement_point_id = modifications.get("reimbursementPointId")

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
        venue_with_same_siret = models.Venue.query.filter_by(siret=siret).one_or_none()
        if venue_with_same_siret:
            raise ApiErrors(errors={"siret": ["Un lieu avec le même siret existe déjà"]})
    if not venue.isVirtual and None in venue_disability_compliance and None in modifications_disability_compliance:
        raise ApiErrors(errors={"global": ["L'accessibilité du lieu doit etre définie."]})

    if reimbursement_point_id:
        check_venue_can_be_linked_to_reimbursement_point(venue, reimbursement_point_id)
    elif business_unit_id:
        check_existing_business_unit(business_unit_id, offerer=venue.managingOfferer)


def _validate_longitude(api_errors, raw_longitude):  # type: ignore [no-untyped-def]
    try:
        longitude = decimal.Decimal(raw_longitude)
    except decimal.InvalidOperation:
        api_errors.add_error("longitude", "Format incorrect")
    else:
        if longitude > MAX_LONGITUDE or longitude < -MAX_LONGITUDE:
            api_errors.add_error("longitude", "La longitude doit être comprise entre -180.0 et +180.0")


def _validate_latitude(api_errors, raw_latitude):  # type: ignore [no-untyped-def]
    try:
        latitude = decimal.Decimal(raw_latitude)
    except decimal.InvalidOperation:
        api_errors.add_error("latitude", "Format incorrect")
    else:
        if latitude > MAX_LATITUDE or latitude < -MAX_LATITUDE:
            api_errors.add_error("latitude", "La latitude doit être comprise entre -90.0 et +90.0")


def check_venue_can_be_linked_to_pricing_point(venue: models.Venue, pricing_point_id: int) -> None:
    if venue.siret and venue.id != pricing_point_id:
        raise ApiErrors(
            errors={
                "pricingPointId": [
                    "Vous ne pouvez pas choisir un autre lieu pour le calcul du barème de remboursement de ce lieu."
                ]
            }
        )
    pricing_point = models.Venue.query.filter_by(id=pricing_point_id).one_or_none()
    if not pricing_point:
        raise ApiErrors(errors={"pricingPointId": ["Ce lieu n'existe pas."]})
    if not pricing_point.siret:
        raise ApiErrors(
            errors={
                "pricingPointId": [
                    "Ce lieu ne peut pas être utilisé comme base de calcul du barème de "
                    "remboursement, car il n'a pas de SIRET."
                ]
            }
        )
    if pricing_point.managingOffererId != venue.managingOffererId:
        raise ApiErrors(
            errors={
                "pricingPointId": [
                    f"Le SIRET {pricing_point.siret} ne peut pas être utilisé pour calculer"
                    f" le barème de remboursement de ce lieu."
                ]
            }
        )


def check_venue_can_be_linked_to_reimbursement_point(venue: models.Venue, reimbursement_point_id: int) -> None:
    reimbursement_point = (
        models.Venue.query.filter_by(id=reimbursement_point_id)
        .options(sqla_orm.joinedload(models.Venue.bankInformation))
        .one_or_none()
    )
    if not reimbursement_point:
        raise ApiErrors(errors={"reimbursementPointId": ["Ce lieu n'existe pas."]})
    error_with_name = f"Le lieu {reimbursement_point.name} ne peut pas être utilisé pour les remboursements."
    if not reimbursement_point.siret:
        raise ApiErrors(errors={"reimbursementPointId": [error_with_name]})
    error_with_siret = f"Le SIRET {reimbursement_point.siret} ne peut pas être utilisé pour les remboursements."
    if (
        not reimbursement_point.bankInformation
        or reimbursement_point.bankInformation.status != finance_models.BankInformationStatus.ACCEPTED
    ):
        raise ApiErrors(errors={"reimbursementPointId": [error_with_siret]})
    if reimbursement_point.managingOffererId != venue.managingOffererId:
        raise ApiErrors(errors={"reimbursementPointId": [error_with_siret]})
