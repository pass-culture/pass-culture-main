import pytest

import pcapi.core.history.models as history_models
from pcapi.core.users.models import User


BASE_DATA_PRO = {
    "email": "toto_pro@example.com",
    "firstName": "Toto",
    "lastName": "Pro",
    "password": "__v4l1d_P455sw0rd__",
    "phoneNumber": "0102030405",
    "contactOk": False,
}


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def test_when_user_data_is_valid(self, client):
        # Given
        data = BASE_DATA_PRO.copy()

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 204
        assert "Set-Cookie" not in response.headers

        user = User.query.filter_by(email="toto_pro@example.com").first()
        assert user is not None
        assert user.has_beneficiary_role is False
        assert user.has_non_attached_pro_role is True
        assert user.email == "toto_pro@example.com"
        assert user.firstName == "Toto"
        assert not user.has_admin_role
        assert user.lastName == "Pro"
        assert user.phoneNumber == "+33102030405"
        assert user.dateOfBirth is None
        assert user.dateCreated is not None
        assert user.notificationSubscriptions == {"marketing_push": True, "marketing_email": False}

        actions_list = history_models.ActionHistory.query.order_by(history_models.ActionHistory.actionType).all()
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.USER_CREATED
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user

    def when_successful_and_mark_pro_user_as_no_cultural_survey_needed(self, client):
        data = BASE_DATA_PRO.copy()

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 204
        user = User.query.filter_by(email="toto_pro@example.com").first()
        assert user.needsToFillCulturalSurvey is False


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_when_email_is_missing(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["email"]

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def test_when_email_is_invalid(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["email"] = "toto"

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def test_when_email_is_already_used(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        client.post("/v2/users/signup/pro", json=data)

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def test_when_password_is_missing(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["password"]

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "password" in error

    def test_when_password_is_invalid(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["password"] = "weakpassword"

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        response = response.json
        assert response["password"] == [
            "Ton mot de passe doit contenir au moins :\n"
            "- 12 caractères\n"
            "- Un chiffre\n"
            "- Une majuscule et une minuscule\n"
            "- Un caractère spécial"
        ]

    def test_when_extra_data_is_given(self, client):
        # Given
        user_json = {
            "email": "toto_pro@example.com",
            "firstName": "Toto",
            "lastName": "Pro",
            "password": "__v4l1d_P455sw0rd__",
            "phoneNumber": "0102030405",
            "isAdmin": True,
            "contactOk": "true",
        }

        # When
        response = client.post("/v2/users/signup/pro", json=user_json)

        # Then
        assert response.status_code == 400
        created_user = User.query.filter_by(email="toto_pro@example.com").first()
        assert created_user is None

    def test_when_bad_format_phone_number(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["phoneNumber"] = "abc 123"

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "phoneNumber" in error
        assert "Le numéro de téléphone est invalide" in error["phoneNumber"]

    def test_when_invalid_phone_number(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["phoneNumber"] = "0873492896"

        # When
        response = client.post("/v2/users/signup/pro", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "phoneNumber" in error
        assert "Le numéro de téléphone est invalide" in error["phoneNumber"]
