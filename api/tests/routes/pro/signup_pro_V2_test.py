from dataclasses import asdict
from unittest import mock

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

import pcapi.core.history.models as history_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core import token as token_utils
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.users.models import User
from pcapi.models import db


BASE_DATA_PRO_WITHOUT_PHONE = {
    "email": "toto_pro@example.com",
    "firstName": "Toto",
    "lastName": "Pro",
    "password": "__v4l1d_P455sw0rd__",  # ggignore
    "contactOk": False,
    "token": "token",
}

BASE_DATA_PRO = BASE_DATA_PRO_WITHOUT_PHONE.copy()
BASE_DATA_PRO["phoneNumber"] = "0102030405"

private_key = rsa.generate_private_key(public_exponent=3, key_size=1024)
public_key = private_key.public_key()

private_pem_file = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption(),
)
public_pem_file = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)


@pytest.mark.usefixtures("db_session")
class Returns204Test:
    def test_when_user_data_is_valid(self, client):
        # Given
        data = BASE_DATA_PRO.copy()

        # When
        response = client.post("/users/signup", json=data)

        # Then
        assert response.status_code == 204
        assert "Set-Cookie" not in response.headers

        user = db.session.query(User).filter_by(email="toto_pro@example.com").first()
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
        assert user.notificationSubscriptions == {
            "marketing_push": True,
            "marketing_email": False,
            "subscribed_themes": [],
        }

        actions_list = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.actionType).all()
        )
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.USER_CREATED
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user

        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["To"] == user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.SIGNUP_EMAIL_CONFIRMATION_TO_PRO.value)

    @pytest.mark.settings(
        PASSWORDLESS_LOGIN_PRIVATE_KEY=private_pem_file, PASSWORDLESS_LOGIN_PUBLIC_KEY=public_pem_file
    )
    @pytest.mark.features(WIP_2025_SIGN_UP=True)
    def test_when_user_data_is_valid_without_phone(self, client):
        # Given
        data = BASE_DATA_PRO_WITHOUT_PHONE.copy()

        # When
        response = client.post("/users/signup", json=data)

        # Then
        assert response.status_code == 204
        assert "Set-Cookie" not in response.headers

        user = db.session.query(User).filter_by(email="toto_pro@example.com").first()
        assert user is not None
        assert user.has_beneficiary_role is False
        assert user.has_non_attached_pro_role is True
        assert user.email == "toto_pro@example.com"
        assert user.firstName == "Toto"
        assert not user.has_admin_role
        assert user.lastName == "Pro"
        assert user.phoneNumber is None
        assert user.dateOfBirth is None
        assert user.dateCreated is not None
        assert user.notificationSubscriptions == {
            "marketing_push": True,
            "marketing_email": False,
            "subscribed_themes": [],
        }

        actions_list = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.actionType).all()
        )
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.USER_CREATED
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user

        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["To"] == user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.SIGNUP_EMAIL_CONFIRMATION_TO_PRO.value)

    def when_successful_and_mark_pro_user_as_no_cultural_survey_needed(self, client):
        data = BASE_DATA_PRO.copy()

        # When
        response = client.post("/users/signup", json=data)

        # Then
        assert response.status_code == 204
        user = db.session.query(User).filter_by(email="toto_pro@example.com").first()
        assert user.needsToFillCulturalSurvey is False


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_when_email_is_missing(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["email"]

        # When
        response = client.post("/users/signup", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def test_when_email_is_invalid(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["email"] = "toto"

        # When
        response = client.post("/users/signup", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def test_when_email_is_already_used(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        client.post("/users/signup", json=data)

        # When
        response = client.post("/users/signup", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "email" in error

    def test_when_password_is_missing(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        del data["password"]

        # When
        response = client.post("/users/signup", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "password" in error

    def test_when_password_is_invalid(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["password"] = "weakpassword"

        # When
        response = client.post("/users/signup", json=data)

        # Then
        assert response.status_code == 400
        response = response.json
        assert response["password"] == [
            "Le mot de passe doit contenir au moins :\n"
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
        response = client.post("/users/signup", json=user_json)

        # Then
        assert response.status_code == 400
        created_user = db.session.query(User).filter_by(email="toto_pro@example.com").first()
        assert created_user is None

    def test_when_bad_format_phone_number(self, client):
        # Given
        data = BASE_DATA_PRO.copy()
        data["phoneNumber"] = "abc 123"

        # When
        response = client.post("/users/signup", json=data)

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
        response = client.post("/users/signup", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "phoneNumber" in error
        assert "Le numéro de téléphone est invalide" in error["phoneNumber"]

    @pytest.mark.features(WIP_2025_SIGN_UP=False)
    def test_when_no_phone_number(self, client):
        # Given
        data = BASE_DATA_PRO_WITHOUT_PHONE.copy()

        # When
        response = client.post("/users/signup", json=data)

        # Then
        assert response.status_code == 400
        error = response.json
        assert "phoneNumber" in error
        assert "Le numéro de téléphone est requis" in error["phoneNumber"]

    @pytest.mark.features(WIP_2025_AUTOLOGIN=True)
    @pytest.mark.settings(
        PASSWORDLESS_LOGIN_PRIVATE_KEY=private_pem_file, PASSWORDLESS_LOGIN_PUBLIC_KEY=public_pem_file
    )
    @mock.patch("pcapi.core.token.create_passwordless_login_token", return_value="fake_passwordless_login_token")
    @mock.patch("pcapi.core.mails.transactional.send_signup_email_confirmation_to_pro")
    def test_passwordlesslogin_token_is_sent_with_ff_on(
        self, mocked_send_signup_email, mocked_create_password_less_login_token, client
    ):
        client.post("/users/signup", json=BASE_DATA_PRO)
        mocked_create_password_less_login_token.assert_called_once()
        mocked_send_signup_email.assert_called_once()

        args, _ = mocked_send_signup_email.call_args

        assert "fake_passwordless_login_token" in args

        user = db.session.query(User).filter_by(email="toto_pro@example.com").first()
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
        assert user.notificationSubscriptions == {
            "marketing_push": True,
            "marketing_email": False,
            "subscribed_themes": [],
        }

    @pytest.mark.features(WIP_2025_AUTOLOGIN=False)
    @mock.patch("pcapi.core.token.Token.create")
    @mock.patch("pcapi.core.token.create_passwordless_login_token")
    @mock.patch("pcapi.core.mails.transactional.send_signup_email_confirmation_to_pro")
    def test_signup_email_confirmation_is_used_with_ff_off(
        self,
        mocked_send_signup_email,
        mocked_create_password_less_login_token,
        mocked_signup_confirmation_email,
        client,
    ):
        client.post("/users/signup", json=BASE_DATA_PRO)

        mocked_create_password_less_login_token.assert_not_called()
        mocked_signup_confirmation_email.assert_called_once()
        mocked_send_signup_email.assert_called_once()

        args, _ = mocked_signup_confirmation_email.call_args

        assert token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION in args

        user = db.session.query(User).filter_by(email="toto_pro@example.com").first()
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
        assert user.notificationSubscriptions == {
            "marketing_push": True,
            "marketing_email": False,
            "subscribed_themes": [],
        }
