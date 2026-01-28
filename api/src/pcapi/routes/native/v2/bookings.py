import logging

from flask_login import current_user
from werkzeug.exceptions import NotFound

import pcapi.core.bookings.api as bookings_api
from pcapi.core.bookings import models as bookings_models
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v2.serialization.bookings import BookingListItemResponse
from pcapi.routes.native.v2.serialization.bookings import BookingResponse
from pcapi.routes.native.v2.serialization.bookings import BookingsListResponseV2
from pcapi.routes.native.v2.serialization.bookings import BookingsResponseV2
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from .. import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_route("/bookings/<int:booking_id>", version="v2", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=BookingResponse, on_error_statuses=[404])
@authenticated_and_active_user_required
@atomic()
def get_booking(booking_id: int) -> BookingResponse:
    booking = bookings_api.get_booking_by_id(current_user, booking_id)
    if booking is None:
        raise ResourceNotFoundError()
    return BookingResponse.from_orm(booking)


@blueprint.native_route("/bookings", version="v2", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=BookingsResponseV2)
@authenticated_and_active_user_required
def get_bookings() -> BookingsResponseV2:
    individual_bookings = bookings_api.get_individual_bookings(current_user)
    ended_bookings, ongoing_bookings = bookings_api.classify_and_sort_bookings(individual_bookings)

    return BookingsResponseV2(
        ended_bookings=[BookingResponse.from_orm(booking) for booking in ended_bookings],
        ongoing_bookings=[BookingResponse.from_orm(booking) for booking in ongoing_bookings],
        has_bookings_after_18=any(
            booking for booking in individual_bookings if bookings_api.is_booking_by_18_user(booking)
        ),
    )


@blueprint.native_route("/bookings/<string:status>", version="v2", methods=["GET"])
@spectree_serialize(
    response_model=BookingsListResponseV2, on_success_status=200, api=blueprint.api, on_error_statuses=[404]
)
@authenticated_and_active_user_required
def get_bookings_list(status: str) -> BookingsListResponseV2:
    try:
        bookings_models.BookingsListStatus(status)
    except ValueError:
        raise NotFound()

    bookings_list = bookings_api.get_user_bookings_by_status(current_user, status)

    return BookingsListResponseV2(bookings=[BookingListItemResponse.from_orm(booking) for booking in bookings_list])
