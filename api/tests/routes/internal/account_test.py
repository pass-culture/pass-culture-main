import datetime
import decimal
from unittest.mock import call
from unittest.mock import patch

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


class E2EAccountTest:
    def test_create_account_unauthorized(self, client):
        response = client.post("/e2e/account", {"step": "EMAIL_VALIDATION", "id_provider": "UBBLE"})
        assert response.status_code == 401

    def test_create_account_forbidden(self, client, settings):
        settings.E2E_API_KEY = "titi"
        response = client.post("/e2e/account", json={}, headers={"x-api-key": "toto"})
        assert response.status_code == 401

    def test_create_account(self, auth_client):
        """
        Response format:
        {
            "id": <user_id>,
            "email": "first_name.last_name.<user_id>@passculture.gen",
            "access_token": <token>,
            "expiration_timestamp": <token_expiration_timestamp>,
        }
        """
        response = auth_client.post("/e2e/account", {"age": 18, "step": "BENEFICIARY", "id_provider": "UBBLE"})
        assert response.status_code == 200

        users = db.session.query(users_models.User).all()
        assert len(users) == 1
        user = users[0]
        assert user.is_beneficiary
        assert response.json["id"] == user.id
        assert response.json["email"] == user.email
        assert "access_token" in response.json
        assert "expiration_timestamp" in response.json

    def test_create_account_with_birth_date(self, auth_client):
        birth_date = datetime.date.today() - relativedelta(years=18)
        birth_date_str = f"{birth_date:%Y-%m-%d}"
        response = auth_client.post(
            "/e2e/account", {"birth_date": birth_date_str, "step": "BENEFICIARY", "id_provider": "UBBLE"}
        )
        assert response.status_code == 200

        users = db.session.query(users_models.User).all()
        assert len(users) == 1
        user = users[0]
        assert user.is_beneficiary
        assert response.json["id"] == user.id
        assert user.age == 18
        assert user.dateOfBirth.date() == birth_date

    def test_create_account_with_credit(self, auth_client):
        response = auth_client.post(
            "/e2e/account",
            {"age": 18, "step": "BENEFICIARY", "id_provider": "UBBLE", "credit": decimal.Decimal("34.7")},
        )
        assert response.status_code == 200

        users = db.session.query(users_models.User).all()
        assert len(users) == 1
        user = users[0]
        assert user.is_beneficiary
        assert response.json["id"] == user.id
        assert user.deposit.amount == decimal.Decimal("34.7")


class E2EAccountUbbleConfigTest:
    def test_configure_account_ubble_unauthorized(self, client):
        user = users_factories.ProfileCompletedUserFactory()
        response = client.post(f"/e2e/account/{user.id}/ubble", {"step": "EMAIL_VALIDATION", "id_provider": "UBBLE"})
        assert response.status_code == 401

    def test_configure_account_ubble_forbidden(self, client, settings):
        settings.E2E_API_KEY = "titi"
        user = users_factories.ProfileCompletedUserFactory()
        response = client.post(f"/e2e/account/{user.id}/ubble", json={}, headers={"x-api-key": "toto"})
        assert response.status_code == 401

    def test_configure_account_ubble(self, auth_client):
        user = users_factories.ProfileCompletedUserFactory()
        response = auth_client.post(
            f"/e2e/account/{user.id}/ubble",
            json={
                "final_response_code": 10000,
                "id_document_number": "ABCD1234",
                "birth_date": "2020-01-01",
            },
        )
        assert response.status_code == 200, response.json


class E2EAccountQFConfigTest:
    def test_configure_account_qf_unauthorized(self, client):
        user = users_factories.BeneficiaryFactory()
        response = client.post(f"/e2e/account/{user.id}/quotient_familial", json={"mock_type": "OK"})
        assert response.status_code == 401

    def test_configure_account_qf_forbidden(self, client, settings):
        settings.E2E_API_KEY = "titi"
        user = users_factories.BeneficiaryFactory()
        response = client.post(
            f"/e2e/account/{user.id}/quotient_familial", json={"mock_type": "OK"}, headers={"x-api-key": "toto"}
        )
        assert response.status_code == 401

    def test_configure_account_qf(self, auth_client):
        user = users_factories.BeneficiaryFactory()
        response = auth_client.post(f"/e2e/account/{user.id}/quotient_familial", json={"mock_type": "OK"})
        assert response.status_code == 200, response.json


