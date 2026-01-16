import typing

from pcapi.core.offerers import constants as offerers_constants
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors

from . import models


if typing.TYPE_CHECKING:
    from pcapi.routes.serialization import venues_serialize

VENUE_BANNER_MAX_SIZE = 10_000_000


def check_accessibility_compliance(venue: "venues_serialize.PostVenueBodyModel") -> None:
    if None in [
        venue.audioDisabilityCompliant,
        venue.mentalDisabilityCompliant,
        venue.motorDisabilityCompliant,
        venue.visualDisabilityCompliant,
    ]:
        raise ApiErrors(errors={"global": ["L'accessibilité du lieu doit être définie."]})


def check_siret_does_not_exists(siret: str) -> None:
    if offerers_repository.find_venue_by_siret(siret):
        raise ApiErrors(errors={"siret": "Un lieu avec ce SIRET existe déjà"})


def check_venue_edition(modifications: dict[str, typing.Any], venue: models.Venue) -> None:
    managing_offerer_id = modifications.get("managingOffererId")
    siret = modifications.get("siret")

    venue_disability_compliance = [
        venue.audioDisabilityCompliant,
        venue.mentalDisabilityCompliant,
        venue.motorDisabilityCompliant,
        venue.visualDisabilityCompliant,
    ]

    modifications_disability_compliance = [
        modifications.get("audioDisabilityCompliant", offerers_constants.UNCHANGED),
        modifications.get("mentalDisabilityCompliant", offerers_constants.UNCHANGED),
        modifications.get("motorDisabilityCompliant", offerers_constants.UNCHANGED),
        modifications.get("visualDisabilityCompliant", offerers_constants.UNCHANGED),
    ]

    if venue.isVirtual:
        raise ApiErrors(errors={"venue": ["Vous ne pouvez pas modifier un lieu Offre Numérique."]})

    if managing_offerer_id:
        raise ApiErrors(errors={"managingOffererId": ["Vous ne pouvez pas changer la structure d'un lieu"]})
    # modifications.get("siret") may be False if there is no change (ok) OR if it has been cleared (forbidden!)
    if "siret" in modifications and not siret and "comment" not in modifications:
        raise ApiErrors(errors={"siret": ["Vous ne pouvez pas supprimer le siret d'un lieu"]})
    if siret:
        venue_with_same_siret = db.session.query(models.Venue).filter_by(siret=siret).one_or_none()
        if venue_with_same_siret:
            raise ApiErrors(errors={"siret": ["Un lieu avec le même siret existe déjà"]})
        if not siret.startswith(venue.managingOfferer.siren):
            raise ApiErrors(
                errors={
                    "siret": [
                        f"Le code {venue.identifier_name} doit correspondre à un établissement de votre structure"
                    ]
                }
            )
    if "name" in modifications and modifications["name"] != venue.name and (siret is None or venue.siret == siret):
        raise ApiErrors(errors={"name": ["Vous ne pouvez pas modifier la raison sociale d'un lieu"]})
    if (
        not venue.isVirtual
        and None in venue_disability_compliance
        and None in modifications_disability_compliance
        and offerers_constants.UNCHANGED not in modifications_disability_compliance
    ):
        raise ApiErrors(errors={"global": ["L'accessibilité du lieu doit être définie."]})


def check_venue_can_be_linked_to_pricing_point(venue: models.Venue, pricing_point_id: int) -> None:
    if venue.siret and venue.id != pricing_point_id:
        raise ApiErrors(
            errors={
                "pricingPointId": [
                    "Ce partenaire culturel a un SIRET, vous ne pouvez donc pas choisir un autre partenaire culturel pour le calcul du barème de remboursement."
                ]
            }
        )

    pricing_point = db.session.query(models.Venue).filter_by(id=pricing_point_id).one_or_none()
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
                    f"le barème de remboursement de ce lieu, "
                    f"car il n'appartient pas à la même structure."
                ]
            }
        )


def check_activity_according_to_open_to_public(
    activity: offerers_models.ActivityOpenToPublic | offerers_models.ActivityNotOpenToPublic, is_open_to_public: bool
) -> None:
    if is_open_to_public:
        if activity.value not in offerers_models.ActivityOpenToPublic:
            raise ApiErrors(errors={"activity": ["Activité non reconnue."]})
    elif activity.value not in offerers_models.ActivityNotOpenToPublic:
        raise ApiErrors(errors={"activity": ["Activité non reconnue."]})
