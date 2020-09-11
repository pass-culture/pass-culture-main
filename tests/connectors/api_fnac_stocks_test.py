from unittest.mock import MagicMock, patch

import pytest

from connectors.api_fnac_stocks import ApiFnacException, get_stocks_from_fnac_api, is_siret_registered


class GetStocksFromFNACApiTest:
    @patch('connectors.api_fnac_stocks.requests.get')
    def test_should_raise_error_when_fnac_api_request_fails(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        mock_requests_get.return_value = MagicMock(status_code=400)

        # When
        with pytest.raises(ApiFnacException) as exception:
            get_stocks_from_fnac_api(siret)

        # Then
        assert str(exception.value) == 'Error 400 when getting Fnac stocks for SIRET: 12345678912345'

    @patch.dict('os.environ', {"PROVIDER_FNAC_BASIC_AUTHENTICATION_TOKEN": '6666'})
    @patch('connectors.api_fnac_stocks.requests.get')
    def test_should_call_fnac_api_with_given_siret(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        mock_requests_get.return_value = MagicMock(status_code=200)

        # When
        get_stocks_from_fnac_api(siret)

        # Then
        mock_requests_get.assert_called_once_with(
            'https://passculture-fr.ws.fnac.com/api/v1/pass-culture/stocks/12345678912345',
            headers={'Authorization': f'Basic 6666'},
            params={'limit': '1000'}
        )

    @patch.dict('os.environ', {"PROVIDER_FNAC_BASIC_AUTHENTICATION_TOKEN": '6666'})
    @patch('connectors.api_fnac_stocks.requests.get')
    def test_should_call_fnac_api_with_given_siret_and_last_processed_isbn(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        last_processed_isbn = '9780199536986'
        modified_since = ''
        mock_requests_get.return_value = MagicMock(status_code=200)

        # When
        get_stocks_from_fnac_api(siret, last_processed_isbn, modified_since)

        # Then
        mock_requests_get.assert_called_once_with(
            'https://passculture-fr.ws.fnac.com/api/v1/pass-culture/stocks/12345678912345',
            headers={'Authorization': f'Basic 6666'},
            params={
                'limit': '1000',
                'after': last_processed_isbn
            })

    @patch.dict('os.environ', {"PROVIDER_FNAC_BASIC_AUTHENTICATION_TOKEN": '6666'})
    @patch('connectors.api_fnac_stocks.requests.get')
    def test_should_call_fnac_api_with_given_siret_and_last_modification_date(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        last_processed_isbn = ''
        modified_since = '2019-12-16T00:00:00'
        mock_requests_get.return_value = MagicMock(status_code=200)

        # When
        get_stocks_from_fnac_api(siret, last_processed_isbn, modified_since)

        # Then
        mock_requests_get.assert_called_once_with(
            'https://passculture-fr.ws.fnac.com/api/v1/pass-culture/stocks/12345678912345',
            headers={'Authorization': f'Basic 6666'},
            params={
                'limit': '1000',
                'modifiedSince': modified_since
            })

    @patch.dict('os.environ', {"PROVIDER_FNAC_BASIC_AUTHENTICATION_TOKEN": '6666'})
    @patch('connectors.api_fnac_stocks.requests.get')
    def test_should_call_fnac_api_with_given_all_parameters(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        last_processed_isbn = '9780199536986'
        modified_since = '2019-12-16T00:00:00'
        mock_requests_get.return_value = MagicMock(status_code=200)

        # When
        get_stocks_from_fnac_api(siret, last_processed_isbn, modified_since)

        # Then
        mock_requests_get.assert_called_once_with(
            'https://passculture-fr.ws.fnac.com/api/v1/pass-culture/stocks/12345678912345',
            headers={'Authorization': f'Basic 6666'},
            params={
                'limit': '1000',
                'after': last_processed_isbn,
                'modifiedSince': modified_since
            })

    @patch.dict('os.environ', {"PROVIDER_FNAC_BASIC_AUTHENTICATION_TOKEN": '6666'})
    @patch('connectors.api_fnac_stocks.requests.get')
    def test_should_return_payload_when_status_code_equals_204(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        last_processed_isbn = '9780199536986'
        modified_since = '2019-12-16T00:00:00'
        mock_requests_get.return_value = MagicMock(status_code=204)

        # When
        result = get_stocks_from_fnac_api(siret, last_processed_isbn, modified_since)

        # Then
        assert result == {
            'Stocks': []
        }


class IsSiretRegisteredTest:
    @patch.dict('os.environ', {"PROVIDER_FNAC_BASIC_AUTHENTICATION_TOKEN": '6666'})
    @patch('connectors.api_fnac_stocks.requests.get')
    def test_should_call_fnac_api_with_given_siret(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        mock_requests_get.return_value = MagicMock(status_code=200)

        # When
        is_siret_registered(siret)

        # Then
        mock_requests_get.assert_called_once_with(
            'https://passculture-fr.ws.fnac.com/api/v1/pass-culture/stocks/12345678912345',
            headers={'Authorization': f'Basic 6666'},
        )

    @patch('connectors.api_fnac_stocks.requests.get')
    def test_should_returns_true_if_api_returns_200(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        mock_requests_get.return_value = MagicMock(status_code=200)

        # When
        output = is_siret_registered(siret)

        # Then
        assert output is True

    @patch('connectors.api_fnac_stocks.requests.get')
    def test_should_returns_false_when_fnac_api_request_fails(self, mock_requests_get):
        # Given
        siret = '12345678912345'
        mock_requests_get.return_value = MagicMock(status_code=400)

        # When
        output = is_siret_registered(siret)

        # Then
        assert output is False
