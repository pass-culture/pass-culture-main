import logging

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.exceptions as bookings_exceptions
from pcapi.core.bookings.models import Booking
from pcapi.core.external_bookings import exceptions as external_bookings_exceptions
from pcapi.core.offers.exceptions import StockDoesNotExist
from pcapi.core.offers.exceptions import UnexpectedCinemaProvider
from pcapi.core.offers.models import Stock
from pcapi.core.providers.exceptions import InactiveProvider
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1.serialization.bookings import BookOfferRequest
from pcapi.routes.native.v1.serialization.bookings import BookOfferResponse
from pcapi.routes.native.v1.serialization.bookings import BookingDisplayStatusRequest
from pcapi.routes.native.v1.serialization.bookings import BookingReponse
from pcapi.routes.native.v1.serialization.bookings import BookingsResponse
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint


logger = logging.getLogger(__name__)


@blueprint.native_route("/bookings", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=BookOfferResponse, on_error_statuses=[400], on_empty_status=204)
@authenticated_and_active_user_required
def book_offer(user: User, body: BookOfferRequest) -> None:
    stock = db.session.query(Stock).get(body.stock_id)
    if not stock:
        logger.info("Could not book offer: stock does not exist", extra={"stock_id": body.stock_id})
        raise ApiErrors({"stock": "stock introuvable"}, status_code=400)

    # No bookings, no problems
    return None


@blueprint.native_route("/bookings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=BookingsResponse)
@authenticated_and_active_user_required
def get_bookings(user: User) -> BookingsResponse:
    individual_bookings = bookings_api.get_individual_bookings(user)
    ended_bookings, ongoing_bookings = bookings_api.classify_and_sort_bookings(individual_bookings)

    return BookingsResponse(
        ended_bookings=[BookingReponse.from_orm(booking) for booking in ended_bookings],
        ongoing_bookings=[BookingReponse.from_orm(booking) for booking in ongoing_bookings],
        hasBookingsAfter18=any(
            booking for booking in individual_bookings if bookings_api.is_booking_by_18_user(booking)
        ),
    )


@blueprint.native_route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204, on_error_statuses=[400, 404])
@authenticated_and_active_user_required
def cancel_booking(user: User, booking_id: int) -> None:
    booking = db.session.query(Booking).filter(Booking.id == booking_id, Booking.userId == user.id).first_or_404()
    try:
        bookings_api.cancel_booking_by_beneficiary(user, booking)
    except bookings_exceptions.BookingIsCancelled:
        # Do not raise an error, to avoid showing an error in case double-click => double call
        # Booking is cancelled so a success status is ok
        return
    except bookings_exceptions.BookingIsAlreadyUsed:
        raise ApiErrors({"code": "ALREADY_USED", "message": "La réservation a déjà été utilisée."})
    except bookings_exceptions.CannotCancelConfirmedBooking:
        raise ApiErrors({"code": "CONFIRMED_BOOKING", "message": "La date limite d'annulation est dépassée."})
    except RuntimeError:
        logger.error("Unexpected call to cancel_booking_by_beneficiary with non-beneficiary user %s", user.id)
        raise ApiErrors()
    except UnexpectedCinemaProvider:
        raise ApiErrors({"external_booking": "L'annulation de réservation a échoué."})
    except InactiveProvider:
        raise ApiErrors({"external_booking": "L'annulation de réservation a échoué."})
    except external_bookings_exceptions.ExternalBookingException:
        raise ApiErrors(
            {"code": "FAILED_TO_CANCEL_EXTERNAL_BOOKING", "message": "L'annulation de réservation a échoué."}
        )


@blueprint.native_route("/bookings/<int:booking_id>/toggle_display", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204, on_error_statuses=[400])
@authenticated_and_active_user_required
def flag_booking_as_used(user: User, booking_id: int, body: BookingDisplayStatusRequest) -> None:
    booking = db.session.query(Booking).filter(Booking.userId == user.id, Booking.id == booking_id).first_or_404()
    booking.displayAsEnded = body.ended
    repository.save(booking)
