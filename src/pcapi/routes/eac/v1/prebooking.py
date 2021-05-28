import logging

from pcapi.routes.eac.security import eac_api_key_required
from pcapi.routes.eac.v1.serialization.prebooking import GetPreBookingsRequest
from pcapi.routes.eac.v1.serialization.prebooking import PreBookingResponse
from pcapi.routes.eac.v1.serialization.prebooking import PreBookingsResponse
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)

from . import blueprint


@blueprint.eac_v1.route("/prebookings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=PreBookingsResponse)
@eac_api_key_required
def get_pre_bookings(query: GetPreBookingsRequest) -> PreBookingsResponse:
    pass


@blueprint.eac_v1.route("/prebookings/<int:pre_booking_id>", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=PreBookingResponse)
@eac_api_key_required
def get_pre_booking() -> PreBookingResponse:
    pass
