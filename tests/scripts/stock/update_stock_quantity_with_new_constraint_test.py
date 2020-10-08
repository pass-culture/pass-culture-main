from datetime import datetime, timedelta
from unittest.mock import patch, call, MagicMock

from pcapi.models import StockSQLEntity
from pcapi.models.db import db
from pcapi.repository import repository
from pcapi.scripts.stock.update_stock_quantity_with_new_constraint import update_stock_quantity_with_new_constraint, \
    _get_old_remaining_quantity, _get_stocks_to_check, _get_stocks_with_negative_remaining_quantity, \
    update_stock_quantity_for_negative_remaining_quantity
from tests.conftest import clean_database
from pcapi.model_creators.generic_creators import create_offerer, create_venue, create_stock, create_booking, \
    create_user
from pcapi.model_creators.specific_creators import create_offer_with_thing_product


class UpdateStockAvailableWithNewConstraintTest:
    @staticmethod
    def setup_method():
        db.engine.execute("ALTER TABLE booking DISABLE TRIGGER ALL;")

    @staticmethod
    def teardown_method():
        db.engine.execute("ALTER TABLE booking ENABLE TRIGGER ALL;")

    @clean_database
    def test_should_update_stock_quantity_when_bookings_quantity_is_more_than_actual_stock_quantity(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        yesterday = datetime.utcnow() - timedelta(days=1)
        stock = create_stock(date_modified=datetime.utcnow(), offer=offer, price=0, quantity=12)
        booking = create_booking(user, stock=stock, quantity=20, is_used=True, date_used=yesterday)
        repository.save(booking)

        mock_application = MagicMock()
        mock_application.redis_client = MagicMock()

        # When
        update_stock_quantity_with_new_constraint(mock_application)

        # Then
        existing_stock = StockSQLEntity.query.first()
        assert existing_stock.remainingQuantity == 12
        assert existing_stock.quantity == 32

    @clean_database
    def test_should_update_stock_quantity_when_remaining_quantity_is_negative(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        yesterday = datetime.utcnow() - timedelta(days=1)
        stock = create_stock(date_modified=datetime.utcnow(), offer=offer, price=0, quantity=1)
        booking = create_booking(user, stock=stock, quantity=2, is_used=True, date_used=yesterday)
        booking1 = create_booking(user, stock=stock, quantity=2, is_used=False)
        repository.save(booking, booking1)

        mock_application = MagicMock()
        mock_application.redis_client = MagicMock()

        # When
        update_stock_quantity_with_new_constraint(mock_application)

        # Then
        existing_stock = StockSQLEntity.query.first()
        assert existing_stock.remainingQuantity == 0
        assert existing_stock.quantity == 4

    @clean_database
    def test_should_keep_remaining_quantity_when_stock_is_not_fully_booked(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(date_modified=datetime.utcnow(), idx=4, offer=offer, price=0, quantity=8)
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking = create_booking(user, stock=stock, quantity=2, is_used=True, date_used=yesterday)
        booking_bis = create_booking(user, stock=stock, quantity=4)
        repository.save(booking, booking_bis)

        mock_application = MagicMock()
        mock_application.redis_client = MagicMock()

        # When
        update_stock_quantity_with_new_constraint(mock_application)

        # Then
        existing_stock = StockSQLEntity.query.get(4)
        assert existing_stock.remainingQuantity == 4
        assert existing_stock.quantity == 10

    @clean_database
    @patch('pcapi.scripts.stock.update_stock_quantity_with_new_constraint.redis.add_offer_id')
    @patch('pcapi.scripts.stock.update_stock_quantity_with_new_constraint._get_stocks_to_check')
    def test_should_update_all_needed_stocks_with_pagination(self, mock_get_stocks_to_check, mock_redis_algolia, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(date_modified=datetime.utcnow(), idx=1, offer=offer, price=0, quantity=12)
        stock2 = create_stock(date_modified=datetime.utcnow(), idx=2, offer=offer, price=0, quantity=10)
        stock3 = create_stock(date_modified=datetime.utcnow(), idx=3, offer=offer, price=0, quantity=4)
        yesterday = datetime.utcnow() - timedelta(days=1)
        booking1 = create_booking(user, stock=stock1, quantity=20, is_used=True, date_used=yesterday)
        booking2 = create_booking(user, stock=stock2, quantity=8, is_used=True, date_used=yesterday)
        booking3 = create_booking(user, stock=stock3, quantity=2, is_used=True, date_used=yesterday)
        repository.save(booking1, booking2, booking3)
        mock_get_stocks_to_check.side_effect = [[stock1, stock2], [stock3]]

        mock_application = MagicMock()
        mock_application.redis_client = MagicMock()

        # When
        update_stock_quantity_with_new_constraint(mock_application, page_size=2)

        # Then
        assert mock_get_stocks_to_check.call_count == 2
        assert mock_get_stocks_to_check.call_args == call(1, 2)

    @clean_database
    @patch('pcapi.scripts.stock.update_stock_quantity_with_new_constraint.redis.add_offer_id')
    def test_should_update_all_needed_stocks_when_stock_has_multiple_bookings(self, mock_redis_algolia, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(date_modified=datetime.utcnow(), idx=1, offer=offer, price=0, quantity=12)
        stock2 = create_stock(date_modified=datetime.utcnow(), idx=2, offer=offer, price=0, quantity=10)
        stock3 = create_stock(date_modified=datetime.utcnow(), idx=3, offer=offer, price=0, quantity=10)
        yesterday = datetime.utcnow() - timedelta(days=1)
        bookings = [
            create_booking(user, stock=stock1, quantity=20, is_used=True, date_used=yesterday),
            create_booking(user, stock=stock1, quantity=20, is_used=True, date_used=yesterday),
            create_booking(user, stock=stock2, quantity=8, is_used=True, date_used=yesterday)
        ]
        repository.save(*bookings, stock3)

        mock_application = MagicMock()
        mock_application.redis_client = MagicMock()

        # When
        update_stock_quantity_with_new_constraint(mock_application, page_size=2)

        # Then
        assert stock1.hasBeenMigrated is True
        assert stock2.hasBeenMigrated is True
        assert stock3.hasBeenMigrated is None

    @clean_database
    def test_should_not_update_values_when_called_twice(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        yesterday = datetime.utcnow() - timedelta(days=1)
        stock = create_stock(date_modified=datetime.utcnow(), offer=offer, price=0, quantity=12)
        booking = create_booking(user, stock=stock, quantity=20, is_used=True, date_used=yesterday)
        repository.save(booking)

        mock_application = MagicMock()
        mock_application.redis_client = MagicMock()
        update_stock_quantity_with_new_constraint(mock_application)

        # When
        update_stock_quantity_with_new_constraint(mock_application)

        # Then
        existing_stock = StockSQLEntity.query.first()
        assert existing_stock.remainingQuantity == 12
        assert existing_stock.quantity == 32

    @clean_database
    def test_should_not_compare_date_used_when_no_value_found(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(date_modified=datetime.utcnow(), offer=offer, price=0, quantity=12)
        booking = create_booking(user, stock=stock, quantity=20, is_used=True, date_used=None)
        repository.save(booking)

        mock_application = MagicMock()
        mock_application.redis_client = MagicMock()

        # When
        update_stock_quantity_with_new_constraint(mock_application)

        # Then
        existing_stock = StockSQLEntity.query.first()
        assert existing_stock.remainingQuantity == 12
        assert existing_stock.quantity == 32

    @clean_database
    @patch('pcapi.scripts.stock.update_stock_quantity_with_new_constraint.redis.add_offer_id')
    def test_should_index_offer_to_algolia_when_stock_has_been_updated(self, mock_add_offer_id_algolia,
                                                                       app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(date_modified=datetime.utcnow(), offer=offer, price=0, quantity=12)
        booking = create_booking(user, stock=stock, quantity=20, is_used=True, date_used=None)
        repository.save(booking)
        offer_id = offer.id

        mock_application = MagicMock()
        mock_application.redis_client = MagicMock()

        # When
        update_stock_quantity_with_new_constraint(mock_application)

        # Then
        mock_add_offer_id_algolia.assert_called_once_with(client=mock_application.redis_client,
                                                          offer_id=offer_id)


class GetOldRemainingQuantityTest:
    @clean_database
    def test_should_return_old_remaining_quantity(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(date_modified=datetime.utcnow(), offer=offer, price=0, quantity=12)
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
        stock = create_stock(offer=offer, quantity=12)
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
        stock = create_stock(is_soft_deleted=True, offer=offer, price=0, quantity=12)
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
        stock = create_stock(offer=offer, price=0, quantity=None)
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
        stock = create_stock(has_been_migrated=True, offer=offer, price=0, quantity=10)
        booking = create_booking(user, stock=stock)
        repository.save(booking)

        # When
        stocks = _get_stocks_to_check()

        # Then
        assert stocks == []


class UpdateStockQuantityForNegativeRemainingQuantityTest:
    @staticmethod
    def setup_method():
        db.engine.execute("ALTER TABLE booking DISABLE TRIGGER ALL;")

    @staticmethod
    def teardown_method():
        db.engine.execute("ALTER TABLE booking ENABLE TRIGGER ALL;")

    @clean_database
    def test_should_adjust_quantity_to_keep_old_remaining_quantity(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(date_modified=datetime.utcnow(), offer=offer, price=0, quantity=1)
        booking = create_booking(user, stock=stock, quantity=6)
        repository.save(booking)

        mock_application = MagicMock()
        mock_application.redis_client = MagicMock()

        # When
        update_stock_quantity_for_negative_remaining_quantity(mock_application)

        # Then
        existing_stock = StockSQLEntity.query.first()
        assert existing_stock.remainingQuantity == 0
        assert existing_stock.quantity == 6
        assert existing_stock.hasBeenMigrated

    @clean_database
    def test_should_not_update_stock_when_remaining_quantity_is_positive(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(date_modified=datetime.utcnow(), offer=offer, price=0, quantity=8)
        booking = create_booking(user, stock=stock, quantity=6)
        booking_bis = create_booking(user, stock=stock, quantity=4, is_cancelled=True)
        repository.save(booking, booking_bis)

        mock_application = MagicMock()
        mock_application.redis_client = MagicMock()

        # When
        update_stock_quantity_for_negative_remaining_quantity(mock_application)

        # Then
        existing_stock = StockSQLEntity.query.first()
        assert existing_stock.remainingQuantity == 2
        assert existing_stock.quantity == 8
        assert not existing_stock.hasBeenMigrated


class GetStocksWithNegativeRemainingQuantityTest:
    @staticmethod
    def setup_method():
        db.engine.execute("ALTER TABLE booking DISABLE TRIGGER ALL;")

    @staticmethod
    def teardown_method():
        db.engine.execute("ALTER TABLE booking ENABLE TRIGGER ALL;")

    @clean_database
    def test_should_return_stock_with_negative_remaining_quantity(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        yesterday = datetime.utcnow() - timedelta(days=1)
        stock = create_stock(date_modified=datetime.utcnow(), offer=offer, price=0, quantity=1)
        booking = create_booking(user, stock=stock, quantity=2, is_used=True, date_used=yesterday)
        booking1 = create_booking(user, stock=stock, quantity=2, is_used=False)
        repository.save(booking, booking1)

        # When
        stocks = _get_stocks_with_negative_remaining_quantity()

        # Then
        assert stocks == [stock]

    @clean_database
    def test_should_not_return_stock_with_positive_remaining_quantity(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0, quantity=5)
        booking = create_booking(user, stock=stock, quantity=2)
        repository.save(booking)

        # When
        stocks = _get_stocks_with_negative_remaining_quantity()

        # Then
        assert stocks == []
