import logging

from pcapi.core.educational.api import deactivate_offerer_for_EAC
from pcapi.core.offerers.repository import find_offerer_by_siren
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.adage.security import adage_api_key_required
from pcapi.routes.adage.v1 import blueprint
from pcapi.routes.adage.v1.serialization import prebooking as prebooking_serialization
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)


@blueprint.adage_v1.route("cultural_partners/<string:siren>/deactivate", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=prebooking_serialization.EducationalBookingsResponse)
@adage_api_key_required
def deactivate_cultural_partner(siren: str) -> prebooking_serialization.EducationalBookingsResponse:
    offerer = find_offerer_by_siren(siren)
    if not offerer:
        raise ApiErrors(errors={"code": "OFFERER_NOT_FOUND"}, status_code=404)

    cancelled_bookings = deactivate_offerer_for_EAC(offerer)
    return prebooking_serialization.EducationalBookingsResponse(
        prebookings=prebooking_serialization.serialize_collective_bookings(cancelled_bookings)
    )
