import logging
import math

from flask_login import current_user
from flask_login import login_required

from pcapi.core.educational import api as collective_api
from pcapi.core.educational import repository as collective_repository
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import collective_bookings_serialize
from pcapi.routes.serialization.bookings_serialize import UserHasBookingResponse
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from ..serialization.collective_bookings_serialize import serialize_collective_booking


logger = logging.getLogger(__name__)


@private_api.route("/collective/bookings/pro", methods=["GET"])
@login_required
@spectree_serialize(
    response_model=collective_bookings_serialize.ListCollectiveBookingsResponseModel,
    api=blueprint.pro_private_schema,
)
def get_collective_bookings_pro(
    query: collective_bookings_serialize.ListCollectiveBookingsQueryModel,
) -> collective_bookings_serialize.ListCollectiveBookingsResponseModel:
    per_page_limit = 1000
    page = query.page
    venue_id = query.venue_id
    event_date = query.event_date
    booking_status = query.booking_status_filter
    booking_period = None
    if query.booking_period_beginning_date and query.booking_period_ending_date:
        booking_period = (query.booking_period_beginning_date, query.booking_period_ending_date)

    total_collective_bookings, collective_bookings_page = collective_repository.find_collective_bookings_by_pro_user(
        user=current_user._get_current_object(),  # for tests to succeed, because current_user is actually a LocalProxy
        booking_period=booking_period,
        status_filter=booking_status,
        event_date=event_date,
        venue_id=venue_id,
        page=int(page),
        per_page_limit=per_page_limit,
    )

    return collective_bookings_serialize.ListCollectiveBookingsResponseModel(
        bookings_recap=[serialize_collective_booking(booking) for booking in collective_bookings_page],
        page=page,
        pages=int(math.ceil(total_collective_bookings / per_page_limit)),  # type: ignore [operator]
        total=total_collective_bookings,
    )


@blueprint.pro_private_api.route("/collective/bookings/csv", methods=["GET"])
@login_required
@spectree_serialize(
    json_format=False,
    response_headers={
        "Content-Type": "text/csv; charset=utf-8-sig;",
        "Content-Disposition": "attachment; filename=reservations_pass_culture.csv",
    },
)
def get_collective_bookings_csv(query: collective_bookings_serialize.ListCollectiveBookingsQueryModel) -> bytes:
    venue_id = query.venue_id
    event_date = query.event_date
    booking_period = None
    if query.booking_period_beginning_date and query.booking_period_ending_date:
        booking_period = (query.booking_period_beginning_date, query.booking_period_ending_date)
    booking_status = query.booking_status_filter

    bookings = collective_api.get_collective_booking_csv_report(
        user=current_user._get_current_object(),  # for tests to succeed, because current_user is actually a LocalProxy
        booking_period=booking_period,
        status_filter=booking_status,
        event_date=event_date,
        venue_id=venue_id,
    )

    return bookings.encode("utf-8-sig")


@blueprint.pro_private_api.route("/collective/bookings/pro/userHasBookings", methods=["GET"])
@login_required
@spectree_serialize(response_model=UserHasBookingResponse)
def get_user_has_collective_bookings() -> UserHasBookingResponse:
    user = current_user._get_current_object()
    return UserHasBookingResponse(hasBookings=collective_repository.user_has_bookings(user))
