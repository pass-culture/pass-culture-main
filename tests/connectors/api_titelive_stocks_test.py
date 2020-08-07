from unittest.mock import patch, MagicMock

import pytest

from connectors.api_titelive_stocks import get_titelive_stocks, ApiTiteLiveException, is_siret_registered


class GetTiteLiveStocksTest:
    @patch('connectors.api_titelive_stocks.requests.get')
    def should_call_titelive_api_with_siret_parameter(self, requests_get):
        # Given
        siret = '123456789123'

        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json = MagicMock()
        response_return_value.return_value = {
            'total': 'null',
            'limit': 5000,
            'stocks': [
                {
                    "ref": "0002730757438",
                    "available": 0,
                    "price": 4500,
                    "validUntil": "2019-10-31T15:10:27Z"
                }
            ]
        }
        requests_get.return_value = response_return_value

        # When
        get_titelive_stocks(siret)

        # Then
        requests_get.assert_called_once_with('https://stock.epagine.fr/stocks/123456789123', params={})

    @patch('connectors.api_titelive_stocks.requests.get')
    def should_call_titelive_api_with_modified_since_parameter_when_given(self, requests_get):
        # Given
        siret = '123456789123'

        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json = MagicMock()
        response_return_value.return_value = {
            'total': 'null',
            'limit': 5000,
            'stocks': [
                {
                    "ref": "0002730757438",
                    "available": 0,
                    "price": 4500,
                    "validUntil": "2019-10-31T15:10:27Z"
                }
            ]
        }
        requests_get.return_value = response_return_value
        modified_since = '2020-08-27T09:15:32Z'

        # When
        get_titelive_stocks(siret, modified_since=modified_since)

        # Then
        requests_get.assert_called_once_with('https://stock.epagine.fr/stocks/123456789123', params={'modifiedSince': modified_since})

    @patch('connectors.api_titelive_stocks.requests.get')
    def should_call_titelive_api_with_siret_and_last_processed_isbn_to_call_next_api_page(self,
                                                                                               requests_get):
        # Given
        siret = '123456789123'
        last_processed_isbn = '9876543214567'

        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json = MagicMock()
        response_return_value.return_value = {
            'total': 'null',
            'limit': 5000,
            'stocks': [
                {
                    "ref": "0002730757438",
                    "available": 0,
                    "price": 4500,
                    "validUntil": "2019-10-31T15:10:27Z"
                }
            ]
        }
        requests_get.return_value = response_return_value

        # When
        get_titelive_stocks(siret, last_processed_isbn)

        # Then
        requests_get.assert_called_once_with('https://stock.epagine.fr/stocks/123456789123', params={'after': '9876543214567'})

    @patch('connectors.api_titelive_stocks.requests.get')
    def should_raise_error_when_request_fails(self, requests_get):
        # Given
        siret = '123456789123'
        last_processed_isbn = '9876543214567'

        response_return_value = MagicMock(status_code=400, text='')
        response_return_value.json = MagicMock()
        response_return_value.return_value = {}
        requests_get.return_value = response_return_value

        # When / Then
        with pytest.raises(ApiTiteLiveException) as exception:
            get_titelive_stocks(siret, last_processed_isbn)

        # Then
        assert str(exception.value) == 'Error 400 when getting TiteLive stocks for siret: 123456789123'


class  IsSiretRegisteredTest:
    @patch('connectors.api_titelive_stocks.requests.get')
    def should_call_titelive_api_with_given_siret(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        mock_requests_get.return_value = MagicMock(status_code=200)

        # When
        is_siret_registered(siret)

        # Then
        mock_requests_get.assert_called_once_with(
            'https://stock.epagine.fr/stocks/12345678912345')

    @patch('connectors.api_titelive_stocks.requests.get')
    def should_returns_true_if_api_returns_200(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        mock_requests_get.return_value = MagicMock(status_code=200)

        # When
        output = is_siret_registered(siret)

        # Then
        assert output == True

    @patch('connectors.api_titelive_stocks.requests.get')
    def should_returns_false_when_libraires_api_request_fails(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        mock_requests_get.return_value = MagicMock(status_code=400)

        # When
        output = is_siret_registered(siret)

        # Then
        assert output == False
