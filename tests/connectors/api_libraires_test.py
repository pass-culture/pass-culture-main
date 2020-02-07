from unittest.mock import patch, MagicMock

import pytest

from connectors.api_libraires import ApiLibrairesException, get_stocks_from_libraires_api


class GetStocksFromLibrairesApiTest:
    @patch('connectors.api_libraires.requests.get')
    def test_should_raise_error_when_libraires_api_request_fails(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        response_return_value = MagicMock(status_code=400, text='', return_value={})
        mock_requests_get.return_value = response_return_value

        # When
        with pytest.raises(ApiLibrairesException) as exception:
            get_stocks_from_libraires_api(siret)

        # Then
        assert str(exception.value) == 'Error getting Libraires stocks for siret: 12345678912345'

    @patch('connectors.api_libraires.requests.get')
    def test_should_call_libraires_api_with_given_siret(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.return_value = {
            "total": 2,
            "limit": 20,
            "offset": 0,
            "stocks": [
                {
                    "ref": "0000001428056",
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

        mock_requests_get.return_value = response_return_value

        # When
        get_stocks_from_libraires_api(siret)

        # Then
        mock_requests_get.assert_called_once_with(
            'https://passculture.leslibraires.fr/stocks/12345678912345?limit=1000')

    @patch('connectors.api_libraires.requests.get')
    def test_should_call_libraires_api_with_given_siret_and_last_processed_isbn(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        last_processed_isbn = '9780199536986'
        modified_since = ''
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.return_value = {
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

        mock_requests_get.return_value = response_return_value

        # When
        get_stocks_from_libraires_api(siret, last_processed_isbn, modified_since)

        # Then
        mock_requests_get.assert_called_once_with(
            'https://passculture.leslibraires.fr/stocks/12345678912345?limit=1000&after=9780199536986')

    @patch('connectors.api_libraires.requests.get')
    def test_should_call_libraires_api_with_given_siret_and_last_modification_date(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        last_processed_isbn = ''
        modified_since = '2019-12-16T00:00:00'
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.return_value = {
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

        mock_requests_get.return_value = response_return_value

        # When
        get_stocks_from_libraires_api(siret, last_processed_isbn, modified_since)

        # Then
        mock_requests_get.assert_called_once_with(
            'https://passculture.leslibraires.fr/stocks/12345678912345?limit=1000&modifiedSince=2019-12-16T00:00:00')

    @patch('connectors.api_libraires.requests.get')
    def test_should_call_libraires_api_with_given_all_parameters(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        last_processed_isbn = '9780199536986'
        modified_since = '2019-12-16T00:00:00'
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.return_value = {
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

        mock_requests_get.return_value = response_return_value

        # When
        get_stocks_from_libraires_api(siret, last_processed_isbn, modified_since)

        # Then
        mock_requests_get.assert_called_once_with(
            'https://passculture.leslibraires.fr/stocks/12345678912345?limit=1000&after=9780199536986&modifiedSince=2019-12-16T00:00:00')
