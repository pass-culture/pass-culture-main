from datetime import datetime

import pytest

from domain.stock.stock_exceptions import StockDoesntExist
from domain.stock.stock import Stock
from repository import repository
from infrastructure.repository.stock.stock_sql_repository import StockSQLRepository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_stock_from_offer


class StockSQLRepositoryTest:

    def setup_method(self):
        self.stock_sql_repository = StockSQLRepository()

    @clean_database
    def test_should_return_stock_with_correct_information(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        thing_offer = create_offer_with_thing_product(venue)
        stock_sql_entity = create_stock_from_offer(
            offer=thing_offer,
            quantity=2,
            price=10,
            booking_limit_datetime=datetime(2020, 3, 18)
        )
        repository.save(stock_sql_entity)

        # When
        stock = self.stock_sql_repository.find_stock_by_id(stock_sql_entity.id)

        # Then
        expected_stock = Stock(
            identifier=stock_sql_entity.id,
            quantity=2,
            beginning_datetime=None,
            booking_limit_datetime=datetime(2020, 3, 18),
            price=10,
            offer=thing_offer
        )
        assert type(stock) == Stock
        assert self._are_stocks_equals(stock, expected_stock)

    def test_should_raise_StockDoesntExist_when_stock_is_not_found(self):
        # Given
        unknown_id = 999

        # When
        with pytest.raises(StockDoesntExist) as error:
            self.stock_sql_repository.find_stock_by_id(unknown_id)

        # Then
        assert error.value.errors['stockId'] == ['stockId ne correspond à aucun stock']

    def _are_stocks_equals(self, stock1: Stock, stock2: Stock) -> bool:
        return stock1.quantity == stock2.quantity \
               and stock1.bookingLimitDatetime == stock2.bookingLimitDatetime \
               and stock1.beginningDatetime == stock2.beginningDatetime \
               and stock1.price == stock2.price \
               and stock1.offer == stock2.offer
