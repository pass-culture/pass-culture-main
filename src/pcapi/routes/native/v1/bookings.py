from datetime import datetime

from sqlalchemy.orm import joinedload

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.exceptions as exceptions
from pcapi.core.bookings.models import Booking
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.routes.native.security import authenticated_user_required
from pcapi.routes.native.v1.serialization.bookings import BookOfferRequest
from pcapi.routes.native.v1.serialization.bookings import BookingReponse
from pcapi.routes.native.v1.serialization.bookings import BookingsResponse
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@blueprint.native_v1.route("/book_offer", methods=["POST"])
@spectree_serialize(api=blueprint.api, on_success_status=204)
@authenticated_user_required
def book_offer(user: User, body: BookOfferRequest) -> None:
    stock = Stock.query.get(body.stock_id)
    if not stock:
        raise ApiErrors({"stock": "stock introuvable"}, status_code=404)

    try:
        bookings_api.book_offer(
            beneficiary=user,
            stock=stock,
            quantity=body.quantity,
        )

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
        if (booking.dateUsed or booking.cancellationDate) and not booking.stock.offer.isPermanent:
            ended_bookings.append(booking)
        else:
            ongoing_bookings.append(booking)

    return BookingsResponse(
        ended_bookings=[
            BookingReponse.from_orm(booking)
            for booking in sorted(ended_bookings, key=lambda b: b.dateUsed or b.cancellationDate, reverse=True)
        ],
        # put permanent bookings at the end with datetime.max
        ongoing_bookings=[
            BookingReponse.from_orm(booking)
            for booking in sorted(
                ongoing_bookings, key=lambda b: b.expirationDate or b.stock.beginningDatetime or datetime.max
            )
        ],
    )
