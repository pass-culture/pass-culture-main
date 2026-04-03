import datetime
import decimal

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="auth_client")
def auth_client_fixture(app, settings):
    settings.E2E_API_KEY = "secret"
    _client = TestClient(app.test_client())
    _client.auth_header = {"x-api-key": settings.E2E_API_KEY}
    return _client


class E2EAccountTest:
    def test_create_account_unauthorized(self, client):
        response = client.post("/e2e/account", {"step": "EMAIL_VALIDATION", "id_provider": "UBBLE"})
        assert response.status_code == 401

    def test_create_account_forbidden(self, client, settings):
        settings.E2E_API_KEY = "titi"
        response = client.post("/e2e/account", json={}, headers={"x-api-key": "toto"})
        assert response.status_code == 403

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

    def test_create_account_with_birthdate(self, auth_client):
        birthdate = datetime.date.today() - relativedelta(years=18)
        birthdate_str = f"{birthdate:%Y-%m-%d}"
        response = auth_client.post(
            "/e2e/account", {"birthdate": birthdate_str, "step": "BENEFICIARY", "id_provider": "UBBLE"}
        )
        assert response.status_code == 200

        users = db.session.query(users_models.User).all()
        assert len(users) == 1
        user = users[0]
        assert user.is_beneficiary
        assert response.json["id"] == user.id

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
        assert response.status_code == 403

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
        response = client.post(
            f"/e2e/account/{user.id}/quotient_familial", {"step": "EMAIL_VALIDATION", "id_provider": "UBBLE"}
        )
        assert response.status_code == 401

    def test_configure_account_qf_forbidden(self, client, settings):
        settings.E2E_API_KEY = "titi"
        user = users_factories.BeneficiaryFactory()
        response = client.post(f"/e2e/account/{user.id}/quotient_familial", json={}, headers={"x-api-key": "toto"})
        assert response.status_code == 403

    def test_configure_account_qf(self, auth_client):
        user = users_factories.BeneficiaryFactory()
        response = auth_client.post(
            f"/e2e/account/{user.id}/quotient_familial",
            json={
                "first_names": ["Pierre", "Paul"],
                "gender": "M.",
                "https_status_code": 200,
                "last_name": "Jean",
                "quotient_familial_value": 700,
                "birth_date": "2020-01-01",
            },
        )
        assert response.status_code == 200, response.json
