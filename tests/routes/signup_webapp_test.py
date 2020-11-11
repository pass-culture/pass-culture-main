from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.models.feature import Feature
from pcapi.models.feature import FeatureToggle
from pcapi.models.user_sql_entity import UserSQLEntity
from pcapi.repository import repository
from pcapi.routes.serialization import serialize

from tests.conftest import TestClient


BASE_DATA = {
    "email": "toto@btmx.fr",
    "firstName": "Toto",
    "lastName": "Martin",
    "postalCode": "93100",
    "publicName": "Toto",
    "password": "__v4l1d_P455sw0rd__",
    "contact_ok": "true",
    "phoneNumber": "0612345678",
    "dateOfBirth": serialize(datetime(2001, 1, 1)),
}


class Post:
    class Returns201:
        @freeze_time("2019-01-01 01:00:00")
        @patch("pcapi.routes.signup.get_authorized_emails_and_dept_codes")
        @pytest.mark.usefixtures("db_session")
        def when_data_is_accurate(self, get_authorized_emails_and_dept_codes, app):
            # Given
            data = BASE_DATA.copy()
            expected_response_json = {
                "canBookFreeOffers": False,
                "departementCode": "93",
                "email": "toto@btmx.fr",
                "firstName": "Toto",
                "isAdmin": False,
                "lastName": "Martin",
                "phoneNumber": "0612345678",
                "postalCode": "93100",
                "publicName": "Toto",
                "dateOfBirth": "2001-01-01T00:00:00Z",
            }
            other_expected_keys = {"id", "dateCreated"}
            get_authorized_emails_and_dept_codes.return_value = (["toto@btmx.fr"], ["93"])

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

        @patch("pcapi.routes.signup.get_authorized_emails_and_dept_codes")
        @pytest.mark.usefixtures("db_session")
        def test_created_user_does_not_have_validation_token_and_cannot_book_free_offers(
            self, get_authorized_emails_and_dept_codes, app
        ):
            data = BASE_DATA.copy()
            get_authorized_emails_and_dept_codes.return_value = (["toto@btmx.fr"], ["93"])

            # When
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=data, headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 201
            assert "validationToken" not in response.json
            created_user = UserSQLEntity.query.filter_by(email="toto@btmx.fr").first()
            assert created_user.validationToken is None
            assert not created_user.canBookFreeOffers

        @patch("pcapi.routes.signup.get_authorized_emails_and_dept_codes")
        @pytest.mark.usefixtures("db_session")
        def test_does_not_allow_the_creation_of_admins(self, get_authorized_emails_and_dept_codes, app):
            # Given
            user_json = {
                "email": "pctest.isAdmin.canBook@btmx.fr",
                "publicName": "IsAdmin CanBook",
                "firstName": "IsAdmin",
                "lastName": "CanBook",
                "postalCode": "93100",
                "password": "__v4l1d_P455sw0rd__",
                "contact_ok": "true",
                "isAdmin": True,
                "canBookFreeOffers": True,
            }
            get_authorized_emails_and_dept_codes.return_value = (["pctest.isAdmin.canBook@btmx.fr"], ["93"])

            # When
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=user_json, headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 201
            created_user = UserSQLEntity.query.filter_by(email="pctest.isAdmin.canBook@btmx.fr").one()
            assert not created_user.isAdmin

        @patch("pcapi.routes.signup.get_authorized_emails_and_dept_codes")
        @pytest.mark.usefixtures("db_session")
        def test_created_user_does_not_have_validation_token_and_cannot_book_free_offers(
            self, get_authorized_emails_and_dept_codes, app
        ):
            # Given
            data = BASE_DATA.copy()
            get_authorized_emails_and_dept_codes.return_value = (["toto@btmx.fr"], ["93"])

            # When
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=data, headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 201
            assert "validationToken" not in response.json
            created_user = UserSQLEntity.query.filter_by(email="toto@btmx.fr").first()
            assert created_user.needsToFillCulturalSurvey == True

    class Returns400:
        @pytest.mark.usefixtures("db_session")
        def when_email_missing(self, app):
            # Given
            data = BASE_DATA.copy()
            del data["email"]

            # When
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=data, headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 400
            error = response.json
            assert "email" in error

        @patch("pcapi.routes.signup.get_authorized_emails_and_dept_codes")
        @pytest.mark.usefixtures("db_session")
        def when_email_with_invalid_format(self, get_authorized_emails_and_dept_codes, app):
            # Given
            get_authorized_emails_and_dept_codes.return_value = (["toto@btmx.fr"], ["93"])
            data = BASE_DATA.copy()
            data["email"] = "toto"

            # When
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=data, headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 400
            error = response.json
            assert "email" in error

        @patch("pcapi.routes.signup.get_authorized_emails_and_dept_codes")
        @pytest.mark.usefixtures("db_session")
        def when_email_is_already_used(self, get_authorized_emails_and_dept_codes, app):
            # Given
            get_authorized_emails_and_dept_codes.return_value = (["toto@btmx.fr"], ["93"])

            TestClient(app.test_client()).post(
                "/users/signup/webapp", json=BASE_DATA, headers={"origin": "http://localhost:3000"}
            )

            # When
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=BASE_DATA, headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 400
            error = response.json
            assert "email" in error

        @patch("pcapi.routes.signup.get_authorized_emails_and_dept_codes")
        @pytest.mark.usefixtures("db_session")
        def when_public_name_is_missing(self, get_authorized_emails_and_dept_codes, app):
            # Given
            get_authorized_emails_and_dept_codes.return_value = (["toto@btmx.fr"], ["93"])
            data = BASE_DATA.copy()
            del data["publicName"]

            # When
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=data, headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 400
            error = response.json
            assert "publicName" in error

        @patch("pcapi.routes.signup.get_authorized_emails_and_dept_codes")
        @pytest.mark.usefixtures("db_session")
        def when_public_name_is_too_short(self, get_authorized_emails_and_dept_codes, app):
            # Given
            get_authorized_emails_and_dept_codes.return_value = (["toto@btmx.fr"], ["93"])
            data = BASE_DATA.copy()
            data["publicName"] = "t"

            # When
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=data, headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 400
            error = response.json
            assert "publicName" in error

        @patch("pcapi.routes.signup.get_authorized_emails_and_dept_codes")
        @pytest.mark.usefixtures("db_session")
        def when_public_name_is_too_long(self, get_authorized_emails_and_dept_codes, app):
            # Given
            get_authorized_emails_and_dept_codes.return_value = (["toto@btmx.fr"], ["93"])
            data = BASE_DATA.copy()
            data["publicName"] = "x" * 300

            # When
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=data, headers={"origin": "http://localhost:3000"}
            )

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
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=data, headers={"origin": "http://localhost:3000"}
            )

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
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=data, headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 400
            response = response.json
            assert "password" in response

        @pytest.mark.usefixtures("db_session")
        def when_missing_contact_ok(self, app):
            data = BASE_DATA.copy()
            del data["contact_ok"]

            # When
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=data, headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 400
            error = response.json
            assert "contact_ok" in error

        @pytest.mark.usefixtures("db_session")
        def when_wrong_format_on_contact_ok(self, app):
            data = BASE_DATA.copy()
            data["contact_ok"] = "t"

            # When
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=data, headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 400
            error = response.json
            assert "contact_ok" in error

        @pytest.mark.usefixtures("db_session")
        @patch("pcapi.routes.signup.get_authorized_emails_and_dept_codes")
        def when_user_not_in_exp_spreadsheet(self, get_authorized_emails_and_dept_codes, app):
            # Given
            get_authorized_emails_and_dept_codes.return_value = (["toto@email.com", "other@email.com"], ["93", "93"])
            data = BASE_DATA.copy()
            data["email"] = "unknown@unknown.com"

            # When
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=data, headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 400
            error = response.json
            assert "email" in error

    class Returns403:
        @pytest.mark.usefixtures("db_session")
        def when_feature_is_not_active(self, app):
            # Given
            data = BASE_DATA.copy()
            feature = Feature.query.filter_by(name=FeatureToggle.WEBAPP_SIGNUP).first()
            feature.isActive = False
            repository.save(feature)

            # When
            response = TestClient(app.test_client()).post(
                "/users/signup/webapp", json=data, headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 403
