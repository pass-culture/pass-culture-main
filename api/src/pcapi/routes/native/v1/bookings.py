from datetime import datetime
import logging

from sqlalchemy.orm import joinedload

import pcapi.core.bookings.api as bookings_api
from pcapi.core.bookings.constants import FREE_OFFER_SUBCATEGORIES_TO_ARCHIVE
import pcapi.core.bookings.exceptions as bookings_exceptions
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.external_bookings.exceptions import ExternalBookingException
import pcapi.core.finance.models as finance_models
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.exceptions import StockDoesNotExist
from pcapi.core.offers.exceptions import UnexpectedCinemaProvider
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import PriceCategory
from pcapi.core.offers.models import PriceCategoryLabel
from pcapi.core.offers.models import Product
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

from . import blueprint


@blueprint.native_v1.route("/bookings", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=BookOfferResponse, on_error_statuses=[400])
@authenticated_and_active_user_required
def book_offer(user: User, body: BookOfferRequest) -> BookOfferResponse:
    stock = Stock.query.get(body.stock_id)
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
        raise ApiErrors({"external_booking": "Cette offre n'est plus réservable."})
    except InactiveProvider:
        logger.info(
            "Could not book offer: The CinemaProvider for this offer is inactive",
            extra={"offer_id": stock.offer.id, "provider_id": stock.offer.lastProviderId},
        )
        raise ApiErrors({"external_booking": "Cette offre n'est plus réservable."})
    except ExternalBookingException:
        logger.info(
            "Could not book offer: Error when booking external ticket",
            extra={"offer_id": stock.offer.id, "provider_id": stock.offer.lastProviderId},
        )
        raise ApiErrors({"external_booking": "La réservation a échoué. Essaye un peu plus tard."})

    return BookOfferResponse(bookingId=booking.id)


@blueprint.native_v1.route("/bookings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=BookingsResponse)
@authenticated_and_active_user_required
def get_bookings(user: User) -> BookingsResponse:
    individual_bookings = (
        Booking.query.filter_by(userId=user.id)
        .options(joinedload(Booking.stock).load_only(Stock.id, Stock.beginningDatetime, Stock.price))
        .options(
            joinedload(Booking.stock)
            .joinedload(Stock.offer)
            .load_only(
                Offer.name,
                Offer.url,
                Offer.subcategoryId,
                Offer.withdrawalDetails,
                Offer.withdrawalType,
                Offer.withdrawalDelay,
                Offer.extraData,
            )
            .joinedload(Offer.product)
            .load_only(
                Product.id,
                Product.thumbCount,
            )
        )
        .options(
            joinedload(Booking.stock)
            .joinedload(Stock.priceCategory)
            .joinedload(PriceCategory.priceCategoryLabel)
            .load_only(PriceCategoryLabel.label)
        )
        .options(
            joinedload(Booking.stock)
            .joinedload(Stock.offer)
            .joinedload(Offer.venue)
            .load_only(
                Venue.name,
                Venue.address,
                Venue.postalCode,
                Venue.city,
                Venue.latitude,
                Venue.longitude,
                Venue.publicName,
            )
        )
        .options(joinedload(Booking.stock).joinedload(Stock.offer).joinedload(Offer.mediations))
        .options(joinedload(Booking.activationCode))
        .options(joinedload(Booking.externalBookings))
        .options(joinedload(Booking.deposit).load_only(finance_models.Deposit.type))
    ).all()

    has_bookings_after_18 = any(
        booking
        for booking in individual_bookings
        if not booking.deposit or booking.deposit.type == finance_models.DepositType.GRANT_18
    )
    ended_bookings = []
    ongoing_bookings = []

    for booking in individual_bookings:
        if is_ended_booking(booking):
            ended_bookings.append(booking)
        else:
            ongoing_bookings.append(booking)
            booking.qrCodeData = bookings_api.get_qr_code_data(booking.token)

    return BookingsResponse(
        ended_bookings=[
            BookingReponse.from_orm(booking)
            for booking in sorted(
                ended_bookings,
                key=lambda b: b.stock.beginningDatetime or b.dateUsed or b.cancellationDate or datetime.min,
                reverse=True,
            )
        ],
        # put permanent bookings at the end with datetime.max
        ongoing_bookings=[
            BookingReponse.from_orm(booking)
            for booking in sorted(
                ongoing_bookings, key=lambda b: (b.expirationDate or b.stock.beginningDatetime or datetime.max, -b.id)
            )
        ],
        hasBookingsAfter18=has_bookings_after_18,
    )


def is_ended_booking(booking: Booking) -> bool:
    if (
        booking.stock.beginningDatetime
        and booking.status != BookingStatus.CANCELLED
        and booking.stock.beginningDatetime >= datetime.utcnow()
    ):
        # consider future events as "ongoing" even if they are used
        return False

    if (booking.stock.canHaveActivationCodes and booking.activationCode) or (
        booking.stock.offer.subcategoryId in FREE_OFFER_SUBCATEGORIES_TO_ARCHIVE and booking.stock.price == 0
    ):
        # consider digital bookings and free offer from defined subcategories as special: is_used should be true anyway so
        # let's use displayAsEnded
        return booking.displayAsEnded  # type: ignore [return-value]

    return (
        not booking.stock.offer.isPermanent
        if booking.is_used_or_reimbursed
        else booking.status == BookingStatus.CANCELLED
    )


@blueprint.native_v1.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
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


@blueprint.native_v1.route("/bookings/<int:booking_id>/toggle_display", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204, on_error_statuses=[400])
@authenticated_and_active_user_required
def flag_booking_as_used(user: User, booking_id: int, body: BookingDisplayStatusRequest) -> None:
    booking = Booking.query.filter(Booking.userId == user.id, Booking.id == booking_id).first_or_404()
    booking.displayAsEnded = body.ended
    repository.save(booking)
