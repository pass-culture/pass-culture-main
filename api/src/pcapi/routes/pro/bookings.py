from datetime import datetime
from typing import cast

from dateutil import parser
from flask import request
from flask_login import current_user
from flask_login import login_required

import pcapi.core.bookings.api as bookings_api
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingExportType
import pcapi.core.bookings.repository as booking_repository
import pcapi.core.bookings.validation as bookings_validation
from pcapi.routes.serialization import serialize
from pcapi.routes.serialization.bookings_recap_serialize import ListBookingsQueryModel
from pcapi.routes.serialization.bookings_recap_serialize import ListBookingsResponseModel
from pcapi.routes.serialization.bookings_recap_serialize import PatchBookingByTokenQueryModel
from pcapi.routes.serialization.bookings_recap_serialize import _serialize_booking_recap
from pcapi.routes.serialization.bookings_serialize import LegacyBookingResponse
from pcapi.routes.serialization.bookings_serialize import UserHasBookingResponse
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize
from pcapi.utils.rest import check_user_has_access_to_offerer
from pcapi.validation.routes.bookings import check_email_and_offer_id_for_anonymous_user
from pcapi.validation.routes.users_authentifications import check_user_is_logged_in_or_email_is_provided
from pcapi.validation.routes.users_authorizations import check_user_can_validate_bookings

from . import blueprint


BASE_CODE_DESCRIPTIONS = {
    "HTTP_401": (None, "Authentification nécessaire"),
    "HTTP_403": (None, "Vous n'avez pas les droits nécessaires pour voir cette contremarque"),
    "HTTP_404": (None, "La contremarque n'existe pas"),
    "HTTP_410": (None, "La contremarque n'est plus valide car elle a déjà été validée ou a été annulée"),
}

# TODO (gvanneste, 2021-10-19) : retravailler cette fonction, notamment check_user_is_logged_in_or_email_is_provided
# À brûler : juste checker si le user a droit de récupérer les bookings
@blueprint.pro_public_api_v1.route("/bookings/token/<token>", methods=["GET"])
@spectree_serialize(
    response_model=LegacyBookingResponse,
    on_success_status=200,
    on_empty_status=204,
)
def get_booking_by_token(token: str) -> LegacyBookingResponse | None:
    email: str | None = request.args.get("email", None)
    offer_id = dehumanize(request.args.get("offer_id", None))

    check_user_is_logged_in_or_email_is_provided(current_user, email)

    booking = booking_repository.find_by(token, email, offer_id)

    bookings_validation.check_is_usable(booking)

    if check_user_can_validate_bookings(current_user, booking.offererId):
        response = _create_response_to_get_booking_by_token(booking)
        return LegacyBookingResponse(**response)

    return None


@blueprint.pro_public_api_v1.route("/bookings/token/<token>", methods=["PATCH"])
@spectree_serialize(on_success_status=204)
def patch_booking_by_token(token: str, query: PatchBookingByTokenQueryModel) -> None:
    email = query.email
    offer_id = dehumanize(query.offer_id)
    booking = booking_repository.find_by(token, email, offer_id)

    if current_user.is_authenticated:
        check_user_has_access_to_offerer(current_user, booking.offererId)
    else:
        check_email_and_offer_id_for_anonymous_user(email, offer_id)

    bookings_api.mark_as_used(booking)


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
@spectree_serialize(response_model=UserHasBookingResponse)
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
        "Content-Type": "application/vnd.ms-excel",
        "Content-Disposition": "attachment; filename=reservations_pass_culture.xlsx",
    },
)
def get_bookings_excel(query: ListBookingsQueryModel) -> bytes:
    return _create_booking_export_file(query, BookingExportType.EXCEL)


def _create_response_to_get_booking_by_token(booking: Booking) -> dict:
    offer_name = booking.stock.offer.product.name
    date = None
    offer = booking.stock.offer
    is_event = offer.isEvent
    if is_event:
        date = serialize(booking.stock.beginningDatetime)
    venue_departement_code = offer.venue.departementCode
    response = {
        "bookingId": humanize(booking.id),
        "date": date,
        "email": booking.email,
        "isUsed": booking.is_used_or_reimbursed,
        "offerName": offer_name,
        "userName": booking.userName,
        "venueDepartementCode": venue_departement_code,
    }

    return response


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
