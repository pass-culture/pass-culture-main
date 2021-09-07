import pytest

import pcapi.core.users.factories as users_factories
from pcapi.models import UserSession

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def when_account_is_known(self, app):
        # given
        user = users_factories.BeneficiaryGrant18Factory(password="secret")
        data = {"identifier": user.email, "password": "secret"}

        # when
        response = TestClient(app.test_client()).post("/beneficiaries/signin", json=data)

        # then
        assert response.status_code == 200

    def when_account_is_known_with_mixed_case_email(self, app):
        # given
        users_factories.BeneficiaryGrant18Factory(email="USER@example.COM", password="secret")
        data = {"identifier": "uSeR@EXAmplE.cOm", "password": "secret"}

        # when
        response = TestClient(app.test_client()).post("/beneficiaries/signin", json=data)

        # then
        assert response.status_code == 200

    def when_account_is_known_with_trailing_spaces_in_email(self, app):
        # given
        users_factories.BeneficiaryGrant18Factory(email="user@example.com", password="secret")
        data = {"identifier": "  user@example.com  ", "password": "secret"}

        # when
        response = TestClient(app.test_client()).post("/beneficiaries/signin", json=data)

        # then
        assert response.status_code == 200

    def expect_a_new_user_session_to_be_recorded(self, app):
        # given
        user = users_factories.BeneficiaryGrant18Factory(password="secret")
        data = {"identifier": user.email, "password": "secret"}

        # when
        response = TestClient(app.test_client()).post("/beneficiaries/signin", json=data)

        # then
        assert response.status_code == 200
        session = UserSession.query.filter_by(userId=user.id).first()
        assert session is not None


@pytest.mark.usefixtures("db_session")
class Returns401Test:
    def when_identifier_is_missing(self, app):
        # Given
        users_factories.BeneficiaryGrant18Factory()
        data = {"identifier": None, "password": "secret"}

        # When
        response = TestClient(app.test_client()).post("/beneficiaries/signin", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["identifier"] == ["Identifiant manquant"]

    def when_identifier_is_unknown(self, app):
        # Given
        users_factories.BeneficiaryGrant18Factory()
        data = {"identifier": "unknown@example.com", "password": "password"}

        # When
        response = TestClient(app.test_client()).post("/beneficiaries/signin", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["signin"] == ["Identifiant ou mot de passe incorrect"]

    def when_password_is_missing(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory()
        data = {"identifier": user.email, "password": None}

        # When
        response = TestClient(app.test_client()).post("/beneficiaries/signin", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["password"] == ["Mot de passe manquant"]

    def when_password_is_incorrect(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory()
        data = {"identifier": user.email, "password": "wrong password"}

        # When
        response = TestClient(app.test_client()).post("/beneficiaries/signin", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["signin"] == ["Identifiant ou mot de passe incorrect"]

    def when_account_is_not_active(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(isActive=False, password="secret")
        data = {"identifier": user.email, "password": "secret"}

        # When
        response = TestClient(app.test_client()).post("/beneficiaries/signin", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["signin"] == ["Identifiant ou mot de passe incorrect"]

    def when_account_is_not_validated(self, app):
        # Given
        user = users_factories.BeneficiaryGrant18Factory(password="secret")
        user.generate_validation_token()
        data = {"identifier": user.email, "password": "secret"}

        # When
        response = TestClient(app.test_client()).post("/beneficiaries/signin", json=data)

        # Then
        assert response.status_code == 401
        assert response.json["identifier"] == ["Ce compte n'est pas validé."]
