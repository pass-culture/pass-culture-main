from flask import current_app as app

from pcapi.connectors import redis
from pcapi.core.bookings import models
from pcapi.core.bookings import validation
from pcapi.models import Stock
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.repository import repository
from pcapi.utils.token import random_token


# FIXME (dbaty): if we really want to keep this feature, we should
# rather add a new `check_expenses_limits=False` argument to
# `core.bookings.api.book_offer()` and let people call it directly.
# And properly log it because the practice seems questionable to me...
def create_booking_for_user_on_specific_stock_bypassing_capping_limits(user_id: int, stock_id: int) -> None:
    stock = Stock.query.get(stock_id)
    user = UserSQLEntity.query.get(user_id)
    quantity = 1

    validation.check_offer_already_booked(user, stock.offer)
    validation.check_quantity(stock.offer, quantity)
    validation.check_can_book_free_offer(user, stock)
    validation.check_stock_is_bookable(stock)

    booking = models.Booking()
    # FIXME: this is not right. PcObject's constructor should allow
    # `Booking(stock=stock, ...)`
    booking.userId = user.id
    booking.stockId = stock.id
    booking.amount = stock.price
    booking.quantity = quantity
    booking.token = random_token()
    repository.save(booking)

    redis.add_offer_id(client=app.redis_client, offer_id=stock.offerId)
