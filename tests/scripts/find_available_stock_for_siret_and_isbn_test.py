from unittest.mock import patch, MagicMock

from scripts.find_available_stock_for_siret_and_isbn import find_available_stock_for_siret_and_isbn


class FindAvailableStockForIsbnAndSiretTest:
    @patch('connectors.api_titelive_stocks.requests.get')
    def test_should_return_negative_value_when_siret_is_not_known(self, mock_titelive_api):
        # Given
        response_return_value = MagicMock(status_code=400, text='')
        response_return_value.json = MagicMock()
        response_return_value.return_value = {}
        mock_titelive_api.return_value = response_return_value

        siret = '1234'
        isbn = '9876543211234'

        # When
        available_stock = find_available_stock_for_siret_and_isbn(siret, isbn)

        # Then
        assert available_stock == -1

    @patch('connectors.api_titelive_stocks.requests.get')
    def test_should_call_api_until_data_exhausted(self, mock_titelive_api):
        # Given
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json.side_effect = [{
            'total': 'null',
            'limit': 5000,
            'stocks': [
                {
                    "ref": "1234567865354",
                    "available": 4,
                    "price": 4500,
                    "validUntil": "2019-10-31T15:10:27Z"
                }
            ]
        },
            {
                'total': 'null',
                'limit': 5000,
                'stocks': [
                    {
                        "ref": "9876543211234",
                        "available": 10,
                        "price": 4500,
                        "validUntil": "2019-10-31T15:10:27Z"
                    }
                ]
            },
        ]
        mock_titelive_api.return_value = response_return_value

        siret = '12345678912345'
        isbn = '9876543211234'

        # When
        available_stock = find_available_stock_for_siret_and_isbn(siret, isbn)

        # Then
        assert mock_titelive_api.call_count == 2
        assert available_stock == 10

    @patch('connectors.api_titelive_stocks.requests.get')
    def test_should_return_available_stock_from_api_data(self, mock_titelive_api):
        # Given
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json.return_value = {
            'total': 'null',
            'limit': 5000,
            'stocks': [
                {
                    "ref": "9876543211234",
                    "available": 4,
                    "price": 4500,
                    "validUntil": "2019-10-31T15:10:27Z"
                }
            ]
        }
        mock_titelive_api.return_value = response_return_value

        siret = '12345678912345'
        isbn = '9876543211234'

        # When
        available_stock = find_available_stock_for_siret_and_isbn(siret, isbn)

        # Then
        assert available_stock == 4
