from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPI
from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPIException


class ProviderAPITest:
    class StocksTest:
        def setup_method(self):
            self.provider_api = ProviderAPI(api_url='http://example.com/stocks', name='ProviderAPI')

        @patch('pcapi.infrastructure.repository.stock_provider.provider_api.requests')
        def should_raise_error_when_provider_api_request_fails(self, requests):
            # Given
            requests.get = MagicMock()
            siret = '12345678912345'
            requests.get.return_value = MagicMock(status_code=400)

            # When
            with pytest.raises(ProviderAPIException) as exception:
                self.provider_api.stocks(siret)

            # Then
            assert str(exception.value) == 'Error 400 when getting ProviderAPI stocks for SIRET: 12345678912345'

            requests.get = MagicMock()

        @patch('pcapi.infrastructure.repository.stock_provider.provider_api.requests')
        def should_return_empty_json_body_when_provider_returns_200_with_no_body(self, requests):
            # Given
            requests.get = MagicMock()
            siret = '12345678912345'
            mock_response = MagicMock()
            mock_response.side_effect = ValueError
            requests.get.return_value = MagicMock(status_code=200, json=mock_response)

            # When
            response = self.provider_api.stocks(siret)

            # Then
            assert response == {}

            requests.get = MagicMock()

        @patch('pcapi.infrastructure.repository.stock_provider.provider_api.requests')
        def should_call_provider_api_with_given_siret(self, requests):
            # Given
            requests.get = MagicMock()
            siret = '12345678912345'
            requests.get.return_value = MagicMock(status_code=200)

            # When
            self.provider_api.stocks(siret)

            # Then
            requests.get.assert_called_once_with(
                url='http://example.com/stocks/12345678912345', params={'limit': '1000'}, headers={})

        @patch('pcapi.infrastructure.repository.stock_provider.provider_api.requests')
        def should_call_provider_api_with_given_siret_and_last_processed_isbn(self,requests):
            # Given
            requests.get = MagicMock()
            siret = '12345678912345'
            last_processed_isbn = '9780199536986'
            modified_since = ''
            requests.get.return_value = MagicMock(status_code=200)

            # When
            self.provider_api.stocks(siret, last_processed_isbn, modified_since)

            # Then
            requests.get.assert_called_once_with(url='http://example.com/stocks/12345678912345',
                                                 params={
                                                     'limit': '1000',
                                                     'after': last_processed_isbn
                                                 },
                                                 headers={})

        @patch('pcapi.infrastructure.repository.stock_provider.provider_api.requests')
        def should_call_provider_api_with_given_siret_and_last_modification_date(self, requests):
            # Given
            requests.get = MagicMock()
            siret = '12345678912345'
            last_processed_isbn = ''
            modified_since = '2019-12-16T00:00:00'
            requests.get.return_value = MagicMock(status_code=200)

            # When
            self.provider_api.stocks(siret, last_processed_isbn, modified_since)

            # Then
            requests.get.assert_called_once_with(url='http://example.com/stocks/12345678912345',
                                                 params={
                                                     'limit': '1000',
                                                     'modifiedSince': modified_since
                                                 },
                                                 headers={})

        @patch('pcapi.infrastructure.repository.stock_provider.provider_api.requests')
        def should_call_provider_api_with_given_all_parameters(self, requests):
            # Given
            requests.get = MagicMock()
            siret = '12345678912345'
            last_processed_isbn = '9780199536986'
            modified_since = '2019-12-16T00:00:00'
            requests.get.return_value = MagicMock(status_code=200)

            # When
            self.provider_api.stocks(siret, last_processed_isbn, modified_since)

            # Then
            requests.get.assert_called_once_with(url='http://example.com/stocks/12345678912345',
                                                 params={
                                                     'limit': '1000',
                                                     'after': last_processed_isbn,
                                                     'modifiedSince': modified_since
                                                 },
                                                 headers={})

        @patch('pcapi.infrastructure.repository.stock_provider.provider_api.requests')
        def should_call_api_with_authentication_token_if_given(self, requests):
            # Given
            requests.get = MagicMock()
            siret = '12345678912345'
            last_processed_isbn = '9780199536986'
            modified_since = '2019-12-16T00:00:00'
            requests.get.return_value = MagicMock(status_code=200)
            self.provider_api = ProviderAPI(api_url='http://example.com/stocks',
                                            name='ProviderAPI',
                                            authentication_token="744563534")

            # When
            self.provider_api.stocks(siret, last_processed_isbn, modified_since)

            # Then
            requests.get.assert_called_once_with(url='http://example.com/stocks/12345678912345',
                                                 params={
                                                     'limit': '1000',
                                                     'after': last_processed_isbn,
                                                     'modifiedSince': modified_since
                                                 },
                                                 headers={'Authorization': 'Basic 744563534'})

    class IsSiretRegisteredTest:
        def setup_method(self):
            self.provider_api = ProviderAPI(api_url='http://example.com/stocks', name='ProviderAPI')

        @patch('pcapi.infrastructure.repository.stock_provider.provider_api.requests')
        def should_call_provider_api_with_given_siret(self, requests):
            # Given
            requests.get = MagicMock()
            siret = '12345678912345'
            requests.get.return_value = MagicMock(status_code=200)

            # When
            self.provider_api.is_siret_registered(siret)

            # Then
            requests.get.assert_called_once_with(url='http://example.com/stocks/12345678912345', headers={})

        @patch('pcapi.infrastructure.repository.stock_provider.provider_api.requests')
        def should_returns_true_if_api_returns_200(self, requests):
            # Given
            requests.get = MagicMock()
            siret = '12345678912345'
            requests.get.return_value = MagicMock(status_code=200)

            # When
            output = self.provider_api.is_siret_registered(siret)

            # Then
            assert output is True

        @patch('pcapi.infrastructure.repository.stock_provider.provider_api.requests')
        def should_returns_false_when_provider_api_request_fails(self, requests):
            # Given
            requests.get = MagicMock()
            siret = '12345678912345'
            requests.get.return_value = MagicMock(status_code=400)

            # When
            output = self.provider_api.is_siret_registered(siret)

            # Then
            assert output is False

        @patch('pcapi.infrastructure.repository.stock_provider.provider_api.requests')
        def should_call_api_with_authentication_token_if_given(self, requests):
            # Given
            requests.get = MagicMock()
            siret = '12345678912345'
            self.provider_api = ProviderAPI(api_url='http://example.com/stocks', name='ProviderAPI',
                                            authentication_token="744563534")

            # When
            self.provider_api.is_siret_registered(siret)

            # Then
            requests.get.assert_called_once_with(url='http://example.com/stocks/12345678912345',
                                                 headers={'Authorization': 'Basic 744563534'})
