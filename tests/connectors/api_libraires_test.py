from unittest.mock import MagicMock

import pytest
import requests

from connectors.api_libraires import ApiLibrairesStocks
from connectors.api_local_provider import ApiLocalProviderException


class GetStocksFromLibrairesApiTest:
    def setup_method(self):
        requests.get = MagicMock()
        self.api = ApiLibrairesStocks(api_url='https://passculture.leslibraires.fr/stocks', name='Libraires')

    def should_raise_error_when_libraires_api_request_fails(self):
        # Given
        siret = '12345678912345'
        requests.get.return_value = MagicMock(status_code=400)

        # When
        with pytest.raises(ApiLocalProviderException) as exception:
            self.api.get_stocks_from_local_provider_api(siret)

        # Then
        assert str(exception.value) == 'Error 400 when getting Libraires stocks for SIRET: 12345678912345'

    def should_call_libraires_api_with_given_siret(self):
        # Given
        siret = '12345678912345'
        requests.get.return_value = MagicMock(status_code=200)

        # When
        self.api.get_stocks_from_local_provider_api(siret)

        # Then
        requests.get.assert_called_once_with(
            'https://passculture.leslibraires.fr/stocks/12345678912345', params={'limit': '1000'})

    def should_call_libraires_api_with_given_siret_and_last_processed_isbn(self):
        # Given
        siret = '12345678912345'
        last_processed_isbn = '9780199536986'
        modified_since = ''
        requests.get.return_value = MagicMock(status_code=200)

        # When
        self.api.get_stocks_from_local_provider_api(siret, last_processed_isbn, modified_since)

        # Then
        requests.get.assert_called_once_with('https://passculture.leslibraires.fr/stocks/12345678912345',
                                             params={
                                                 'limit': '1000',
                                                 'after': last_processed_isbn
                                             })

    def should_call_libraires_api_with_given_siret_and_last_modification_date(self):
        # Given
        siret = '12345678912345'
        last_processed_isbn = ''
        modified_since = '2019-12-16T00:00:00'
        requests.get.return_value = MagicMock(status_code=200)

        # When
        self.api.get_stocks_from_local_provider_api(siret, last_processed_isbn, modified_since)

        # Then
        requests.get.assert_called_once_with('https://passculture.leslibraires.fr/stocks/12345678912345',
                                             params={
                                                 'limit': '1000',
                                                 'modifiedSince': modified_since
                                             })

    def should_call_libraires_api_with_given_all_parameters(self):
        # Given
        siret = '12345678912345'
        last_processed_isbn = '9780199536986'
        modified_since = '2019-12-16T00:00:00'
        requests.get.return_value = MagicMock(status_code=200)

        # When
        self.api.get_stocks_from_local_provider_api(siret, last_processed_isbn, modified_since)

        # Then
        requests.get.assert_called_once_with('https://passculture.leslibraires.fr/stocks/12345678912345',
                                             params={
                                                 'limit': '1000',
                                                 'after': last_processed_isbn,
                                                 'modifiedSince': modified_since
                                             })


class IsSiretRegisteredTest:
    def setup_method(self):
        requests.get = MagicMock()
        self.api = ApiLibrairesStocks(api_url='https://passculture.leslibraires.fr/stocks', name='Libraires')

    def should_call_libraires_api_with_given_siret(self):
        # Given
        siret = '12345678912345'
        requests.get.return_value = MagicMock(status_code=200)

        # When
        self.api.is_siret_registered(siret)

        # Then
        requests.get.assert_called_once_with('https://passculture.leslibraires.fr/stocks/12345678912345')

    def should_returns_true_if_api_returns_200(self):
        # Given
        siret = '12345678912345'
        requests.get.return_value = MagicMock(status_code=200)

        # When
        output = self.api.is_siret_registered(siret)

        # Then
        assert output is True

    def should_returns_false_when_libraires_api_request_fails(self):
        # Given
        siret = '12345678912345'
        requests.get.return_value = MagicMock(status_code=400)

        # When
        output = self.api.is_siret_registered(siret)

        # Then
        assert output is False
