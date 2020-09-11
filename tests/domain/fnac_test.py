from unittest.mock import Mock

from domain.fnac import get_fnac_stock_information


class GetFnacStockInformationTest:
    def setup_method(self):
        self.siret = '12345678912345'
        self.mock_fnac_stocks = Mock()

    def test_should_return_no_stock_information_when_fnac_api_returns_no_result(self):
        # Given
        last_processed_isbn = ''
        modified_since = ''
        self.mock_fnac_stocks.return_value = {
            "Stocks": []
        }

        # When
        fnac_stock_information = get_fnac_stock_information(self.siret, last_processed_isbn, modified_since,
                                                            get_fnac_stocks=self.mock_fnac_stocks)

        # Then
        self.mock_fnac_stocks.assert_called_once_with(self.siret, last_processed_isbn, modified_since)
        assert len(list(fnac_stock_information)) == 0
