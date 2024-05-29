import logging

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.exceptions as bookings_exceptions
from pcapi.core.bookings.models import Booking
from pcapi.core.external_bookings import exceptions as external_bookings_exceptions
import pcapi.core.finance.models as finance_models
from pcapi.core.offers.exceptions import StockDoesNotExist
from pcapi.core.offers.exceptions import UnexpectedCinemaProvider
from pcapi.core.offers.models import Stock
from pcapi.core.providers.exceptions import InactiveProvider
from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.v1.serialization.bookings import BookOfferRequest
from pcapi.routes.native.v1.serialization.bookings import BookOfferResponse
from pcapi.routes.native.v1.serialization.bookings import BookingDisplayStatusRequest
from pcapi.routes.native.v1.serialization.bookings import BookingReponse
from pcapi.routes.native.v1.serialization.bookings import BookingsResponse
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)

from .. import blueprint


@blueprint.native_route("/bookings", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=BookOfferResponse, on_error_statuses=[400])
@authenticated_and_active_user_required
def book_offer(user: User, body: BookOfferRequest) -> BookOfferResponse:
    stock = Stock.query.filter_by(id=body.stock_id).one_or_none()
    if not stock:
        logger.info("Could not book offer: stock does not exist", extra={"stock_id": body.stock_id})
        raise ApiErrors({"stock": "stock introuvable"}, status_code=400)

    try:
        booking = bookings_api.book_offer(
            beneficiary=user,
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
            extra={"stock_id": body.stock_id, "subcategory_id": stock.offer.subcategoryId, "user_roles": user.roles},
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
    except external_bookings_exceptions.ExternalBookingException as error:
        if stock.offer.lastProvider.hasProviderEnableCharlie:
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
    except external_bookings_exceptions.ExternalBookingSoldOutError:
        raise ApiErrors({"code": "PROVIDER_STOCK_SOLD_OUT"})
    except external_bookings_exceptions.ExternalBookingNotEnoughSeatsError:
        raise ApiErrors({"code": "PROVIDER_STOCK_NOT_ENOUGH_SEATS"})
    return BookOfferResponse(bookingId=booking.id)


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
            booking
            for booking in individual_bookings
            if not booking.deposit or booking.deposit.type == finance_models.DepositType.GRANT_18
        ),
    )


@blueprint.native_route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204, on_error_statuses=[400, 404])
@authenticated_and_active_user_required
def cancel_booking(user: User, booking_id: int) -> None:
    booking = Booking.query.filter(Booking.id == booking_id, Booking.userId == user.id).first_or_404()
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
    booking = Booking.query.filter(Booking.userId == user.id, Booking.id == booking_id).first_or_404()
    booking.displayAsEnded = body.ended
    repository.save(booking)