class E2EAccountAAHConfigTest:
    def test_configure_account_aah_unauthorized(self, client):
        user = users_factories.BeneficiaryFactory()
        response = client.post(f"/e2e/account/{user.id}/aah", json={"mock_type": "RECIPIENT"})
        assert response.status_code == 401

    def test_configure_account_aah_forbidden(self, client, settings):
        settings.E2E_API_KEY = "titi"
        user = users_factories.BeneficiaryFactory()
        response = client.post(
            f"/e2e/account/{user.id}/aah", json={"mock_type": "RECIPIENT"}, headers={"x-api-key": "toto"}
        )
        assert response.status_code == 401

    def test_configure_account_aah(self, auth_client):
        user = users_factories.BeneficiaryFactory()
        response = auth_client.post(f"/e2e/account/{user.id}/aah", json={"mock_type": "RECIPIENT"})
        assert response.status_code == 200, response.json


class E2EAccountAEEHConfigTest:
    def test_configure_account_aeeh_unauthorized(self, client):
        user = users_factories.BeneficiaryFactory()
        response = client.post(f"/e2e/account/{user.id}/aeeh", json={"mock_type": "RECIPIENT"})
        assert response.status_code == 401

    def test_configure_account_aeeh_forbidden(self, client, settings):
        settings.E2E_API_KEY = "titi"
        user = users_factories.BeneficiaryFactory()
        response = client.post(
            f"/e2e/account/{user.id}/aeeh", json={"mock_type": "RECIPIENT"}, headers={"x-api-key": "toto"}
        )
        assert response.status_code == 401

    def test_configure_account_aeeh(self, auth_client):
        user = users_factories.BeneficiaryFactory()
        response = auth_client.post(f"/e2e/account/{user.id}/aeeh", json={"mock_type": "RECIPIENT"})
        assert response.status_code == 200, response.json


class E2EAccountBonusCreditRecoveryTest:
    def test_recover_started_bonus_credit_applications_unauthorized(self, client):
        response = client.post("/e2e/bonus_credit/1/recover")

        assert response.status_code == 401

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_quotient_familial_bonus_task.delay")
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_adult_disability_bonus_task.delay")
    @patch("pcapi.core.subscription.bonus.tasks.apply_for_disabled_child_education_bonus_task.delay")
    def test_recover_started_bonus_credit_applications_full_page(
        self, mocked_apply_for_aeeh_task, mocked_apply_for_aah_task, mocked_apply_for_qf_task, auth_client
    ):
        user = users_factories.BeneficiaryFactory()
        next_year = date_utils.get_naive_utc_now() + relativedelta(years=1)
        started_fraud_check_1 = subscription_factories.QFBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, user=user, resultContent={"next_retry_at": next_year}
        )
        started_fraud_check_2 = subscription_factories.QFBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, user=user, resultContent={"next_retry_at": next_year}
        )
        aah_fraud_check = subscription_factories.AAHBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, user=user, resultContent={"next_retry_at": next_year}
        )
        aeeh_fraud_check = subscription_factories.AEEHBonusCreditFraudCheckFactory.create(
            status=subscription_models.FraudCheckStatus.STARTED, user=user, resultContent={"next_retry_at": next_year}
        )

        response = auth_client.post(f"/e2e/bonus_credit/{user.id}/recover")

        assert response.status_code == 200
        assert response.json == {
            "aah_bonus_credit": [aah_fraud_check.id],
            "aeeh_bonus_credit": [aeeh_fraud_check.id],
            "qf_bonus_credit": [started_fraud_check_1.id, started_fraud_check_2.id],
        } or response.json == {
            "aah_bonus_credit": [aah_fraud_check.id],
            "aeeh_bonus_credit": [aeeh_fraud_check.id],
            "qf_bonus_credit": [started_fraud_check_2.id, started_fraud_check_1.id],
        }

        mocked_apply_for_qf_task.assert_has_calls(
            [
                call(payload={"fraud_check_id": started_fraud_check_1.id}),
                call(payload={"fraud_check_id": started_fraud_check_2.id}),
            ],
            any_order=True,
        )
        mocked_apply_for_aah_task.assert_has_calls([call(payload={"fraud_check_id": aah_fraud_check.id})])
        mocked_apply_for_aeeh_task.assert_has_calls([call(payload={"fraud_check_id": aeeh_fraud_check.id})])
