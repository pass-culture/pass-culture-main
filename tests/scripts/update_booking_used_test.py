from datetime import datetime

from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.models import Booking
from pcapi.scripts.update_booking_used import update_booking_used_after_stock_occurrence


class UpdateBookingUsedTest:
    @pytest.mark.usefixtures("db_session")
    def test_do_not_update_if_thing_product(self):
        # Given
        stock = offers_factories.ThingStockFactory()
        bookings_factories.BookingFactory(stock=stock)

        # When
        update_booking_used_after_stock_occurrence()

        # Then
        booking = Booking.query.first()
        assert not booking.isUsed
        assert not booking.dateUsed

    @freeze_time("2019-10-13")
    @pytest.mark.usefixtures("db_session")
    def test_update_booking_used_when_event_date_is_3_days_before(self):
        # Given
        beginning = datetime(2019, 10, 9, 10, 20, 0)
        stock = offers_factories.EventStockFactory(beginningDatetime=beginning)
        bookings_factories.BookingFactory(stock=stock)

        # When
        update_booking_used_after_stock_occurrence()

        # Then
        booking = Booking.query.first()
        assert booking.isUsed
        assert booking.dateUsed == datetime(2019, 10, 13)

    @freeze_time("2019-10-13")
    @pytest.mark.usefixtures("db_session")
    def test_does_not_update_booking_if_already_used(self):
        # Given
        beginning = datetime(2019, 10, 9, 10, 20, 0)
        stock = offers_factories.EventStockFactory(beginningDatetime=beginning)
        booking = bookings_factories.BookingFactory(stock=stock, isUsed=True)
        initial_date_used = booking.dateUsed

        # When
        update_booking_used_after_stock_occurrence()

        # Then
        booking = Booking.query.first()
        assert booking.isUsed
        assert booking.dateUsed == initial_date_used

    @freeze_time("2019-10-10")
    @pytest.mark.usefixtures("db_session")
    def test_update_booking_used_when_event_date_is_only_1_day_before(self):
        # Given
        beginning = datetime(2019, 10, 9, 10, 20, 0)
        stock = offers_factories.EventStockFactory(beginningDatetime=beginning)
        bookings_factories.BookingFactory(stock=stock)

        # When
        update_booking_used_after_stock_occurrence()

        # Then
        booking = Booking.query.first()
        assert not booking.isUsed
        assert booking.dateUsed is None
