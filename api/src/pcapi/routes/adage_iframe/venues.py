import logging

from pcapi.core.offerers import repository as offerers_repository
from pcapi.models import ApiErrors
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.venues import VenueResponse
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)


@blueprint.adage_iframe.route("/venues/<siret>", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=VenueResponse)
@adage_jwt_required
def get_venue_by_siret(authenticated_information: AuthenticatedInformation, siret: str) -> VenueResponse:
    venue = offerers_repository.find_venue_by_siret(siret)

    if venue is None:
        logger.info("Venue does not exists for given siret", extra={"siret": siret})
        raise ApiErrors({"siret": "Aucun lieu n'existe pour ce siret"}, status_code=404)

    return VenueResponse.from_orm(venue)
