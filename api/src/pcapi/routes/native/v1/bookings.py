from datetime import datetime
import logging

from sqlalchemy.orm import joinedload

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.exceptions as bookings_exceptions
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.exceptions import StockDoesNotExist
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
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

    return BookOfferResponse(bookingId=booking.id)


@blueprint.native_v1.route("/bookings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=BookingsResponse)
@authenticated_and_active_user_required
def get_bookings(user: User) -> BookingsResponse:
    individual_bookings = (
        IndividualBooking.query.filter_by(userId=user.id)
        .options(
            joinedload(IndividualBooking.booking).joinedload(Booking.stock).load_only(Stock.id, Stock.beginningDatetime)
        )
        .options(
            joinedload(IndividualBooking.booking)
            .joinedload(Booking.stock)
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
            joinedload(IndividualBooking.booking)
            .joinedload(Booking.stock)
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
        .options(
            joinedload(IndividualBooking.booking)
            .joinedload(Booking.stock)
            .joinedload(Stock.offer)
            .joinedload(Offer.mediations)
        )
        .options(joinedload(IndividualBooking.booking).joinedload(Booking.activationCode))
        .options(joinedload(IndividualBooking.booking).joinedload(Booking.externalBookings))
    ).all()

    ended_bookings = []
    ongoing_bookings = []

    for individual_booking in individual_bookings:
        booking = individual_booking.booking
        if is_ended_booking(booking):
            ended_bookings.append(booking)
        else:
            ongoing_bookings.append(booking)
            booking.qrCodeData = bookings_api.get_qr_code_data(booking.token)
            booking.token = None if booking.isExternal else booking.token

    result = BookingsResponse(
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
    )
    _update_booking_offer_url(result.ended_bookings)
    _update_booking_offer_url(result.ongoing_bookings)

    # TODO: some objects seem to be updated. remove rollback when this is fixed
    db.session.rollback()
    return result


def _update_booking_offer_url(booking_response_list: list[BookingReponse]) -> None:
    # TODO: remove after all AppNative client use version >= 203
    # Native application should use `booking.completedUrl` but actually
    # it uses booking.stock.offer.url until versions < 203
    # So we need to update the response object not to override the database object
    # Remove when native app stops using booking.stock.offer.url
    for booking in booking_response_list:
        booking.stock.offer.url = booking.completedUrl


def is_ended_booking(booking: Booking) -> bool:
    if (
        booking.stock.beginningDatetime
        and booking.status != BookingStatus.CANCELLED
        and booking.stock.beginningDatetime >= datetime.utcnow()
    ):
        # consider future events events as "ongoing" even if they are used
        return False

    if booking.stock.canHaveActivationCodes and booking.activationCode:
        # consider digital bookings as special: is_used should be true anyway so
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
    booking = (
        Booking.query.join(IndividualBooking)
        .filter(Booking.id == booking_id, IndividualBooking.userId == user.id)
        .first_or_404()
    )
    try:
        bookings_api.cancel_booking_by_beneficiary(user, booking)
    except bookings_exceptions.BookingIsAlreadyUsed:
        raise ApiErrors({"code": "ALREADY_USED", "message": "La réservation a déjà été utilisée."})
    except bookings_exceptions.CannotCancelConfirmedBooking:
        raise ApiErrors({"code": "CONFIRMED_BOOKING", "message": "La date limite d'annulation est dépassée."})
    except RuntimeError:
        logger.error("Unexpected call to cancel_booking_by_beneficiary with non-beneficiary user %s", user.id)
        raise ApiErrors()


@blueprint.native_v1.route("/bookings/<int:booking_id>/toggle_display", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204, on_error_statuses=[400])
@authenticated_and_active_user_required
def flag_booking_as_used(user: User, booking_id: int, body: BookingDisplayStatusRequest) -> None:
    individual_booking = (
        IndividualBooking.query.join(IndividualBooking.booking)
        .filter(IndividualBooking.userId == user.id, Booking.id == booking_id)
        .first_or_404()
    )
    booking = individual_booking.booking
    booking.displayAsEnded = body.ended
    repository.save(booking)
