from unittest.mock import Mock

from domain.titelive import get_stocks_information
from tests.test_utils import assert_iterator_is_empty


class GetStocksInformation():
    def setup_method(self):
        self.mock_get_titelive_stocks = Mock()

    def test_should_return_no_stock_information_when_api_return_no_result(self):
        # Given
        self.mock_get_titelive_stocks.side_effect = [
            {
                'total': 'null',
                'limit': 5000,
                'stocks': []
            }
        ]
        siret = '345678907659'
        last_processed_isbn = ''

        # When
        stocks_information = get_stocks_information(siret,
                                                    last_processed_isbn,
                                                    get_titelive_stocks_from_api=self.mock_get_titelive_stocks)

        # Then
        self.mock_get_titelive_stocks.assert_called_once_with(siret, last_processed_isbn)
        assert_iterator_is_empty(stocks_information)

    def test_should_return_iterator_with_2_elements(self):
        # Given
        self.mock_get_titelive_stocks.side_effect = [
            {
                'total': 'null',
                'limit': 5000,
                'stocks': [
                    {
                        "ref": "0002730757438",
                        "available": 0,
                        "price": 4500,
                        "validUntil": "2019-10-31T15:10:27Z"
                    },
                    {
                        "ref": "0002730757443",
                        "available": 1,
                        "price": 9500,
                        "validUntil": "2019-11-24T11:40:37Z"
                    }
                ]
            }
        ]
        siret = '345678907659'
        last_processed_isbn = ''

        # When
        stocks_information = get_stocks_information(siret,
                                                    last_processed_isbn,
                                                    get_titelive_stocks_from_api=self.mock_get_titelive_stocks)

        # Then
        self.mock_get_titelive_stocks.assert_called_once_with(siret, last_processed_isbn)
        number_of_stock_info = 0
        for stock_info in stocks_information:
            number_of_stock_info += 1
        assert number_of_stock_info == 2
