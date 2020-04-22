import secrets
from unittest.mock import patch, MagicMock

import pytest

from connectors.api_entreprises import ApiEntrepriseException, get_by_offerer
from tests.model_creators.generic_creators import create_offerer


class GetByOffererTest:
    @patch('connectors.api_entreprises.requests.get')
    def test_raises_ApiEntrepriseException_when_sirene_api_does_not_respond(self, requests_get):
        # Given
        requests_get.return_value = MagicMock(status_code=400)
        validation_token = secrets.token_urlsafe(20)

        offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                                 name='Accenture', validation_token=validation_token)

        # When
        with pytest.raises(ApiEntrepriseException) as error:
            get_by_offerer(offerer)

        # Then
        assert 'Error getting API entreprise DATA for SIREN' in str(error.value)

    @patch('connectors.api_entreprises.requests.get')
    def test_returns_api_response_when_sirene_api_responds(self, requests_get):
        # Given
        mocked_api_response = MagicMock(status_code=200)
        requests_get.return_value = mocked_api_response

        validation_token = secrets.token_urlsafe(20)

        offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                                 name='Accenture', validation_token=validation_token)

        # When
        response = get_by_offerer(offerer)

        # Then
        requests_get.assert_called_once_with("https://entreprise.data.gouv.fr/api/sirene/v1/siren/732075312",
                                             verify=False)
        assert response == mocked_api_response
