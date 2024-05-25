from datetime import date
import math
from typing import cast

from flask_login import current_user
from flask_login import login_required

from pcapi.core.bookings import models as bookings_models
from pcapi.core.bookings.models import BookingExportType
import pcapi.core.bookings.repository as booking_repository
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users import repository as users_repository
from pcapi.models import api_errors
from pcapi.routes.serialization.bookings_recap_serialize import BookingsExportQueryModel
from pcapi.routes.serialization.bookings_recap_serialize import BookingsExportStatusFilter
from pcapi.routes.serialization.bookings_recap_serialize import EventDateScheduleAndPriceCategoriesCountModel
from pcapi.routes.serialization.bookings_recap_serialize import EventDatesInfos
from pcapi.routes.serialization.bookings_recap_serialize import ListBookingsQueryModel
from pcapi.routes.serialization.bookings_recap_serialize import ListBookingsResponseModel
from pcapi.routes.serialization.bookings_recap_serialize import UserHasBookingResponse
from pcapi.routes.serialization.bookings_recap_serialize import serialize_bookings
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@blueprint.pro_private_api.route("/bookings/pro", methods=["GET"])
@login_required
@spectree_serialize(response_model=ListBookingsResponseModel, api=blueprint.pro_private_schema)
def get_bookings_pro(query: ListBookingsQueryModel) -> ListBookingsResponseModel:
    page = query.page
    per_page_limit = 1000
    venue_id = query.venue_id
    offer_id = query.offer_id
    event_date = query.event_date
    booking_status = query.booking_status_filter
    booking_period = None
    if query.booking_period_beginning_date and query.booking_period_ending_date:
        booking_period = (
            query.booking_period_beginning_date,
            query.booking_period_ending_date,
        )
    offer_type = query.offer_type

    bookings_query, total = booking_repository.find_by_pro_user(
        user=current_user._get_current_object(),  # for tests to succeed, because current_user is actually a LocalProxy
        booking_period=booking_period,
        status_filter=booking_status,
        event_date=event_date,
        venue_id=venue_id,
        offer_id=offer_id,
        offer_type=offer_type,
        page=int(page),
        per_page_limit=per_page_limit,
    )

    return ListBookingsResponseModel(
        bookingsRecap=[serialize_bookings(booking) for booking in bookings_query],
        page=page,
        pages=int(math.ceil(total / per_page_limit)),
        total=total,
    )


@blueprint.pro_private_api.route("/bookings/pro/userHasBookings", methods=["GET"])
@login_required
@spectree_serialize(response_model=UserHasBookingResponse, api=blueprint.pro_private_schema)
def get_user_has_bookings() -> UserHasBookingResponse:
    user = current_user._get_current_object()
    return UserHasBookingResponse(hasBookings=booking_repository.user_has_bookings(user.id))


@blueprint.pro_private_api.route("/bookings/offer/<int:offer_id>/csv", methods=["GET"])
@login_required
@spectree_serialize(
    json_format=False,
    response_headers={
        "Content-Type": "text/csv; charset=utf-8;",
        "Content-Disposition": "attachment; filename=reservations_pass_culture.csv",
    },
    api=blueprint.pro_private_schema,
)
def export_bookings_for_offer_as_csv(offer_id: int, query: BookingsExportQueryModel) -> bytes:
    user = current_user._get_current_object()
    offer = Offer.query.get(int(offer_id))

    if not users_repository.has_access(user, offer.venue.managingOffererId):
        raise api_errors.ForbiddenError({"global": "You are not allowed to access this offer"})

    if query.status == BookingsExportStatusFilter.VALIDATED:
        return cast(
            str,
            booking_repository.export_validated_bookings_by_offer_id(
                offer_id, event_beginning_date=query.event_date, export_type=BookingExportType.CSV
            ),
        ).encode("utf-8-sig")
    return cast(
        str,
        booking_repository.export_bookings_by_offer_id(
            offer_id, event_beginning_date=query.event_date, export_type=BookingExportType.CSV
        ),
    ).encode("utf-8-sig")


