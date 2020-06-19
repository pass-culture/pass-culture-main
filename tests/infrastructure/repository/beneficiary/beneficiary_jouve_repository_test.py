from unittest.mock import MagicMock, call, patch

import pytest
from freezegun import freeze_time
from tests.connector_creators import jouve_creators

from domain.beneficiary.beneficiary_pre_subscription import \
    BeneficiaryPreSubscription
from infrastructure.repository.beneficiary.beneficiary_jouve_repository import (
    ApiJouveException, BeneficiaryJouveRepository)


@freeze_time('2020-10-15 09:00:00')
@patch('infrastructure.repository.beneficiary.beneficiary_jouve_repository.JOUVE_API_DOMAIN', 'https://jouve.com')
@patch('infrastructure.repository.beneficiary.beneficiary_jouve_repository.JOUVE_PASSWORD', 'secret-password')
@patch('infrastructure.repository.beneficiary.beneficiary_jouve_repository.JOUVE_USERNAME', 'username')
@patch('infrastructure.repository.beneficiary.beneficiary_jouve_repository.JOUVE_VAULT_GUID', '12')
@patch('infrastructure.repository.beneficiary.beneficiary_jouve_repository.requests.post')
def test_calls_jouve_api_with_previously_fetched_token(mocked_requests_post):
    # Given
    token = 'token-for-tests'
    application_id = '5'

    get_token_response = MagicMock(status_code=200)
    get_token_response.json = MagicMock(return_value=jouve_creators.get_token_detail_response(token))

    get_application_by_json = jouve_creators.get_application_by_detail_response(
        address='18 avenue des fleurs',
        birth_date='09/08/1995',
        city='RENNES',
        department_code='35123',
        email='rennes@example.org',
        first_name='Céline',
        gender='F',
        last_name='DURAND',
        phone_number='0123456789',
        status='Apprenti'
    )
    get_application_by_response = MagicMock(status_code=200)
    get_application_by_response.json = MagicMock(return_value=get_application_by_json)

    mocked_requests_post.side_effect = [
        get_token_response,
        get_application_by_response
    ]

    # When
    beneficiary_pre_subscription = BeneficiaryJouveRepository().get_application_by(application_id)

    # Then
    assert mocked_requests_post.call_args_list[0] == call(
        'https://jouve.com/REST/server/authenticationtokens',
        headers={'Content-Type': 'application/json'},
        json={
            'Username': 'username',
            'Password': 'secret-password',
            'VaultGuid': '12',
            'Expiration': '2020-10-15T10:00:00'
        })
    assert mocked_requests_post.call_args_list[1] == call(
        'https://jouve.com/REST/vault/extensionmethod/VEM_GetJeuneByID',
        data=application_id,
        headers={'X-Authentication': token})
    assert type(beneficiary_pre_subscription) == BeneficiaryPreSubscription
    assert beneficiary_pre_subscription.address == '18 avenue des fleurs'
    assert beneficiary_pre_subscription.birth_date == '09/08/1995'
    assert beneficiary_pre_subscription.city == 'RENNES'
    assert beneficiary_pre_subscription.department_code == '35123'
    assert beneficiary_pre_subscription.email == 'rennes@example.org'
    assert beneficiary_pre_subscription.first_name == 'Céline'
    assert beneficiary_pre_subscription.gender == 'F'
    assert beneficiary_pre_subscription.last_name == 'DURAND'
    assert beneficiary_pre_subscription.phone_number == '0123456789'
    assert beneficiary_pre_subscription.status == 'Apprenti'


@patch('infrastructure.repository.beneficiary.beneficiary_jouve_repository.requests.post')
def test_raise_exception_when_password_is_invalid(stubed_requests_post):
    # Given
    application_id = '5'
    stubed_requests_post.return_value = MagicMock(status_code=400)

    # When
    with pytest.raises(ApiJouveException) as api_jouve_exception:
        BeneficiaryJouveRepository().get_application_by(application_id)

    # Then
    assert str(api_jouve_exception.value) == 'Error getting API jouve authentication token'


@patch('infrastructure.repository.beneficiary.beneficiary_jouve_repository.requests.post')
def test_raise_exception_when_token_is_invalid(stubed_requests_post):
    # Given
    token = 'token-for-tests'
    application_id = '5'

    get_token_response = MagicMock(status_code=200)
    get_token_response.json = MagicMock(return_value=jouve_creators.get_token_detail_response(token))

    get_application_by_json = jouve_creators.get_application_by_detail_response()
    get_application_by_response = MagicMock(status_code=400)
    get_application_by_response.json = MagicMock(return_value=get_application_by_json)

    stubed_requests_post.side_effect = [
        get_token_response,
        get_application_by_response
    ]

    # When
    with pytest.raises(ApiJouveException) as api_jouve_exception:
        BeneficiaryJouveRepository().get_application_by(application_id)

    # Then
    assert str(api_jouve_exception.value) == 'Error getting API jouve GetJouveByID with id: 5'
