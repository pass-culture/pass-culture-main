from datetime import datetime
from unittest.mock import MagicMock

from pcapi.infrastructure.repository.stock_provider.stock_provider_praxiel import StockProviderPraxielRepository


class StockProviderPraxielRepositoryTest:
    def setup_method(self):
        self.stock_provider_praxiel_repository = StockProviderPraxielRepository()
        self.stock_provider_praxiel_repository.praxiel_api.stocks = MagicMock()
        self.stock_provider_praxiel_repository.praxiel_api.is_siret_registered = MagicMock()

    def should_instanciate_provider_api_with_correct_params(self):
        # Then
        assert self.stock_provider_praxiel_repository.praxiel_api.api_url == 'https://www.praxiel-passculture.fr/stocks'
        assert self.stock_provider_praxiel_repository.praxiel_api.name == 'Praxiel/Inference'

    def should_call_provider_api_stocks_with_expected_arguments(self):
        # When
        self.stock_provider_praxiel_repository.stocks_information(siret='12345678912345',
                                                                  last_processed_reference='9782070584628',
                                                                  modified_since=datetime(2019, 10, 1))

        # Then
        self.stock_provider_praxiel_repository.praxiel_api.stocks.assert_called_once_with(siret='12345678912345',
                                                                                          last_processed_reference='9782070584628',
                                                                                          modified_since='2019-10-01T00:00:00Z')

    def should_set_empty_modified_since_date_when_no_modified_since_date_given(self):
        # When
        self.stock_provider_praxiel_repository.stocks_information(siret='12345678912345',
                                                                  last_processed_reference='9782070584628')

        # Then
        self.stock_provider_praxiel_repository.praxiel_api.stocks.assert_called_once_with(siret='12345678912345',
                                                                                          last_processed_reference='9782070584628',
                                                                                          modified_since='')

    def should_return_no_stock_information_when_praxiel_api_returns_no_result(self):
        # Given
        self.stock_provider_praxiel_repository.praxiel_api.stocks.return_value = {
            "total": 0,
            "limit": 20,
            "offset": 0,
            "stocks": []
        }

        # When
        praxiel_stock_information = self.stock_provider_praxiel_repository.stocks_information(
            siret='12345678912345',
            last_processed_reference='9782070584628',
            modified_since=datetime(2019, 10, 1))

        # Then
        assert len(list(praxiel_stock_information)) == 0

    def should_return_correct_stock_information_when_praxiel_api_returns_two_stocks(self):
        # Given
        self.stock_provider_praxiel_repository.praxiel_api.stocks.return_value = {
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
        praxiel_stock_information = self.stock_provider_praxiel_repository.stocks_information(
            siret='12345678912345',
            last_processed_reference='9782070584628',
            modified_since=datetime(2019, 10, 1))

        # Then
        praxiel_stocks_data = list(praxiel_stock_information)
        assert len(praxiel_stocks_data) == 2
        assert praxiel_stocks_data[0] == {'available': 1, 'price': 6.36, 'ref': '9780199536986'}
        assert praxiel_stocks_data[1] == {'available': 1, 'price': 9.15, 'ref': '0000191524088'}

    def should_call_provider_api_siret_with_expected_siret(self):
        # When
        self.stock_provider_praxiel_repository.can_be_synchronized(siret='12345678912345')

        # Then
        self.stock_provider_praxiel_repository.praxiel_api.is_siret_registered.assert_called_once_with(
            siret='12345678912345')
