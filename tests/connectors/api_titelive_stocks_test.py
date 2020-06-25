from unittest.mock import patch, MagicMock

import pytest

from connectors.api_titelive_stocks import get_titelive_stocks, ApiTiteLiveException


class GetTiteLiveStocksTest:
    @patch('connectors.api_titelive_stocks.requests.get')
    def test_should_call_titelive_api_with_siret_parameter(self, requests_get):
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
        requests_get.assert_called_once_with('https://stock.epagine.fr/stocks/123456789123')

    @patch('connectors.api_titelive_stocks.requests.get')
    def test_should_call_titelive_api_with_siret_and_last_processed_isbn_to_call_next_api_page(self,
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
        requests_get.assert_called_once_with('https://stock.epagine.fr/stocks/123456789123?after=9876543214567')

    @patch('connectors.api_titelive_stocks.requests.get')
    def test_should_raise_error_when_request_fails(self, requests_get):
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
