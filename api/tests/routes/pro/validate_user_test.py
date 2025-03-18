from unittest import mock
import uuid

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import session
import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.token as token_utils
from pcapi.core.users import models as users_models


class ValidateUserTest:
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
    def test_validate_user_token(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__isEmailValidated=False)
        token = token_utils.Token.create(
            token_utils.TokenType.SIGNUP_EMAIL_CONFIRMATION, None, user_id=user_offerer.user.id
        )
        response = client.patch(f"/users/validate_signup/{token.encoded_token}")
        assert response.status_code == 204
        assert user_offerer.user.isEmailValidated

    @pytest.mark.usefixtures("db_session")
    def test_fail_if_unknown_token(self, client):
        response = client.patch("/users/validate_signup/unknown-token")

        assert response.status_code == 404
        assert response.json["global"] == ["Ce lien est invalide"]

    @pytest.mark.features(WIP_2025_SIGN_UP=True)
    @pytest.mark.settings(
        PASSWORDLESS_LOGIN_PRIVATE_KEY=private_pem_file, PASSWORDLESS_LOGIN_PUBLIC_KEY=public_pem_file
    )
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.execute")
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.delete")
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.get")
    @mock.patch("pcapi.flask_app.redis.client.Redis.set")
    @mock.patch("pcapi.core.mails.transactional.send_signup_email_confirmation_to_pro")
    @mock.patch("uuid.uuid4", return_value=uuid.uuid4())
    def test_passwordless_login_workflow_on_signup(
        self,
        mocked_uuid,
        mocked_send_signup_email,
        mocked_redis_set,
        mocked_pipeline_get,
        mocked_pipeline_del,
        mocked_pipeline_exec,
        client,
    ):
        user_data = {
            "email": "pro@example.com",
            "firstName": "Toto",
            "lastName": "Pro",
            "password": "__v4l1d_P455sw0rd__",
            "contactOk": False,
            "token": "token",
            "phoneNumber": "0102030405",
        }
        response = client.post("/users/signup", json=user_data)

        mocked_send_signup_email.assert_called_once()
        args, kwargs = mocked_send_signup_email.call_args
        passwordless_login_token = args[1]

        user = users_models.User.query.filter_by(email="pro@example.com").one()
        assert user.email == "pro@example.com"
        assert user.isEmailValidated is False

        mocked_pipeline_exec.return_value = [f'{{"user_id": "{user.id}", "jti": "{str(uuid.uuid4())}"}}', 1]

        response = client.patch(f"/users/validate_signup/{passwordless_login_token}")
        assert response.status_code == 204
        assert "Set-Cookie" in response.headers

        user = users_models.User.query.filter_by(email="pro@example.com").one()
        assert user.email == "pro@example.com"
        assert user.isEmailValidated is True

        with client.client.session_transaction() as session:
            assert session["user_id"] == user.id
