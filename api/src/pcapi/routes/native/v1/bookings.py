import logging

from flask_login import current_user

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.exceptions as bookings_exceptions
from pcapi.core.bookings.models import Booking
from pcapi.core.external_bookings import exceptions as external_bookings_exceptions
from pcapi.core.offers.exceptions import StockDoesNotExist
from pcapi.core.offers.exceptions import UnexpectedCinemaProvider
from pcapi.core.offers.models import Stock
from pcapi.core.providers.exceptions import InactiveProvider
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.utils import first_or_404
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
@spectree_serialize(api=blueprint.api, response_model=BookOfferResponse, on_error_statuses=[400])
@authenticated_and_active_user_required
def book_offer(body: BookOfferRequest) -> BookOfferResponse:
    stock = db.session.get(Stock, body.stock_id)
    if not stock:
        logger.info("Could not book offer: stock does not exist", extra={"stock_id": body.stock_id})
        raise ApiErrors({"stock": "stock introuvable"}, status_code=400)

    try:
        booking = bookings_api.book_offer(
            beneficiary=current_user,
            stock_id=body.stock_id,
            quantity=body.quantity,
        )

    except StockDoesNotExist:
        logger.info("Could not book offer: stock does not exist", extra={"stock_id": body.stock_id})
        raise ApiErrors({"stock": "stock introuvable"}, status_code=400)

    except (
        bookings_exceptions.UserHasInsufficientFunds,
        bookings_exceptions.DigitalExpenseLimitHasBeenReached,
        bookings_exceptions.PhysicalExpenseLimitHasBeenReached,
    ):
        logger.info("Could not book offer: insufficient credit", extra={"stock_id": body.stock_id})
        raise ApiErrors({"code": "INSUFFICIENT_CREDIT"})

    except bookings_exceptions.OfferIsAlreadyBooked:
        logger.info("Could not book offer: offer already booked", extra={"stock_id": body.stock_id})
        raise ApiErrors({"code": "ALREADY_BOOKED"})

    except bookings_exceptions.StockIsNotBookable:
        logger.info("Could not book offer: stock is not bookable", extra={"stock_id": body.stock_id})
        raise ApiErrors({"code": "STOCK_NOT_BOOKABLE"})

    except bookings_exceptions.OfferCategoryNotBookableByUser:
        logger.info(
            "Could not book offer: category is not bookable by user",
            extra={
                "stock_id": body.stock_id,
                "subcategory_id": stock.offer.subcategoryId,
                "user_roles": current_user.roles,
            },
        )
        raise ApiErrors({"code": "OFFER_CATEGORY_NOT_BOOKABLE_BY_USER"})
    except UnexpectedCinemaProvider:
        logger.info(
            "Could not book offer: The CinemaProvider for the Venue does not match the Offer Provider",
            extra={"offer_id": stock.offer.id, "venue_id": stock.offer.venue.id},
        )
        raise ApiErrors({"code": "CINEMA_PROVIDER_ERROR"})
    except InactiveProvider:
        logger.info(
            "Could not book offer: The CinemaProvider for this offer is inactive",
            extra={"offer_id": stock.offer.id, "provider_id": stock.offer.lastProviderId},
        )
        raise ApiErrors({"code": "CINEMA_PROVIDER_INACTIVE"})
    except external_bookings_exceptions.ExternalBookingTimeoutException:
        raise ApiErrors({"code": "PROVIDER_BOOKING_TIMEOUT"})
    except external_bookings_exceptions.ExternalBookingException as error:
        if stock.offer.lastProvider and stock.offer.lastProvider.hasTicketingService:
            logger.info(
                "Could not book offer: Error when booking external ticket. Message: %s",
                str(error),
                extra={"offer_id": stock.offer.id, "provider_id": stock.offer.lastProviderId},
            )
            raise ApiErrors({"code": "EXTERNAL_EVENT_PROVIDER_BOOKING_FAILED", "message": str(error)})
        logger.info(
            "Could not book offer: Error when booking external ticket",
            extra={"offer_id": stock.offer.id, "provider_id": stock.offer.lastProviderId},
        )
        raise ApiErrors({"code": "CINEMA_PROVIDER_BOOKING_FAILED"})
    except external_bookings_exceptions.ExternalBookingNotEnoughSeatsError:
        raise ApiErrors({"code": "PROVIDER_STOCK_NOT_ENOUGH_SEATS"})
    except external_bookings_exceptions.ExternalBookingShowDoesNotExistError:
        raise ApiErrors({"code": "PROVIDER_SHOW_DOES_NOT_EXIST"})
    return BookOfferResponse(bookingId=booking.id)


@blueprint.native_route("/bookings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=BookingsResponse)
@authenticated_and_active_user_required
def get_bookings() -> BookingsResponse:
    individual_bookings = bookings_api.get_individual_bookings(current_user)
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
def cancel_booking(booking_id: int) -> None:
    booking = first_or_404(
        db.session.query(Booking).filter(Booking.id == booking_id, Booking.userId == current_user.id)
    )
    try:
        bookings_api.cancel_booking_by_beneficiary(current_user, booking)
    except bookings_exceptions.BookingIsCancelled:
        # Do not raise an error, to avoid showing an error in case double-click => double call
        # Booking is cancelled so a success status is ok
        return
    except bookings_exceptions.BookingIsAlreadyUsed:
        raise ApiErrors({"code": "ALREADY_USED", "message": "La réservation a déjà été utilisée."})
    except bookings_exceptions.CannotCancelConfirmedBooking:
        raise ApiErrors({"code": "CONFIRMED_BOOKING", "message": "La date limite d'annulation est dépassée."})
    except RuntimeError:
        logger.error("Unexpected call to cancel_booking_by_beneficiary with non-beneficiary user %s", current_user.id)
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
def flag_booking_as_used(booking_id: int, body: BookingDisplayStatusRequest) -> None:
    booking = first_or_404(
        db.session.query(Booking).filter(Booking.userId == current_user.id, Booking.id == booking_id)
    )
    booking.displayAsEnded = body.ended
    db.session.add(booking)
    db.session.commit()
