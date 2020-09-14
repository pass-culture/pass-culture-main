from unittest.mock import Mock

from datetime import datetime

from domain.fnac import get_fnac_stock_information, read_last_modified_date


class GetFnacStockInformationTest:
    def setup_method(self):
        self.siret = '12345678912345'
        self.mock_fnac_stocks = Mock()

    def test_should_return_no_stock_information_when_fnac_api_returns_no_result(self):
        # Given
        last_processed_isbn = ''
        modified_since = ''
        self.mock_fnac_stocks.return_value = {
            "total": 2,
            "limit": 20,
            "offset": 0,
            "Stocks": []
        }

        # When
        fnac_stock_information = get_fnac_stock_information(self.siret, last_processed_isbn, modified_since,
                                                            get_fnac_stocks=self.mock_fnac_stocks)

        # Then
        self.mock_fnac_stocks.assert_called_once_with(self.siret, last_processed_isbn, modified_since)
        assert len(list(fnac_stock_information)) == 0

    def test_should_return_correct_stock_information_when_fnac_api_returns_two_stocks(self):
        # Given
        last_processed_isbn = ''
        modified_since = ''
        self.mock_fnac_stocks.return_value = {
            "Total": 2,
            "Limit": 20,
            "Offset": 0,
            "Stocks": [
                {
                    "Ref": "9780199536986",
                    "Available": 1,
                    "Price": 6.36
                },
                {
                    "Ref": "0000191524088",
                    "Available": 1,
                    "Price": 9.15
                }
            ]
        }

        # When
        fnac_stock_information = get_fnac_stock_information(self.siret,
                                                            last_processed_isbn,
                                                            modified_since,
                                                            get_fnac_stocks=self.mock_fnac_stocks)

        # Then
        self.mock_fnac_stocks.assert_called_once_with(self.siret, last_processed_isbn, modified_since)
        fnac_stocks_data = list(fnac_stock_information)
        assert len(fnac_stocks_data) == 2
        assert fnac_stocks_data[0] == {'Available': 1, 'Price': 6.36, 'Ref': '9780199536986'}
        assert fnac_stocks_data[1] == {'Available': 1, 'Price': 9.15, 'Ref': '0000191524088'}


class ReadLastModifiedDateTest:
    def test_should_read_fnac_stocks_modifiedsince_datetime_when_it_is_empty(self):
        # Given
        date = None

        # When
        modified_since = read_last_modified_date(date)

        # Then
        assert modified_since == ''

    def test_should_read_fnac_stocks_modifiedsince_datetime_when_it_is_not_empty(self):
        # Given
        date = datetime(2020, 2, 2, 20, 20)

        # When
        modified_since = read_last_modified_date(date)

        # Then
        assert modified_since == '2020-02-02T20:20:00Z'
