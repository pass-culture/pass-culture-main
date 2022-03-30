import logging

from flask_login import current_user
from flask_login import login_required

from pcapi.core.educational import repository as collective_repository
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import collective_bookings_serialize
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


logger = logging.getLogger(__name__)


@private_api.route("/collective/bookings/pro", methods=["GET"])
@login_required
@spectree_serialize(response_model=collective_bookings_serialize.ListCollectiveBookingsResponseModel, api=blueprint.pro_private_schema)  # type: ignore
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
        __root__=collective_bookings_serialize.serialize_collective_bookings_page(
            page, per_page_limit, total_collective_bookings, collective_bookings_page
        )
    )
