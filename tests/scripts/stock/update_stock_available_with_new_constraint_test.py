from datetime import datetime, timedelta
from unittest.mock import patch, call

from models import Stock
from models.db import db
from repository import repository
from scripts.stock.update_stock_available_with_new_constraint import update_stock_available_with_new_constraint, \
    _get_old_remaining_quantity, _get_stocks_to_check
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_stock, create_booking, \
    create_user
from tests.model_creators.specific_creators import create_offer_with_thing_product


class UpdateStockAvailableWithNewConstraintTest:
    @staticmethod
    def setup_method():
        db.engine.execute("ALTER TABLE booking DISABLE TRIGGER ALL;")

    @staticmethod
    def teardown_method():
        db.engine.execute("ALTER TABLE booking ENABLE TRIGGER ALL;")

    @clean_database
    def test_should_update_stock_available_when_bookings_quantity_is_more_than_actual_stock_quantity(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        yesterday = datetime.utcnow() - timedelta(days=1)
        stock = create_stock(offer=offer, available=12, price=0, date_modified=datetime.utcnow())
        booking = create_booking(user, stock=stock, quantity=20, is_used=True, date_used=yesterday)
        repository.save(booking)

        # When
        update_stock_available_with_new_constraint()

        # Then
        existing_stock = Stock.query.first()
        assert existing_stock.remainingQuantity == 12
        assert existing_stock.available == 32


    @clean_database
    def test_should_keep_remaining_quantity_when_stock_is_not_full_booked(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(idx=4, offer=offer, available=8, price=0, date_modified=datetime.utcnow())
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(user, stock=stock, quantity=2, is_used=True, date_used=yesterday)
        booking_bis = create_booking(user, stock=stock, quantity=4)
        repository.save(booking, booking_bis)

        # When
        update_stock_available_with_new_constraint()

        # Then
        existing_stock = Stock.query.get(4)
        assert existing_stock.remainingQuantity == 4
        assert existing_stock.available == 10


    @clean_database
    @patch('scripts.stock.update_stock_available_with_new_constraint._get_stocks_to_check')
    def test_should_update_all_needed_stocks_with_pagination(self, mock_get_stocks_to_check, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(idx=1, offer=offer, available=12, price=0, date_modified=datetime.utcnow())
        stock2 = create_stock(idx=2, offer=offer, available=10, price=0, date_modified=datetime.utcnow())
        stock3 = create_stock(idx=3, offer=offer, available=4, price=0, date_modified=datetime.utcnow())
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking1 = create_booking(user, stock=stock1, quantity=20, is_used=True, date_used=yesterday)
        booking2 = create_booking(user, stock=stock2, quantity=8, is_used=True, date_used=yesterday)
        booking3 = create_booking(user, stock=stock3, quantity=2, is_used=True, date_used=yesterday)
        repository.save(booking1, booking2, booking3)
        mock_get_stocks_to_check.side_effect = [[stock1, stock2], [stock3]]

        # When
        update_stock_available_with_new_constraint(page_size=2)

        # Then
        assert mock_get_stocks_to_check.call_count == 2
        assert mock_get_stocks_to_check.call_args == call(1, 2)

    @clean_database
    def test_should_not_update_values_when_called_twice(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        yesterday = datetime.utcnow() - timedelta(days=1)
        stock = create_stock(offer=offer, available=12, price=0, date_modified=datetime.utcnow())
        booking = create_booking(user, stock=stock, quantity=20, is_used=True, date_used=yesterday)
        repository.save(booking)
        update_stock_available_with_new_constraint()

        # When
        update_stock_available_with_new_constraint()

        # Then
        existing_stock = Stock.query.first()
        assert existing_stock.remainingQuantity == 12
        assert existing_stock.available == 32


class GetOldRemainingQuantityTest:
    @clean_database
    def test_should_return_old_remaining_quantity(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, available=12, price=0, date_modified=datetime.utcnow())
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking_used_before_stock_update = create_booking(user, stock=stock, quantity=2, is_used=True,
                                                          date_used=yesterday)
        booking_cancelled = create_booking(user, stock=stock, quantity=2, is_cancelled=True)
        repository.save(booking_used_before_stock_update, booking_cancelled)

        # When
        result = _get_old_remaining_quantity(stock)

        # Then
        assert result == 12


class GetStocksToCheckTest:
    @clean_database
    def test_should_not_return_stocks_with_no_bookings(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, available=12)
        repository.save(stock)

        # When
        stocks = _get_stocks_to_check()

        # Then
        assert stocks == []

    @clean_database
    def test_should_not_return_soft_deleted_stocks(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0, available=12, is_soft_deleted=True)
        booking = create_booking(user, stock=stock)
        repository.save(booking)

        # When
        stocks = _get_stocks_to_check()

        # Then
        assert stocks == []

    @clean_database
    def test_should_not_return_stock_with_unlimited_quantity(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0, available=None)
        booking = create_booking(user, stock=stock)
        repository.save(booking)

        # When
        stocks = _get_stocks_to_check()

        # Then
        assert stocks == []

    @clean_database
    def test_should_not_return_stock_that_has_already_been_migrated(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0, available=10, has_been_migrated=True)
        booking = create_booking(user, stock=stock)
        repository.save(booking)

        # When
        stocks = _get_stocks_to_check()

        # Then
        assert stocks == []
