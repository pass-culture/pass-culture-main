import logging

import pcapi.core.bookings.api as bookings_api
from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v2.serialization.bookings import BookingListItemResponse
from pcapi.routes.native.v2.serialization.bookings import BookingResponse
from pcapi.routes.native.v2.serialization.bookings import BookingsListResponseV2
from pcapi.routes.native.v2.serialization.bookings import BookingsResponseV2
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_route("/bookings", version="v2", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=BookingsResponseV2)
@authenticated_and_active_user_required
def get_bookings(user: User) -> BookingsResponseV2:
    individual_bookings = bookings_api.get_individual_bookings(user)
    ended_bookings, ongoing_bookings = bookings_api.classify_and_sort_bookings(individual_bookings)

    return BookingsResponseV2(
        ended_bookings=[BookingResponse.from_orm(booking) for booking in ended_bookings],
        ongoing_bookings=[BookingResponse.from_orm(booking) for booking in ongoing_bookings],
        has_bookings_after_18=any(
            booking for booking in individual_bookings if bookings_api.is_booking_by_18_user(booking)
        ),
    )


@blueprint.native_route("/bookings/<string:status>", version="v2", methods=["GET"])
@spectree_serialize(on_success_status=200, api=blueprint.api, response_model=BookingsListResponseV2)
@authenticated_and_active_user_required
def get_bookings_list(user: User, status: str) -> BookingsListResponseV2:
    VALID_BOOKING_STATUS = {"ongoing", "ended"}

    if status not in VALID_BOOKING_STATUS:
        raise ApiErrors(
            {"status": f"Statut invalide '{status}'. Les statuts valides sont : 'ongoing' ou 'ended'."}, status_code=422
        )

    individual_bookings_list = bookings_api.get_individual_bookings_by_status(user, status)

    return BookingsListResponseV2(
        bookings=[BookingListItemResponse.from_orm(booking) for booking in individual_bookings_list]
    )
