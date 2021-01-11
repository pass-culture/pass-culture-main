from unittest.mock import patch

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.models import Booking
from pcapi.models import ThingType
from pcapi.scripts.booking.create_booking_for_user_on_specific_stock import (
    create_booking_for_user_on_specific_stock_bypassing_capping_limits,
)


class CreateBookingForUserOnSpecificStockBypassingCappingLimitsTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.scripts.booking.create_booking_for_user_on_specific_stock.redis")
    def should_book_an_offer_even_if_physical_offer_capping_is_exeeded(self, mocked_redis, app):
        # Given
        product = offers_factories.DigitalProductFactory()
        stock1 = offers_factories.StockFactory(
            price=200,
            offer__type=str(ThingType.AUDIOVISUEL),
            offer__product=product,
        )
        booking = bookings_factories.BookingFactory(stock=stock1)
        user = booking.user
        stock2 = offers_factories.StockFactory(
            price=200,
            offer__type=str(ThingType.AUDIOVISUEL),
            offer__product=product,
        )

        # When
        create_booking_for_user_on_specific_stock_bypassing_capping_limits(user.id, stock2.id)

        # Then
        assert Booking.query.filter_by(stockId=stock2.id).one() is not None
        mocked_redis.add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=stock2.offer.id)
