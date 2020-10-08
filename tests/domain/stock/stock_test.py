from datetime import datetime

from freezegun import freeze_time

from domain.stock.stock import Stock
from model_creators.generic_creators import create_offerer, create_venue, create_user, create_booking
from model_creators.specific_creators import create_offer_with_thing_product, create_stock_from_offer


class HasBookingLimitDatetimePassedTest:
    @freeze_time('2019-07-10')
    def test_should_return_true_when_booking_limit_datetime_is_in_the_past(self):
        # Given
        stock = Stock(
            beginning_datetime=None,
            booking_limit_datetime=datetime(2019, 7, 9),
            bookings=None,
            identifier=1,
            is_soft_deleted=False,
            offer=None,
            price=1,
            quantity=1,
        )

        # When
        has_booking_limit_datetime_passed = stock.has_booking_limit_datetime_passed()

        # Then
        assert has_booking_limit_datetime_passed

    @freeze_time('2019-07-10')
    def test_should_return_false_when_booking_limit_datetime_is_in_the_future(self):
        # Given
        stock = Stock(
            beginning_datetime=None,
            booking_limit_datetime=datetime(2019, 7, 20),
            bookings=[],
            identifier=1,
            is_soft_deleted=False,
            offer=None,
            price=1,
            quantity=1,
        )

        # When
        has_booking_limit_datetime_passed = stock.has_booking_limit_datetime_passed()

        # Then
        assert not has_booking_limit_datetime_passed

    @freeze_time('2019-07-10')
    def test_should_return_false_when_no_booking_datetime_limit(self):
        # Given
        stock = Stock(
            beginning_datetime=None,
            booking_limit_datetime=None,
            bookings=[],
            identifier=1,
            is_soft_deleted=False,
            offer=None,
            price=1,
            quantity=1,
        )

        # When
        has_booking_limit_datetime_passed = stock.has_booking_limit_datetime_passed()

        # Then
        assert not has_booking_limit_datetime_passed


class BookingsQuantityTest:
    def test_should_return_0_when_no_bookings(self):
        # Given
        stock = Stock(
            beginning_datetime=None,
            booking_limit_datetime=None,
            bookings=[],
            identifier=1,
            is_soft_deleted=False,
            offer=None,
            price=1,
            quantity=1,
        )

        # When
        bookings_quantity = stock.bookings_quantity()

        # Then
        assert bookings_quantity == 0

    def test_should_return_the_quantity_of_bookings(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock_sql_entity = create_stock_from_offer(offer, price=0)
        user = create_user()
        booking = create_booking(user=user, stock=stock_sql_entity, quantity=1)
        stock = Stock(
            beginning_datetime=None,
            booking_limit_datetime=None,
            bookings=[booking],
            identifier=1,
            is_soft_deleted=False,
            offer=None,
            price=1,
            quantity=1,
        )

        # When
        bookings_quantity = stock.bookings_quantity()

        # Then
        assert bookings_quantity == 1

    def test_should_not_include_cancelled_booking(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock_sql_entity = create_stock_from_offer(offer, price=0)
        user = create_user()
        booking = create_booking(user=user, stock=stock_sql_entity, quantity=1)
        cancelled_booking = create_booking(user=user, is_cancelled=True, stock=stock_sql_entity, quantity=2)
        stock = Stock(
            beginning_datetime=None,
            booking_limit_datetime=None,
            bookings=[booking, cancelled_booking],
            identifier=1,
            is_soft_deleted=False,
            offer=None,
            price=1,
            quantity=1,
        )

        # When
        bookings_quantity = stock.bookings_quantity()

        # Then
        assert bookings_quantity == 1


class StockRemainingQuantityTest:
    def test_should_be_equal_to_total_stock_when_there_is_no_booking(self):
        # Given
        stock = Stock(
            beginning_datetime=None,
            booking_limit_datetime=None,
            bookings=[],
            identifier=1,
            is_soft_deleted=False,
            offer=None,
            price=1,
            quantity=2,
        )

        # When
        remaining_quantity = stock.remaining_quantity()

        # Then
        assert remaining_quantity == 2

    def test_should_be_0_when_all_stocks_are_booked(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock_from_offer(offer, quantity=2, price=0)
        user = create_user()
        booking1 = create_booking(user=user, stock=stock, is_cancelled=False, quantity=1)
        booking2 = create_booking(user=user, stock=stock, is_cancelled=False, quantity=1)
        stock = Stock(
            beginning_datetime=None,
            booking_limit_datetime=None,
            bookings=[booking1, booking2],
            identifier=1,
            is_soft_deleted=False,
            offer=None,
            price=1,
            quantity=2,
        )

        # When
        remaining_quantity = stock.remaining_quantity()

        # Then
        assert remaining_quantity == 0

    def test_should_be_unlimited_when_stock_is_unlimited(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock_sql_entity = create_stock_from_offer(offer, quantity=None, price=0)
        user = create_user()
        booking = create_booking(user=user, stock=stock_sql_entity, quantity=100)
        stock = Stock(
            beginning_datetime=None,
            booking_limit_datetime=None,
            bookings=[booking],
            identifier=1,
            is_soft_deleted=False,
            offer=None,
            price=1,
            quantity=None,
        )

        # When
        remaining_quantity = stock.remaining_quantity()

        # Then
        assert remaining_quantity == 'unlimited'
