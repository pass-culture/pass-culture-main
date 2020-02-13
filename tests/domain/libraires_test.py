from datetime import datetime
from unittest.mock import Mock

from domain.libraires import get_libraires_stock_information, read_last_modified_date


class GetLibrairesStockInformationTest:
    def setup_method(self):
        self.siret = '12345678912345'
        self.mock_libraires_stocks = Mock()

    def test_should_return_no_stock_information_when_libraires_api_returns_no_result(self):
        # Given
        last_processed_isbn = ''
        modified_since = ''
        self.mock_libraires_stocks.return_value = {
            "total": 0,
            "limit": 20,
            "offset": 0,
            "stocks": []
        }

        # When
        libraires_stock_information = get_libraires_stock_information(self.siret, last_processed_isbn, modified_since,
                                                                      get_libraires_stocks=self.mock_libraires_stocks)

        # Then
        self.mock_libraires_stocks.assert_called_once_with(self.siret, last_processed_isbn, modified_since)
        assert len(list(libraires_stock_information)) == 0

    def test_should_return_correct_stock_information_when_libraires_api_returns_two_stocks(self):
        # Given
        last_processed_isbn = ''
        modified_since = ''
        self.mock_libraires_stocks.return_value = {
            "total": 2,
            "limit": 20,
            "offset": 0,
            "stocks": [
                {
                    "ref": "9780199536986",
                    "available": 1,
                    "price": 6.36
                },
                {
                    "ref": "0000191524088",
                    "available": 1,
                    "price": 9.15
                }
            ]
        }

        # When
        libraires_stock_information = get_libraires_stock_information(self.siret, last_processed_isbn, modified_since,
                                                                      get_libraires_stocks=self.mock_libraires_stocks)

        # Then
        self.mock_libraires_stocks.assert_called_once_with(self.siret, last_processed_isbn, modified_since)
        librairies_stocks_data = list(libraires_stock_information)
        assert len(librairies_stocks_data) == 2
        assert librairies_stocks_data[0] == {'available': 1, 'price': 6.36, 'ref': '9780199536986'}
        assert librairies_stocks_data[1] == {'available': 1, 'price': 9.15, 'ref': '0000191524088'}


class ReadLastModifiedDateTest:
    def test_should_read_libraires_stocks_modifiedsince_datetime_when_it_is_empty(self):
        # Given
        date = None

        # When
        modified_since = read_last_modified_date(date)

        # Then
        assert modified_since == ''

    def test_should_read_libraires_stocks_modifiedsince_datetime_when_it_is_not_empty(self):
        # Given
        date = datetime(2020, 2, 2, 20, 20)

        # When
        modified_since = read_last_modified_date(date)

        # Then
        assert modified_since == '2020-02-02T20:20:00Z'
