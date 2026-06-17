import datetime
import decimal

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db


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
        response = client.post(f"/e2e/account/{user.id}/aah", json={"mock_type": "BENEFICIARY"})
        assert response.status_code == 401

    def test_configure_account_aah_forbidden(self, client, settings):
        settings.E2E_API_KEY = "titi"
        user = users_factories.BeneficiaryFactory()
        response = client.post(
            f"/e2e/account/{user.id}/aah", json={"mock_type": "BENEFICIARY"}, headers={"x-api-key": "toto"}
        )
        assert response.status_code == 401

    def test_configure_account_aah(self, auth_client):
        user = users_factories.BeneficiaryFactory()
        response = auth_client.post(f"/e2e/account/{user.id}/aah", json={"mock_type": "BENEFICIARY"})
        assert response.status_code == 200, response.json


class E2EAccountAEEHConfigTest:
    def test_configure_account_aeeh_unauthorized(self, client):
        user = users_factories.BeneficiaryFactory()
        response = client.post(f"/e2e/account/{user.id}/aeeh", json={"mock_type": "BENEFICIARY"})
        assert response.status_code == 401

    def test_configure_account_aeeh_forbidden(self, client, settings):
        settings.E2E_API_KEY = "titi"
        user = users_factories.BeneficiaryFactory()
        response = client.post(
            f"/e2e/account/{user.id}/aeeh", json={"mock_type": "BENEFICIARY"}, headers={"x-api-key": "toto"}
        )
        assert response.status_code == 401

    def test_configure_account_aeeh(self, auth_client):
        user = users_factories.BeneficiaryFactory()
        response = auth_client.post(f"/e2e/account/{user.id}/aeeh", json={"mock_type": "BENEFICIARY"})
        assert response.status_code == 200, response.json
