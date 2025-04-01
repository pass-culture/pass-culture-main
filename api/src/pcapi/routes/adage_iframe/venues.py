import logging

from pcapi.core.educational.api import adage as educational_api_adage
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import atomic
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.venues import GetRelativeVenuesQueryModel
from pcapi.routes.adage_iframe.serialization.venues import VenueResponse
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)


@blueprint.adage_iframe.route("/venues/siret/<siret>", methods=["GET"])
@atomic()
@spectree_serialize(api=blueprint.api, response_model=VenueResponse)
@adage_jwt_required
def get_venue_by_siret(
    authenticated_information: AuthenticatedInformation, siret: str, query: GetRelativeVenuesQueryModel
) -> VenueResponse:
    venue, relative = educational_api_adage.get_venue_by_siret_for_adage_iframe(
        siret=siret, search_relative=query.getRelative
    )
    if venue is None:
        logger.info("Venue does not exists for given siret", extra={"siret": siret})
        raise ApiErrors({"siret": "Aucun lieu n'existe pour ce siret"}, status_code=404)

    return VenueResponse.build(venue=venue, relative=relative)


@blueprint.adage_iframe.route("/venues/<int:venue_id>", methods=["GET"])
@atomic()
@spectree_serialize(api=blueprint.api, response_model=VenueResponse)
@adage_jwt_required
def get_venue_by_id(
    authenticated_information: AuthenticatedInformation, venue_id: int, query: GetRelativeVenuesQueryModel
) -> VenueResponse:
    venue, relative = educational_api_adage.get_venue_by_id_for_adage_iframe(
        venue_id=venue_id, search_relative=query.getRelative
    )

    if venue is None:
        logger.info("Venue does not exists for given venue_id", extra={"venue_id": venue_id})
        raise ApiErrors({"venue_id": "Aucun lieu n'existe pour ce venue_id"}, status_code=404)

    return VenueResponse.build(venue=venue, relative=relative)
