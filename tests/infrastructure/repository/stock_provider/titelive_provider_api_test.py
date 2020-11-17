from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPIException
from pcapi.infrastructure.repository.stock_provider.titelive_provider_api import TiteliveProviderAPI


class TiteliveProviderAPITest:
    class StocksTest:
        def setup_method(self):
            self.provider_api = TiteliveProviderAPI(api_url="http://example.com/stocks", name="ProviderAPI")

        @patch("pcapi.infrastructure.repository.stock_provider.provider_api.requests")
        def should_raise_error_when_provider_api_request_fails(self, requests):
            # Given
            requests.get = MagicMock()
            siret = "12345678912345"
            requests.get.return_value = MagicMock(status_code=400)

            # When
            with pytest.raises(ProviderAPIException) as exception:
                self.provider_api.stocks(siret)

            # Then
            assert str(exception.value) == "Error 400 when getting ProviderAPI stocks for SIRET: 12345678912345"

        @patch("pcapi.infrastructure.repository.stock_provider.provider_api.requests")
        def should_return_empty_json_body_when_provider_returns_200_with_no_body(self, requests):
            # Given
            requests.get = MagicMock()
            siret = "12345678912345"
            mock_response = MagicMock()
            mock_response.side_effect = ValueError
            requests.get.return_value = MagicMock(status_code=200, json=mock_response)

            # When
            response = self.provider_api.stocks(siret)

            # Then
            assert response == {}

        @patch("pcapi.infrastructure.repository.stock_provider.provider_api.requests")
        def should_call_provider_api_with_given_siret(self, requests):
            # Given
            requests.get = MagicMock()
            siret = "12345678912345"
            requests.get.return_value = MagicMock(status_code=200)

            # When
            self.provider_api.stocks(siret)

            # Then
            requests.get.assert_called_once_with(
                url="http://example.com/stocks/12345678912345",
                params={"limit": "1000", "inStock": "1"},
                headers={},
                timeout=60,
            )

        @patch("pcapi.infrastructure.repository.stock_provider.provider_api.requests")
        def should_call_provider_api_with_available_stocks_after_last_isbn(self, requests):
            # Given
            requests.get = MagicMock()
            siret = "12345678912345"
            last_processed_isbn = "9780199536986"
            modified_since = ""
            only_available_stocks = "1"
            requests.get.return_value = MagicMock(status_code=200)

            # When
            self.provider_api.stocks(siret, last_processed_isbn, modified_since)

            # Then
            requests.get.assert_called_once_with(
                url="http://example.com/stocks/12345678912345",
                params={"limit": "1000", "after": last_processed_isbn, "inStock": only_available_stocks},
                headers={},
                timeout=60,
            )

        @patch("pcapi.infrastructure.repository.stock_provider.provider_api.requests")
        def should_call_provider_api_with_all_stocks_after_last_synchronization(self, requests):
            # Given
            requests.get = MagicMock()
            siret = "12345678912345"
            last_processed_isbn = ""
            last_synchronization_date = "2019-12-16T00:00:00"
            requests.get.return_value = MagicMock(status_code=200)

            # When
            self.provider_api.stocks(siret, last_processed_isbn, last_synchronization_date)

            # Then
            requests.get.assert_called_once_with(
                url="http://example.com/stocks/12345678912345",
                params={"limit": "1000", "modifiedSince": last_synchronization_date},
                headers={},
                timeout=60,
            )

        @patch("pcapi.infrastructure.repository.stock_provider.provider_api.requests")
        def should_call_provider_api_with_given_all_parameters(self, requests):
            # Given
            requests.get = MagicMock()
            siret = "12345678912345"
            last_processed_isbn = "9780199536986"
            modified_since = "2019-12-16T00:00:00"
            requests.get.return_value = MagicMock(status_code=200)

            # When
            self.provider_api.stocks(siret, last_processed_isbn, modified_since)

            # Then
            requests.get.assert_called_once_with(
                url="http://example.com/stocks/12345678912345",
                params={"limit": "1000", "after": last_processed_isbn, "modifiedSince": modified_since},
                headers={},
                timeout=60,
            )

    class IsSiretRegisteredTest:
        def setup_method(self):
            self.provider_api = TiteliveProviderAPI(api_url="http://example.com/stocks", name="ProviderAPI")

        @patch("pcapi.infrastructure.repository.stock_provider.provider_api.requests")
        def should_call_provider_api_with_given_siret(self, requests):
            # Given
            requests.get = MagicMock()
            siret = "12345678912345"
            requests.get.return_value = MagicMock(status_code=200)

            # When
            self.provider_api.is_siret_registered(siret)

            # Then
            requests.get.assert_called_once_with(url="http://example.com/stocks/12345678912345", headers={}, timeout=60)

        @patch("pcapi.infrastructure.repository.stock_provider.provider_api.requests")
        def should_returns_true_if_api_returns_200(self, requests):
            # Given
            requests.get = MagicMock()
            siret = "12345678912345"
            requests.get.return_value = MagicMock(status_code=200)

            # When
            output = self.provider_api.is_siret_registered(siret)

            # Then
            assert output is True

        @patch("pcapi.infrastructure.repository.stock_provider.provider_api.requests")
        def should_returns_false_when_provider_api_request_fails(self, requests):
            # Given
            requests.get = MagicMock()
            siret = "12345678912345"
            requests.get.return_value = MagicMock(status_code=400)

            # When
            output = self.provider_api.is_siret_registered(siret)

            # Then
            assert output is False
