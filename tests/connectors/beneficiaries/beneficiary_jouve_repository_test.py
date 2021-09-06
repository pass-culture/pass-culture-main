from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.connectors.beneficiaries.jouve_backend import ApiJouveException
from pcapi.connectors.beneficiaries.jouve_backend import get_application_content
from pcapi.connectors.beneficiaries.jouve_backend import get_subscription_from_content
from pcapi.domain.beneficiary_pre_subscription.model import BeneficiaryPreSubscription


# Required by the feature flag...
pytestmark = pytest.mark.usefixtures("db_session")


def get_application_by_detail_response(application_id: int = 2, birth_date: str = "19/08/1995", **kwargs) -> dict:
    return {
        "id": application_id,
        "birthDateTxt": birth_date,
        "registrationDate": "04/06/2020 06:00",
        "address": "18 avenue des fleurs",
        "city": "RENNES",
        "email": "rennes@example.org",
        "firstName": "Céline",
        "gender": "F",
        "lastName": "DURAND",
        "postalCode": "35123",
        "phoneNumber": "0123456789",
        "activity": "Apprenti",
        "birthLocationCtrl": "OK",
        "posteCodeCtrl": "OK",
        "serviceCodeCtrl": "OK",
        "creatorCtrl": "OK",
        "bodyBirthDateLevel": "100",
        "bodyNameLevel": "50",
        "bodyPieceNumber": "id-piece-number",
        **kwargs,
    }


def get_token_detail_response(token: str) -> dict:
    return {"Value": token}


class JouveBackendTest:
    @freeze_time("2020-10-15 09:00:00")
    @patch("pcapi.settings.JOUVE_API_DOMAIN", "https://jouve.com")
    @patch("pcapi.settings.JOUVE_API_PASSWORD", "secret-password")
    @patch("pcapi.settings.JOUVE_API_USERNAME", "username")
    @patch("pcapi.settings.JOUVE_API_VAULT_GUID", "12")
    @patch("pcapi.settings.IS_PROD", True)
    @patch("pcapi.connectors.beneficiaries.jouve_backend.requests.post")
    def test_calls_jouve_api_with_previously_fetched_token(self, mocked_requests_post):
        # Given
        token = "token-for-tests"
        application_id = 5

        get_token_response = MagicMock(status_code=200)
        get_token_response.json = MagicMock(return_value=get_token_detail_response(token))

        get_application_by_json = get_application_by_detail_response(
            application_id=application_id,
            birth_date="24/08/1995",
        )
        get_application_by_response = MagicMock(status_code=200)
        get_application_by_response.json = MagicMock(return_value=get_application_by_json)

        mocked_requests_post.side_effect = [get_token_response, get_application_by_response]

        # When
        jouve_content = get_application_content(application_id)
        beneficiary_pre_subscription = get_subscription_from_content(jouve_content)

        # Then
        assert mocked_requests_post.call_args_list[0] == call(
            "https://jouve.com/REST/server/authenticationtokens",
            headers={"Content-Type": "application/json"},
            json={
                "Username": "username",
                "Password": "secret-password",
                "VaultGuid": "12",
                "Expiration": "2020-10-15T10:00:00",
            },
        )
        assert mocked_requests_post.call_args_list[1] == call(
            "https://jouve.com/REST/vault/extensionmethod/VEM_GetJeuneByID",
            data=str(application_id),
            headers={"X-Authentication": token},
        )
        assert isinstance(beneficiary_pre_subscription, BeneficiaryPreSubscription)
        assert beneficiary_pre_subscription.activity == "Apprenti"
        assert beneficiary_pre_subscription.address == "18 avenue des fleurs"
        assert beneficiary_pre_subscription.application_id == 5
        assert beneficiary_pre_subscription.city == "RENNES"
        assert beneficiary_pre_subscription.civility == "Mme"
        assert beneficiary_pre_subscription.date_of_birth.date() == datetime(1995, 8, 24).date()
        assert beneficiary_pre_subscription.department_code == "35"
        assert beneficiary_pre_subscription.email == "rennes@example.org"
        assert beneficiary_pre_subscription.first_name == "Céline"
        assert beneficiary_pre_subscription.last_name == "DURAND"
        assert beneficiary_pre_subscription.phone_number == "0123456789"
        assert beneficiary_pre_subscription.postal_code == "35123"
        assert beneficiary_pre_subscription.public_name == "Céline DURAND"
        assert beneficiary_pre_subscription.id_piece_number == "id-piece-number"

    @patch("pcapi.connectors.beneficiaries.jouve_backend.requests.post")
    def test_raise_exception_when_password_is_invalid(self, stubed_requests_post):
        # Given
        application_id = "5"
        stubed_requests_post.return_value = MagicMock(status_code=400)

        # When
        with pytest.raises(ApiJouveException) as api_jouve_exception:
            get_application_content(application_id)

        # Then
        assert str(api_jouve_exception.value.message) == "Error getting API Jouve authentication token"
        assert api_jouve_exception.value.route == "/REST/server/authenticationtokens"
        assert api_jouve_exception.value.status_code == 400

    @patch("pcapi.connectors.beneficiaries.jouve_backend.requests.post")
    def test_raise_exception_when_token_is_invalid(self, stubed_requests_post):
        # Given
        token = "token-for-tests"
        application_id = "5"

        get_token_response = MagicMock(status_code=200)
        get_token_response.json = MagicMock(return_value=get_token_detail_response(token))

        get_application_by_json = get_application_by_detail_response()
        get_application_by_response = MagicMock(status_code=500)
        get_application_by_response.json = MagicMock(return_value=get_application_by_json)

        stubed_requests_post.side_effect = [get_token_response, get_application_by_response]

        # When
        with pytest.raises(ApiJouveException) as api_jouve_exception:
            get_application_content(application_id)

        # Then
        assert str(api_jouve_exception.value.message) == "Error getting API jouve GetJeuneByID"
        assert api_jouve_exception.value.route == "/REST/vault/extensionmethod/VEM_GetJeuneByID"
        assert api_jouve_exception.value.status_code == 500

    @pytest.mark.parametrize("jouve_field", ["birthLocationCtrl", "bodyBirthDateCtrl", "bodyNameCtrl"])
    @pytest.mark.parametrize("wrong_possible_value", ["NOT_APPLICABLE", "KO"])
    @patch("pcapi.connectors.beneficiaries.jouve_backend._get_raw_content")
    def test_jouve_response_with_wrong_values_are_supiscious(self, _get_raw_content, jouve_field, wrong_possible_value):
        response_data = get_application_by_detail_response()
        response_data[jouve_field] = wrong_possible_value
        _get_raw_content.return_value = response_data

        jouve_content = get_application_content("fake-application-id")
        pre_subscription = get_subscription_from_content(jouve_content)
        item_found = False
        for item in pre_subscription.fraud_fields["non_blocking_controls"]:
            if item.key == jouve_field:
                assert item.valid == False
                item_found = True

        assert item_found
