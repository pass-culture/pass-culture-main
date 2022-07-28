from datetime import datetime
import logging
import math
from typing import cast

from dateutil import parser
from flask_login import current_user
from flask_login import login_required

from pcapi.core.bookings.models import BookingExportType
from pcapi.core.educational import api as collective_api
from pcapi.core.educational import repository as collective_repository
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.apis import private_api
from pcapi.routes.serialization import collective_bookings_serialize
from pcapi.routes.serialization.bookings_serialize import UserHasBookingResponse
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize_or_raise
from pcapi.utils.rest import check_user_has_access_to_offerer

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
    event_date = parser.parse(query.event_date) if query.event_date else None
    booking_status = query.booking_status_filter
    booking_period = None
    if query.booking_period_beginning_date and query.booking_period_ending_date:
        booking_period = (
            datetime.fromisoformat(query.booking_period_beginning_date).date(),
            datetime.fromisoformat(query.booking_period_ending_date).date(),
        )
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
        bookingsRecap=[serialize_collective_booking(booking) for booking in collective_bookings_page],
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
        "Content-Disposition": "attachment; filename=reservations_eac_pass_culture.csv",
    },
)
def get_collective_bookings_csv(
    query: collective_bookings_serialize.ListCollectiveBookingsQueryModel,
) -> str | bytes:
    return _create_collective_bookings_export_file(query, BookingExportType.CSV)


@blueprint.pro_private_api.route("/collective/bookings/excel", methods=["GET"])
@login_required
@spectree_serialize(
    json_format=False,
    response_headers={
        "Content-Type": "application/vnd.ms-excel",
        "Content-Disposition": "attachment; filename=reservations_eac_pass_culture.xlsx",
    },
)
def get_collective_bookings_excel(
    query: collective_bookings_serialize.ListCollectiveBookingsQueryModel,
) -> str | bytes:
    return _create_collective_bookings_export_file(query, BookingExportType.EXCEL)


def _create_collective_bookings_export_file(
    query: collective_bookings_serialize.ListCollectiveBookingsQueryModel, export_type: BookingExportType
) -> str | bytes:
    venue_id = query.venue_id
    event_date = parser.parse(query.event_date) if query.event_date else None
    booking_period = None
    if query.booking_period_beginning_date and query.booking_period_ending_date:
        booking_period = (
            datetime.fromisoformat(query.booking_period_beginning_date).date(),
            datetime.fromisoformat(query.booking_period_ending_date).date(),
        )
    booking_status = query.booking_status_filter

    export_data = collective_api.get_collective_booking_report(
        user=current_user._get_current_object(),  # for tests to succeed, because current_user is actually a LocalProxy
        booking_period=booking_period,
        status_filter=booking_status,
        event_date=event_date,
        venue_id=venue_id,
        export_type=export_type,
    )

    if export_type == BookingExportType.CSV:
        return cast(str, export_data).encode("utf-8-sig")
    return cast(bytes, export_data)


@blueprint.pro_private_api.route("/collective/bookings/pro/userHasBookings", methods=["GET"])
@login_required
@spectree_serialize(response_model=UserHasBookingResponse)
def get_user_has_collective_bookings() -> UserHasBookingResponse:
    user = current_user._get_current_object()
    return UserHasBookingResponse(hasBookings=collective_repository.user_has_bookings(user))


@private_api.route("/collective/offers/<offer_id>/cancel_booking", methods=["PATCH"])
@login_required
@spectree_serialize(
    on_success_status=204,
    on_error_statuses=[400, 403, 404],
    api=blueprint.pro_private_schema,
)
def cancel_collective_offer_booking(offer_id: str) -> None:

    dehumanized_offer_id = dehumanize_or_raise(offer_id)

    try:
        offerer = offerers_api.get_offerer_by_collective_offer_id(dehumanized_offer_id)
    except offerers_exceptions.CannotFindOffererForOfferId:
        raise ApiErrors(
            {"code": "NO_EDUCATIONAL_OFFER_FOUND", "message": "No educational offer has been found with this id"}, 404
        )
    else:
        check_user_has_access_to_offerer(current_user, offerer.id)

    try:
        offers_api.cancel_collective_offer_booking(dehumanized_offer_id)
    except offers_exceptions.StockNotFound:
        raise ApiErrors(
            {"code": "NO_ACTIVE_STOCK_FOUND", "message": "No active stock has been found with this id"}, 404
        )
    except offers_exceptions.NoBookingToCancel:
        raise ApiErrors({"code": "NO_BOOKING", "message": "This educational offer has no booking to cancel"}, 400)
    return