@blueprint.pro_private_api.route("/bookings/offer/<int:offer_id>/excel", methods=["GET"])
@login_required
@spectree_serialize(
    json_format=False,
    response_headers={
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "Content-Disposition": "attachment; filename=reservations_pass_culture.xlsx",
    },
    api=blueprint.pro_private_schema,
)
def export_bookings_for_offer_as_excel(offer_id: int, query: BookingsExportQueryModel) -> bytes:
    user = current_user._get_current_object()
    offer = Offer.query.get(int(offer_id))

    if not users_repository.has_access(user, offer.venue.managingOffererId):
        raise api_errors.ForbiddenError({"global": "You are not allowed to access this offer"})

    if query.status == BookingsExportStatusFilter.VALIDATED:
        return cast(
            bytes,
            booking_repository.export_validated_bookings_by_offer_id(
                offer_id, event_beginning_date=query.event_date, export_type=BookingExportType.EXCEL
            ),
        )
    return cast(
        bytes,
        booking_repository.export_bookings_by_offer_id(
            offer_id, event_beginning_date=query.event_date, export_type=BookingExportType.EXCEL
        ),
    )


@blueprint.pro_private_api.route("/bookings/csv", methods=["GET"])
@login_required
@spectree_serialize(
    json_format=False,
    response_headers={
        "Content-Type": "text/csv; charset=utf-8;",
        "Content-Disposition": "attachment; filename=reservations_pass_culture.csv",
    },
    api=blueprint.pro_private_schema,
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
    api=blueprint.pro_private_schema,
)
def get_bookings_excel(query: ListBookingsQueryModel) -> bytes:
    return _create_booking_export_file(query, BookingExportType.EXCEL)


@blueprint.pro_private_api.route("/bookings/dates/<int:offer_id>", methods=["GET"])
@login_required
@spectree_serialize(response_model=EventDatesInfos, api=blueprint.pro_private_schema)
def get_offer_price_categories_and_schedules_by_dates(offer_id: int) -> EventDatesInfos:
    user = current_user._get_current_object()
    offer = Offer.query.get(offer_id)

    if not users_repository.has_access(user, offer.venue.managingOffererId):
        raise api_errors.ForbiddenError({"global": "You are not allowed to access this offer"})

    stocks = (
        Stock.query.join(bookings_models.Booking)
        .filter(
            Stock.offerId == offer_id,
            Stock.isSoftDeleted == False,
            Stock.beginningDatetime.isnot(None),
        )
        .order_by(Stock.beginningDatetime)
        .all()
    )
    stocks_by_date: dict[date, dict[str, list]] = {}

    for stock in stocks:
        if stock.beginningDatetime is None:
            continue
        stock_date = stock.beginningDatetime.date()
        stock_time = stock.beginningDatetime.time()
        stock_price_category = stock.priceCategoryId
        if stock_date not in stocks_by_date:
            stocks_by_date[stock_date] = {
                "price_categories": [stock.priceCategoryId],
                "schedules": [stock_time],
            }
        else:
            if stock_price_category not in stocks_by_date[stock_date]["price_categories"]:
                stocks_by_date[stock_date]["price_categories"].append(stock_price_category)
            if stock_time not in stocks_by_date[stock_date]["schedules"]:
                stocks_by_date[stock_date]["schedules"].append(stock_time)

    return EventDatesInfos(
        __root__=[
            EventDateScheduleAndPriceCategoriesCountModel(
                event_date=date,
                schedule_count=len(schedule_and_price_categories_count["schedules"]),
                price_categories_count=len(schedule_and_price_categories_count["price_categories"]),
            )
            for date, schedule_and_price_categories_count in stocks_by_date.items()
        ]
    )


def _create_booking_export_file(query: ListBookingsQueryModel, export_type: BookingExportType) -> bytes:
    venue_id = query.venue_id
    event_date = query.event_date
    booking_period = None
    if query.booking_period_beginning_date and query.booking_period_ending_date:
        booking_period = (
            query.booking_period_beginning_date,
            query.booking_period_ending_date,
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
