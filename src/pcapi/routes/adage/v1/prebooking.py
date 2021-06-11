import logging

from pcapi.routes.adage.security import adage_api_key_required
from pcapi.routes.adage.v1.educational_institution import educational_institution_path
from pcapi.routes.adage.v1.serialization.prebooking import GetPreBookingsRequest
from pcapi.routes.adage.v1.serialization.prebooking import PreBookingResponse
from pcapi.routes.adage.v1.serialization.prebooking import PreBookingsResponse
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)

from . import blueprint


@blueprint.adage_v1.route(educational_institution_path + "/prebookings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=PreBookingsResponse, tags=("get prebookings",))
@adage_api_key_required
def get_pre_bookings(query: GetPreBookingsRequest) -> PreBookingsResponse:
    """Get a list of prebookings"""


@blueprint.adage_v1.route("/prebookings/<int:pre_booking_id>", methods=["GET"])
@spectree_serialize(
    api=blueprint.api, response_model=PreBookingResponse, on_error_statuses=[404], tags=("get prebookings",)
)
@adage_api_key_required
def get_pre_booking() -> PreBookingResponse:
    """Get details on a prebooking"""


@blueprint.adage_v1.route("/prebookings/<int:pre_booking_id>/confirm", methods=["POST"])
@spectree_serialize(
    api=blueprint.api, response_model=PreBookingResponse, on_error_statuses=[404, 422], tags=("change prebookings",)
)
@adage_api_key_required
def confirm_pre_booking() -> PreBookingResponse:
    """Confirm a prebooking

    Can only work if the prebooking is not confirmed yet."""


@blueprint.adage_v1.route("/prebookings/<int:pre_booking_id>/cancel_confirmation", methods=["POST"])
@spectree_serialize(
    api=blueprint.api, response_model=PreBookingResponse, on_error_statuses=[404, 422], tags=("change bookings",)
)
@adage_api_key_required
def cancel_pre_booking() -> PreBookingResponse:
    """Cancel a prebooking confirmation

    Can only work if prebooking has already been confirmed,
    is not yet used and still cancellable."""


@blueprint.adage_v1.route("/prebookings/<int:pre_booking_id>", methods=["DELETE"])
@spectree_serialize(
    api=blueprint.api, response_model=PreBookingResponse, on_error_statuses=[404, 422], tags=("change prebookings",)
)
@adage_api_key_required
def delete_pre_booking() -> PreBookingResponse:
    """Delete a prebooking

    Can only be used if prebooking is not confirmed yet."""
