from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.testing import override_features
from pcapi.core.users.models import User
from pcapi.notifications.push import testing as push_testing
from pcapi.routes.serialization import serialize

from tests.conftest import TestClient


BASE_DATA = {
    "email": "toto@example.com",
    "firstName": "Toto",
    "lastName": "Martin",
    "postalCode": "93100",
    "publicName": "Toto",
    "password": "__v4l1d_P455sw0rd__",
    "contact_ok": "true",
    "phoneNumber": "0612345678",
    "dateOfBirth": serialize(datetime(2001, 1, 1)),
}


class Returns201Test:
    @freeze_time("2019-01-01 01:00:00")
    @patch("pcapi.routes.webapp.signup.get_authorized_emails_and_dept_codes")
    @pytest.mark.usefixtures("db_session")
    def when_data_is_accurate(self, get_authorized_emails_and_dept_codes, app):
        # Given
        data = BASE_DATA.copy()
        expected_response_json = {
            "isBeneficiary": False,
            "departementCode": "93",
            "email": "toto@example.com",
            "firstName": "Toto",
            "isAdmin": False,
            "lastName": "Martin",
            "phoneNumber": "0612345678",
            "postalCode": "93100",
            "publicName": "Toto",
            "dateOfBirth": "2001-01-01T00:00:00Z",
        }
        other_expected_keys = {"id", "dateCreated"}
        get_authorized_emails_and_dept_codes.return_value = (["toto@example.com"], ["93"])

        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=data)

        # Then
        assert response.status_code == 201
        assert "Set-Cookie" not in response.headers
        json = response.json
        for key, value in expected_response_json.items():
            if key != "dateCreated":
                assert json[key] == value
        for key in other_expected_keys:
            assert key in json

        user = User.query.filter_by(email="toto@example.com").first()
        assert user.notificationSubscriptions == {"marketing_push": True, "marketing_email": True}
        assert user.hasSeenTutorials is True
        assert user.needsToFillCulturalSurvey is False

    @patch("pcapi.routes.webapp.signup.get_authorized_emails_and_dept_codes")
    @pytest.mark.usefixtures("db_session")
    def test_created_user_does_not_have_validation_token_and_cannot_book_free_offers(
        self, get_authorized_emails_and_dept_codes, app
    ):
        data = BASE_DATA.copy()
        get_authorized_emails_and_dept_codes.return_value = (["toto@example.com"], ["93"])

        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=data)

        # Then
        assert response.status_code == 201
        assert "validationToken" not in response.json
        created_user = User.query.filter_by(email="toto@example.com").first()
        assert created_user.validationToken is None
        assert not created_user.has_beneficiary_role
        assert len(push_testing.requests) == 1
        assert not push_testing.requests[0]["attribute_values"]["u.is_beneficiary"]

    @patch("pcapi.routes.webapp.signup.get_authorized_emails_and_dept_codes")
    @pytest.mark.usefixtures("db_session")
    def test_does_not_allow_the_creation_of_admins(self, get_authorized_emails_and_dept_codes, app):
        # Given
        user_json = {
            "email": "pctest.isAdmin.canBook@example.com",
            "publicName": "IsAdmin CanBook",
            "firstName": "IsAdmin",
            "lastName": "CanBook",
            "postalCode": "93100",
            "password": "__v4l1d_P455sw0rd__",
            "contact_ok": "true",
            "isAdmin": True,
            "isBeneficiary": True,
        }
        get_authorized_emails_and_dept_codes.return_value = (["pctest.isAdmin.canBook@example.com"], ["93"])

        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=user_json)

        # Then
        assert response.status_code == 201
        created_user = User.query.filter_by(email="pctest.isadmin.canbook@example.com").one()
        assert not created_user.isAdmin


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    def when_email_missing(self, app):
        # Given
        data = BASE_DATA.copy()
        del data["email"]

        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error
        assert len(push_testing.requests) == 0

    @patch("pcapi.routes.webapp.signup.get_authorized_emails_and_dept_codes")
    @pytest.mark.usefixtures("db_session")
    def when_email_with_invalid_format(self, get_authorized_emails_and_dept_codes, app):
        # Given
        get_authorized_emails_and_dept_codes.return_value = (["toto@example.com"], ["93"])
        data = BASE_DATA.copy()
        data["email"] = "toto"

        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    @patch("pcapi.routes.webapp.signup.get_authorized_emails_and_dept_codes")
    @pytest.mark.usefixtures("db_session")
    def when_email_is_already_used(self, get_authorized_emails_and_dept_codes, app):
        # Given
        get_authorized_emails_and_dept_codes.return_value = (["toto@example.com"], ["93"])

        TestClient(app.test_client()).post("/users/signup/webapp", json=BASE_DATA)

        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=BASE_DATA)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    @patch("pcapi.routes.webapp.signup.get_authorized_emails_and_dept_codes")
    @pytest.mark.usefixtures("db_session")
    def when_public_name_is_missing(self, get_authorized_emails_and_dept_codes, app):
        # Given
        get_authorized_emails_and_dept_codes.return_value = (["toto@example.com"], ["93"])
        data = BASE_DATA.copy()
        del data["publicName"]

        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "publicName" in error

    @patch("pcapi.routes.webapp.signup.get_authorized_emails_and_dept_codes")
    @pytest.mark.usefixtures("db_session")
    def when_public_name_is_too_long(self, get_authorized_emails_and_dept_codes, app):
        # Given
        get_authorized_emails_and_dept_codes.return_value = (["toto@example.com"], ["93"])
        data = BASE_DATA.copy()
        data["publicName"] = "x" * 300

        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "publicName" in error

    @pytest.mark.usefixtures("db_session")
    def when_password_is_missing(self, app):
        # Given
        data = BASE_DATA.copy()
        del data["password"]

        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "password" in error

    @pytest.mark.usefixtures("db_session")
    def when_password_is_invalid(self, app):
        # Given
        data = BASE_DATA.copy()
        data["password"] = "weakpassword"

        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=data)

        # Then
        assert response.status_code == 400
        response = response.json
        assert "password" in response

    @pytest.mark.usefixtures("db_session")
    def when_missing_contact_ok(self, app):
        data = BASE_DATA.copy()
        del data["contact_ok"]

        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "contact_ok" in error

    @pytest.mark.usefixtures("db_session")
    def when_wrong_format_on_contact_ok(self, app):
        data = BASE_DATA.copy()
        data["contact_ok"] = "t"

        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "contact_ok" in error

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.routes.webapp.signup.get_authorized_emails_and_dept_codes")
    def when_user_not_in_exp_spreadsheet(self, get_authorized_emails_and_dept_codes, app):
        # Given
        get_authorized_emails_and_dept_codes.return_value = (["toto@email.com", "other@email.com"], ["93", "93"])
        data = BASE_DATA.copy()
        data["email"] = "unknown@unknown.com"

        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error


class Returns403Test:
    @pytest.mark.usefixtures("db_session")
    @override_features(WEBAPP_SIGNUP=False)
    def when_feature_is_not_active(self, app):
        # When
        response = TestClient(app.test_client()).post("/users/signup/webapp", json=BASE_DATA)

        # Then
        assert response.status_code == 403
