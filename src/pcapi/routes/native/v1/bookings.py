from datetime import datetime
import logging

from sqlalchemy.orm import joinedload

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.exceptions as exceptions
from pcapi.core.bookings.models import Booking
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.exceptions import StockDoesNotExist
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.models.product import Product
from pcapi.routes.native.security import authenticated_user_required
from pcapi.routes.native.v1.serialization.bookings import BookOfferRequest
from pcapi.routes.native.v1.serialization.bookings import BookOfferResponse
from pcapi.routes.native.v1.serialization.bookings import BookingReponse
from pcapi.routes.native.v1.serialization.bookings import BookingsResponse
from pcapi.serialization.decorator import spectree_serialize


logger = logging.getLogger(__name__)

from . import blueprint


@blueprint.native_v1.route("/book_offer", methods=["POST"])  # TODO(viconnex): remove route when frontend uses /bookings
@blueprint.native_v1.route("/bookings", methods=["POST"])
@spectree_serialize(api=blueprint.api, response_model=BookOfferResponse, on_error_statuses=[400])
@authenticated_user_required
def book_offer(user: User, body: BookOfferRequest) -> BookOfferResponse:
    stock = Stock.query.get(body.stock_id)
    if not stock:
        raise ApiErrors({"stock": "stock introuvable"}, status_code=400)

    try:
        booking = bookings_api.book_offer(
            beneficiary=user,
            stock_id=body.stock_id,
            quantity=body.quantity,
        )

    except StockDoesNotExist:
        raise ApiErrors({"stock": "stock introuvable"}, status_code=400)

    except (
        exceptions.UserHasInsufficientFunds,
        exceptions.DigitalExpenseLimitHasBeenReached,
        exceptions.PhysicalExpenseLimitHasBeenReached,
    ):
        raise ApiErrors({"code": "INSUFFICIENT_CREDIT"})

    except exceptions.OfferIsAlreadyBooked:
        raise ApiErrors({"code": "ALREADY_BOOKED"})

    except exceptions.StockIsNotBookable:
        raise ApiErrors({"code": "STOCK_NOT_BOOKABLE"})

    return BookOfferResponse(bookingId=booking.id)


@blueprint.native_v1.route("/bookings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=BookingsResponse)
@authenticated_user_required
def get_bookings(user: User) -> BookingsResponse:
    bookings = (
        Booking.query.filter_by(userId=user.id)
        .options(joinedload(Booking.stock).load_only(Stock.id, Stock.beginningDatetime))
        .options(
            joinedload(Booking.stock)
            .joinedload(Stock.offer)
            .load_only(Offer.name, Offer.url, Offer.type, Offer.withdrawalDetails, Offer.extraData)
        )
        .options(joinedload(Booking.stock).joinedload(Stock.offer).joinedload(Offer.mediations))
        .options(
            joinedload(Booking.stock)
            .joinedload(Stock.offer)
            .joinedload(Offer.product)
            .load_only(Product.id, Product.thumbCount)
        )
        .options(
            joinedload(Booking.stock)
            .joinedload(Stock.offer)
            .joinedload(Offer.venue)
            .load_only(Venue.name, Venue.city, Venue.latitude, Venue.longitude)
        )
    ).all()

    ended_bookings = []
    ongoing_bookings = []

    for booking in bookings:
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
                key=lambda b: b.stock.beginningDatetime or b.dateUsed or b.cancellationDate,
                reverse=True,
            )
        ],
        # put permanent bookings at the end with datetime.max
        ongoing_bookings=[
            BookingReponse.from_orm(booking)
            for booking in sorted(
                ongoing_bookings, key=lambda b: b.expirationDate or b.stock.beginningDatetime or datetime.max
            )
        ],
    )


def is_ended_booking(booking: Booking) -> bool:
    if (
        booking.stock.beginningDatetime
        and not booking.isCancelled
        and booking.stock.beginningDatetime >= datetime.utcnow()
    ):
        # consider future events events as "ongoing" even if they are used
        return False

    return (booking.dateUsed or booking.cancellationDate) and not booking.stock.offer.isPermanent


@blueprint.native_v1.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204, on_error_statuses=[400, 404])
@authenticated_user_required
def cancel_booking(user: User, booking_id: int) -> None:
    booking = Booking.query.filter_by(id=booking_id, userId=user.id).first_or_404()
    try:
        bookings_api.cancel_booking_by_beneficiary(user, booking)
    except exceptions.BookingIsAlreadyUsed:
        raise ApiErrors({"code": "ALREADY_USED", "message": "La réservation a déjà été utilisée"})
    except exceptions.CannotCancelConfirmedBooking as e:
        raise ApiErrors({"code": "CONFIRMED_BOOKING", "message": e.errors["booking"][0]})
    except RuntimeError:
        logger.error("Unexpected call to cancel_booking_by_beneficiary with non-beneficiary user %s", user.id)
        raise ApiErrors()
