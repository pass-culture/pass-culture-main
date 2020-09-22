from datetime import datetime
from unittest.mock import Mock, patch

from domain.fnac import get_fnac_stock_information, read_last_modified_date, can_be_synchronized_with_fnac


class GetFnacStockInformationTest:
    def setup_method(self):
        self.siret = '12345678912345'
        self.mock_fnac_stocks = Mock()

    def test_should_call_get_fnac_stock_infos_with_correct_params(self):
        # Given
        last_processed_isbn = ''
        modified_since = ''
        self.mock_fnac_stocks.return_value = {
            "stocks": []
        }

        # When
        get_fnac_stock_information(siret=self.siret, last_processed_isbn=last_processed_isbn,
                                   modified_since=modified_since,
                                   get_fnac_stocks=self.mock_fnac_stocks)

        # Then
        self.mock_fnac_stocks.assert_called_once_with(siret=self.siret, last_processed_isbn=last_processed_isbn,
                                                      modified_since=modified_since)

    def test_should_return_no_stock_information_when_fnac_api_returns_no_result(self):
        # Given
        last_processed_isbn = ''
        modified_since = ''
        self.mock_fnac_stocks.return_value = {
            "stocks": []
        }

        # When
        fnac_stock_information = get_fnac_stock_information(siret=self.siret, last_processed_isbn=last_processed_isbn,
                                                            modified_since=modified_since,
                                                            get_fnac_stocks=self.mock_fnac_stocks)

        # Then
        assert len(list(fnac_stock_information)) == 0

    def test_should_return_no_stock_information_when_fnac_api_returns_empty_body_result(self):
        # Given
        last_processed_isbn = ''
        modified_since = ''
        self.mock_fnac_stocks.return_value = {}

        # When
        fnac_stock_information = get_fnac_stock_information(siret=self.siret, last_processed_isbn=last_processed_isbn,
                                                            modified_since=modified_since,
                                                            get_fnac_stocks=self.mock_fnac_stocks)

        # Then
        assert len(list(fnac_stock_information)) == 0

    def test_should_return_correct_stock_information_when_fnac_api_returns_two_stocks(self):
        # Given
        last_processed_isbn = ''
        modified_since = ''
        self.mock_fnac_stocks.return_value = {"stocks": [{"price": 6.36}, {"price": 9.15}]}

        # When
        fnac_stock_information = get_fnac_stock_information(siret=self.siret, last_processed_isbn=last_processed_isbn,
                                                            modified_since=modified_since,
                                                            get_fnac_stocks=self.mock_fnac_stocks)

        # Then
        fnac_stocks_data = list(fnac_stock_information)
        assert len(fnac_stocks_data) == 2


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
        modified_since = read_last_modified_date(date=date)

        # Then
        assert modified_since == '2020-02-02T20:20:00Z'


class CanBeSynchronizedTest:
    @patch('domain.fnac.is_siret_registered')
    def test_should_call_can_be_synchronized_with_fnac_with_correct_param(self, mock_is_siret_registered):
        # Given
        siret = '12345678912345'

        # When
        can_be_synchronized_with_fnac(siret=siret)

        # Then
        mock_is_siret_registered.assert_called_once_with(siret=siret)
