import uuid
from datetime import timedelta
from unittest import mock

import pytest

import pcapi.core.token as token_utils
from pcapi.core.users import models as users_models
from pcapi.models import db


class Returns204Tests:
    @pytest.mark.usefixtures("db_session")
    @pytest.mark.usefixtures("rsa_keys")
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
        rsa_keys,
        settings,
    ):
        private_key_pem_file, public_key_pem_file = rsa_keys
        settings.PASSWORDLESS_LOGIN_PRIVATE_KEY = private_key_pem_file
        settings.PASSWORDLESS_LOGIN_PUBLIC_KEY = public_key_pem_file
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
        assert response.status_code == 204

        mocked_send_signup_email.assert_called_once()
        args, _ = mocked_send_signup_email.call_args
        passwordless_login_token = args[1]

        user = db.session.query(users_models.User).filter_by(email="pro@example.com").one()
        assert user.email == "pro@example.com"
        assert user.isEmailValidated is False
        mocked_pipeline_exec.return_value = [f'{{"user_id": "{user.id}", "jti": "{str(uuid.uuid4())}"}}', 1]
        response = client.patch(f"/users/validate_signup/{passwordless_login_token}")
        assert response.status_code == 204
        assert "Set-Cookie" in response.headers

        user = db.session.query(users_models.User).filter_by(email="pro@example.com").one()
        assert user.email == "pro@example.com"
        assert user.isEmailValidated is True

        with client.client.session_transaction() as session_:
            assert session_["user_id"] == user.id


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    @pytest.mark.usefixtures("rsa_keys")
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.execute")
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.delete")
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.get")
    @mock.patch("pcapi.flask_app.redis.client.Redis.set")
    @mock.patch("pcapi.core.mails.transactional.send_signup_email_confirmation_to_pro")
    @mock.patch("uuid.uuid4", return_value=uuid.uuid4())
    def test_invalid_user_id(
        self,
        mocked_uuid,
        mocked_send_signup_email,
        mocked_redis_set,
        mocked_pipeline_get,
        mocked_pipeline_del,
        mocked_pipeline_exec,
        client,
        rsa_keys,
        settings,
    ):
        private_key_pem_file, public_key_pem_file = rsa_keys
        settings.PASSWORDLESS_LOGIN_PRIVATE_KEY = private_key_pem_file
        settings.PASSWORDLESS_LOGIN_PUBLIC_KEY = public_key_pem_file
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
        assert response.status_code == 204

        mocked_send_signup_email.assert_called_once()
        args, _ = mocked_send_signup_email.call_args
        passwordless_login_token = args[1]

        user = db.session.query(users_models.User).filter_by(email="pro@example.com").one()
        assert user.email == "pro@example.com"
        assert user.isEmailValidated is False
        mocked_pipeline_exec.return_value = [f'{{"user_id": "{user.id - 1}", "jti": "{str(uuid.uuid4())}"}}', 1]
        response = client.patch(f"/users/validate_signup/{passwordless_login_token}")
        assert response.status_code == 404
        assert "Set-Cookie" not in response.headers

        user = db.session.query(users_models.User).filter_by(email="pro@example.com").one()
        assert user.email == "pro@example.com"
        assert user.isEmailValidated is False

    @pytest.mark.usefixtures("db_session")
    @pytest.mark.usefixtures("rsa_keys")
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.execute")
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.delete")
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.get")
    @mock.patch("pcapi.flask_app.redis.client.Redis.set")
    @mock.patch("pcapi.core.mails.transactional.send_signup_email_confirmation_to_pro")
    @mock.patch("uuid.uuid4", return_value=uuid.uuid4())
    def test_expired_token(
        self,
        mocked_uuid,
        mocked_send_signup_email,
        mocked_redis_set,
        mocked_pipeline_get,
        mocked_pipeline_del,
        mocked_pipeline_exec,
        client,
        rsa_keys,
        settings,
    ):
        private_key_pem_file, public_key_pem_file = rsa_keys
        settings.PASSWORDLESS_LOGIN_PRIVATE_KEY = private_key_pem_file
        settings.PASSWORDLESS_LOGIN_PUBLIC_KEY = public_key_pem_file
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
        assert response.status_code == 204

        mocked_send_signup_email.assert_called_once()

        user = db.session.query(users_models.User).filter_by(email="pro@example.com").one()
        assert user.email == "pro@example.com"
        assert user.isEmailValidated is False

        fake = token_utils.create_passwordless_login_token(user.id, ttl=timedelta(seconds=0))
        mocked_pipeline_exec.return_value = [f'{{"user_id": "{user.id}", "jti": "{str(uuid.uuid4())}"}}', 1]
        response = client.patch(f"/users/validate_signup/{fake}")
        assert response.status_code == 404
        assert "Set-Cookie" not in response.headers

        user = db.session.query(users_models.User).filter_by(email="pro@example.com").one()
        assert user.email == "pro@example.com"
        assert user.isEmailValidated is False

    @pytest.mark.usefixtures("db_session")
    @pytest.mark.usefixtures("rsa_keys")
    @mock.patch("pcapi.core.mails.transactional.send_signup_email_confirmation_to_pro")
    @mock.patch("uuid.uuid4", return_value=uuid.uuid4())
    def test_already_used_token(
        self,
        mocked_uuid,
        mocked_send_signup_email,
        client,
        rsa_keys,
        settings,
    ):
        private_key_pem_file, public_key_pem_file = rsa_keys
        settings.PASSWORDLESS_LOGIN_PRIVATE_KEY = private_key_pem_file
        settings.PASSWORDLESS_LOGIN_PUBLIC_KEY = public_key_pem_file
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
        assert response.status_code == 204

        mocked_send_signup_email.assert_called_once()
        args, _ = mocked_send_signup_email.call_args
        passwordless_login_token = args[1]

        user = db.session.query(users_models.User).filter_by(email="pro@example.com").one()
        assert user.email == "pro@example.com"
        assert user.isEmailValidated is False
        response = client.patch(f"/users/validate_signup/{passwordless_login_token}")
        assert response.status_code == 204
        assert "Set-Cookie" in response.headers
        response = client.patch(f"/users/validate_signup/{passwordless_login_token}")
        assert response.status_code == 404
