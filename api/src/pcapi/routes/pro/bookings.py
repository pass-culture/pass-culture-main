from datetime import datetime
from typing import cast

from dateutil import parser
from flask_login import current_user
from flask_login import login_required

from pcapi.core.bookings.models import BookingExportType
import pcapi.core.bookings.repository as booking_repository
from pcapi.routes.serialization.bookings_recap_serialize import ListBookingsQueryModel
from pcapi.routes.serialization.bookings_recap_serialize import ListBookingsResponseModel
from pcapi.routes.serialization.bookings_recap_serialize import UserHasBookingResponse
from pcapi.routes.serialization.bookings_recap_serialize import _serialize_booking_recap
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@blueprint.pro_private_api.route("/bookings/pro", methods=["GET"])
@login_required
@spectree_serialize(response_model=ListBookingsResponseModel, api=blueprint.pro_private_schema)
def get_bookings_pro(query: ListBookingsQueryModel) -> ListBookingsResponseModel:
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
    offer_type = query.offer_type

    # FIXME: rewrite this route. The repository function should return
    # a bare SQLAlchemy query, and the route should handle the
    # serialization so that we can get rid of BookingsRecapPaginated
    # that is only used here.
    bookings_recap_paginated = booking_repository.find_by_pro_user(
        user=current_user._get_current_object(),  # for tests to succeed, because current_user is actually a LocalProxy
        booking_period=booking_period,
        status_filter=booking_status,
        event_date=event_date,
        venue_id=venue_id,
        offer_type=offer_type,
        page=int(page),
    )

    return ListBookingsResponseModel(
        bookingsRecap=[
            _serialize_booking_recap(booking_recap) for booking_recap in bookings_recap_paginated.bookings_recap
        ],
        page=bookings_recap_paginated.page,
        pages=bookings_recap_paginated.pages,
        total=bookings_recap_paginated.total,
    )


@blueprint.pro_private_api.route("/bookings/pro/userHasBookings", methods=["GET"])
@login_required
@spectree_serialize(response_model=UserHasBookingResponse, api=blueprint.pro_private_schema)
def get_user_has_bookings() -> UserHasBookingResponse:
    user = current_user._get_current_object()
    return UserHasBookingResponse(hasBookings=booking_repository.user_has_bookings(user))


@blueprint.pro_private_api.route("/bookings/csv", methods=["GET"])
@login_required
@spectree_serialize(
    json_format=False,
    response_headers={
        "Content-Type": "text/csv; charset=utf-8;",
        "Content-Disposition": "attachment; filename=reservations_pass_culture.csv",
    },
)
def get_bookings_csv(query: ListBookingsQueryModel) -> bytes:
    return _create_booking_export_file(query, BookingExportType.CSV)


@blueprint.pro_private_api.route("/bookings/excel", methods=["GET"])
@login_required
@spectree_serialize(
    json_format=False,
    response_headers={
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "Content-Disposition": "attachment; filename=reservations_pass_culture.xlsx",
    },
)
def get_bookings_excel(query: ListBookingsQueryModel) -> bytes:
    return _create_booking_export_file(query, BookingExportType.EXCEL)


def _create_booking_export_file(query: ListBookingsQueryModel, export_type: BookingExportType) -> bytes:
    venue_id = query.venue_id
    event_date = parser.parse(query.event_date) if query.event_date else None
    booking_period = None
    if query.booking_period_beginning_date and query.booking_period_ending_date:
        booking_period = (
            datetime.fromisoformat(query.booking_period_beginning_date).date(),
            datetime.fromisoformat(query.booking_period_ending_date).date(),
        )
    booking_status = query.booking_status_filter
    offer_type = query.offer_type

    export_data = booking_repository.get_export(
        user=current_user._get_current_object(),  # for tests to succeed, because current_user is actually a LocalProxy
        booking_period=booking_period,
        status_filter=booking_status,
        event_date=event_date,
        venue_id=venue_id,
        offer_type=offer_type,
        export_type=export_type,
    )

    if export_type == BookingExportType.CSV:
        return cast(str, export_data).encode("utf-8-sig")
    return cast(bytes, export_data)
