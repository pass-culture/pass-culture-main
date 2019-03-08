import secrets
from unittest.mock import patch, MagicMock

import pytest

from connectors.api_entreprises import ApiEntrepriseException, get_by_offerer
from tests.test_utils import create_offerer


@pytest.mark.standalone
@patch('connectors.api_entreprises.requests.get')
def test_write_object_validation_email_raises_ApiEntrepriseException_when_siren_api_does_not_respond(requests_get):
    # Given
    requests_get.return_value = MagicMock(status_code=400)
    validation_token = secrets.token_urlsafe(20)

    offerer = create_offerer(siren='732075312', address='122 AVENUE DE FRANCE', city='Paris', postal_code='75013',
                             name='Accenture', validation_token=validation_token)

    #When
    with pytest.raises(ApiEntrepriseException) as error:
        get_by_offerer(offerer)

    #Then
    assert 'Error getting API entreprise DATA for SIREN' in str(error)