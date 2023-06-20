import json

import pytest
import requests_mock

from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPI
from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPIException


class StocksTest:
    def setup_method(self):
        self.api_url = "http://example.com/stocks"
        self.provider_api = ProviderAPI(api_url=self.api_url, name="ProviderAPI")

    def test_get_stocks_with_default_limits(self):
        # Given
        siret = "1234"
        stock_response_data = {"some": "data"}

        # When
        with requests_mock.Mocker() as mock:
            mock.get(f"{self.api_url}/{siret}?limit=1000", json=stock_response_data)
            response = self.provider_api.stocks(siret)

        # Then
        assert response == stock_response_data

    def test_get_stocks_with_custom_limits(self):
        # Given
        siret = "1234"
        modified_since = "2019-12-16T00:00:00"
        last_processed_ean = "789"
        stock_response_data = {"some": "data"}

        # When
        expected_url = f"{self.api_url}/{siret}?limit=1000&after={last_processed_ean}&modifiedSince={modified_since}"
        with requests_mock.Mocker() as mock:
            mock.get(expected_url, json=stock_response_data)
            response = self.provider_api.stocks(siret, last_processed_ean, modified_since)

        # Then
        assert response == stock_response_data

    def should_call_api_with_authentication_token_if_given(self):
        # Given
        siret = "1234"
        provider_api = ProviderAPI(api_url=self.api_url, name="x", authentication_token="744563534")

        # When
        with requests_mock.Mocker() as mock:
            mocked_get = mock.get(f"{self.api_url}/{siret}?limit=1000")
            provider_api.stocks(siret)

        # Then
        assert mocked_get.last_request.headers["Authorization"] == "Basic 744563534"

    def should_raise_error_when_provider_api_request_fails(self):
        # Given
        siret = "1234"

        # When
        with requests_mock.Mocker() as mock:
            mock.get(f"{self.api_url}/{siret}?limit=1000", status_code=400)
            with pytest.raises(ProviderAPIException) as exception:
                self.provider_api.stocks(siret=siret)

        # Then
        assert str(exception.value) == f"Error 400 when getting ProviderAPI stocks for SIRET: {siret}"

    def should_return_empty_json_body_when_provider_returns_200_with_no_body(self):
        # Given
        siret = "1234"

        # When
        with requests_mock.Mocker() as mock:
            mock.get(f"{self.api_url}/{siret}?limit=1000", content=b"")
            response = self.provider_api.stocks(siret=siret)

        # Then
        assert response == {}

    def should_raise_error_if_content_is_not_json(self):
        siret = "1234"

        with pytest.raises(json.JSONDecodeError):
            with requests_mock.Mocker() as mock:
                mock.get(f"{self.api_url}/{siret}?limit=1000", content=b"invalid JSON")
                self.provider_api.stocks(siret=siret)


class IsSiretRegisteredTest:
    def setup_method(self):
        self.api_url = "http://example.com/stocks"
        self.provider_api = ProviderAPI(api_url=self.api_url, name="ProviderAPI")

    def test_is_siret_registered_ok(self):
        # Given
        siret = "1234"

        # When
        with requests_mock.Mocker() as mock:
            mock.get(f"{self.api_url}/{siret}")
            registered = self.provider_api.is_siret_registered(siret=siret)

        assert registered

    def test_is_siret_registered_nok_if_not_200(self):
        # Given
        siret = "1234"

        # When
        with requests_mock.Mocker() as mock:
            mock.get(f"{self.api_url}/{siret}", status_code=400)
            registered = self.provider_api.is_siret_registered(siret=siret)

        assert not registered

    def should_call_api_with_authentication_token_if_given(self):
        # Given
        siret = "1234"
        provider_api = ProviderAPI(api_url=self.api_url, name="x", authentication_token="744563534")

        # When
        with requests_mock.Mocker() as mock:
            mocked_get = mock.get(f"{self.api_url}/{siret}")
            registered = provider_api.is_siret_registered(siret=siret)

        # Then
        assert registered
        assert mocked_get.last_request.headers["Authorization"] == "Basic 744563534"
