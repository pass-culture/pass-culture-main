import logging

import pcapi.core.bookings.api as bookings_api
from pcapi.core.users.models import User
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v2.serialization.bookings import BookingResponse
from pcapi.routes.native.v2.serialization.bookings import BookingsResponse
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_route("/bookings", version="v2", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=BookingsResponse)
@authenticated_and_active_user_required
def get_bookings(user: User) -> BookingsResponse:
    individual_bookings = bookings_api.get_individual_bookings(user)
    ended_bookings, ongoing_bookings = bookings_api.classify_and_sort_bookings(individual_bookings)

    return BookingsResponse(
        ended_bookings=[BookingResponse.from_orm(booking) for booking in ended_bookings],
        ongoing_bookings=[BookingResponse.from_orm(booking) for booking in ongoing_bookings],
        hasBookingsAfter18=any(
            booking for booking in individual_bookings if bookings_api.is_booking_by_18_user(booking)
        ),
    )
