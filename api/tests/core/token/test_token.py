from datetime import datetime
from datetime import timedelta
import hashlib
import json
import logging
from unittest import mock
import uuid

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import fakeredis
import jwt
import pytest
import time_machine

from pcapi import settings
from pcapi.core import token as token_tools
from pcapi.core.users.exceptions import InvalidToken
from pcapi.core.users.utils import encode_jwt_payload


pytestmark = pytest.mark.usefixtures("db_session")


class TokenTest:
    token_type = token_tools.TokenType.EMAIL_CHANGE_CONFIRMATION
    ttl = timedelta(days=1)
    data = {"key1": "value1", "key2": "value2"}
    user_id = 4597

    def test_create_token_then_get_data(self):
        """testing the creation of a token and getting the data"""
        token = token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
        assert token.data == self.data
        assert token.user_id == self.user_id
        assert token.type_ == self.token_type
        assert token.encoded_token is not None
        assert token_tools.Token.get_expiration_date(self.token_type, self.user_id).isoformat(timespec="hours") == (
            datetime.utcnow() + self.ttl
        ).isoformat(timespec="hours")

    def test_create_token_with_no_data_no_ttl(self):
        """no data, no user and no ttl are provided"""
        token = token_tools.Token.create(self.token_type, None, self.user_id)
        assert not token.data and isinstance(token.data, dict)
        assert token.user_id == self.user_id
        assert token.type_ == self.token_type
        assert token.encoded_token is not None
        assert token_tools.Token.get_expiration_date(self.token_type, self.user_id) is None

    def test_token_from_encoded_token_and_get_data(self):
        """if the token is created from an encoded token, the data should be the same"""
        old_token = token_tools.Token.create(
            self.token_type,
            self.ttl,
            self.user_id,
            self.data,
        )
        token = token_tools.Token.load_without_checking(old_token.encoded_token)
        assert token.data == old_token.data
        assert token.user_id == old_token.user_id
        assert token.type_ == old_token.type_
        assert token.encoded_token == old_token.encoded_token
        assert token_tools.Token.get_expiration_date(self.token_type, self.user_id).isoformat(timespec="hours") == (
            datetime.utcnow() + self.ttl
        ).isoformat(timespec="hours")

    def test_get_expiration_date_used_token(self):
        """if the token has been expired using expire_token, the expiration date should be None"""
        token = token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
        token.expire()
        assert token_tools.Token.get_expiration_date(self.token_type, self.user_id) is None

    def test_get_expiration_date_expired_token(self):
        """if the token has been expired using expire_token, the expiration date should be None"""
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            with time_machine.travel("2021-01-01"):
                token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
            with time_machine.travel("2021-01-03"):
                assert token_tools.Token.get_expiration_date(self.token_type, self.user_id) is None

    def test_check_token_exists(self):
        """if the token exists, no exception should be raised"""
        token = token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
        # should not raise
        token.check(self.token_type, self.user_id)

    def test_check_token_is_used(self):
        """if the token has been expired using expire_token, an exception should be raised"""
        token = token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
        token.expire()
        with pytest.raises(InvalidToken):
            token.check(self.token_type, self.user_id)

    def test_check_token_does_not_exist(self):
        """if the token does not exist, an exception should be raised"""
        encoded_token = encode_jwt_payload(
            {"token_type": self.token_type.value, "user_id": self.user_id, "data": self.data}
        )
        token = token_tools.Token.load_without_checking(encoded_token)
        with pytest.raises(InvalidToken):
            token.check(self.token_type, self.user_id)

    def test_wrong_token(self):
        """if the token has the wrong format, an exception should be raised"""
        with pytest.raises(InvalidToken):
            token_tools.Token.load_without_checking("encoded_token")

        # every token should have a token_type
        encoded_token = encode_jwt_payload({"user_id": self.user_id, "data": self.data})
        with pytest.raises(InvalidToken):
            token_tools.Token.load_without_checking(encoded_token)

    mock_redis_client = fakeredis.FakeStrictRedis()

    def test_check_token_is_expired(self, app):
        """if the token expiration date is in the past, an exception should be raised"""
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            with time_machine.travel("2021-01-01"):
                token = token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
            with time_machine.travel("2021-01-03"):
                with pytest.raises(InvalidToken):
                    token.check(self.token_type, self.user_id)

    def test_check_token_wrong_type(self):
        """if the token type is not the same as the one provided when creating the token, an exception should be raised"""
        token = token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
        with pytest.raises(InvalidToken):
            token.check(token_tools.TokenType.EMAIL_CHANGE_VALIDATION, self.user_id)

    def test_check_token_wrong_user(self):
        """if the user_id is not the same as the one provided when creating the token, an exception should be raised"""
        token = token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
        with pytest.raises(InvalidToken):
            token.check(self.token_type, "wrong_user_id")

    def test_check_token_no_user_provided(self):
        """if no user is provided, we do not check the user_id"""
        token = token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
        # should not raise
        token.check(self.token_type)

    def test_expire_twice(self):
        """the expire_token method should not raise if called twice"""
        token = token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
        token.expire()
        # should not raise
        token.expire()

    def check_token_twice(self):
        """the check_token method should not expire the token"""
        token = token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
        # should not raise
        token.check(self.token_type, self.user_id)
        # should not raise
        token.check(self.token_type, self.user_id)


class SecureTokenTest:
    def test_create_token_with_data(self, app):
        data = {"int": 12, "str": "Ça c'est pas de l'ascii 😉"}

        token = token_tools.SecureToken(data=data)

        assert 29 < app.redis_client.ttl(f"pcapi:token:SecureToken_{token.token}") <= 30
        assert len(token.token) == 86
        assert token.data["int"] == data["int"]
        assert token.data["str"] == data["str"]

    def test_create_token_without_data(self, app):
        token = token_tools.SecureToken(ttl=10)

        assert 9 < app.redis_client.ttl(f"pcapi:token:SecureToken_{token.token}") <= 10
        assert len(token.token) == 86

    def test_retrieve_token_with_data(self, app):
        data = {"int": 12, "str": "Ça c'est pas de l'ascii 😉"}
        original_token = token_tools.SecureToken(data=data)

        token = token_tools.SecureToken(token=original_token.token)

        assert app.redis_client.ttl(f"pcapi:token:SecureToken_{original_token.token}") == -2
        assert token.data["int"] == data["int"]
        assert token.data["str"] == data["str"]

    def test_retrieve_token_without_data(self, app):
        original_token = token_tools.SecureToken()

        token = token_tools.SecureToken(token=original_token.token)

        assert app.redis_client.ttl(f"pcapi:token:SecureToken_{original_token.token}") == -2
        assert token.data == {}

    def test_retrieve_unknown_token(self, app):
        # create token
        original_token = token_tools.SecureToken()
        # remove token from redis
        app.redis_client.delete(f"pcapi:token:SecureToken_{original_token.token}")
        with pytest.raises(InvalidToken):
            token_tools.SecureToken(token=original_token.token)


class AsymetricTokenTest:
    token_type = token_tools.TokenType.EMAIL_CHANGE_CONFIRMATION
    ttl = timedelta(days=1)
    data = {"key1": "value1", "key2": "value2"}
    private_key = rsa.generate_private_key(
        public_exponent=3,
        key_size=1024,
    )
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    wrong_private_key = rsa.generate_private_key(
        public_exponent=3,
        key_size=1024,
    )
    wrong_private_key_pem = wrong_private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    wrong_public_key = wrong_private_key.public_key()
    wrong_public_key_pem = wrong_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    @pytest.mark.settings(DISCORD_JWT_PRIVATE_KEY=private_key_pem, DISCORD_JWT_PUBLIC_KEY=public_key_pem)
    def test_create_token_then_get_data(self):
        """testing the creation of a token and getting the data"""
        token = token_tools.AsymetricToken.create(
            self.token_type, settings.DISCORD_JWT_PRIVATE_KEY, self.ttl, data=self.data
        )
        assert token.data == self.data
        assert token.type_ == self.token_type
        assert token.encoded_token is not None
        assert token_tools.AsymetricToken.get_expiration_date(
            self.token_type,
            token.key_suffix,
        ).isoformat(timespec="hours") == (datetime.utcnow() + self.ttl).isoformat(timespec="hours")

    @pytest.mark.settings(DISCORD_JWT_PRIVATE_KEY=wrong_private_key_pem, DISCORD_JWT_PUBLIC_KEY=public_key_pem)
    def test_creating_and_verifying_signature_with_mismatch_private_and_public_keys(self):
        token = token_tools.AsymetricToken.create(
            self.token_type, settings.DISCORD_JWT_PRIVATE_KEY, self.ttl, data=self.data
        )
        with pytest.raises(InvalidToken) as exc_info:
            token_tools.AsymetricToken.load_and_check(token.encoded_token, settings.DISCORD_JWT_PUBLIC_KEY)

        assert isinstance(exc_info.value.__cause__, jwt.PyJWTError)
        assert "Signature verification failed" == str(exc_info.value.__cause__)

    @pytest.mark.settings(DISCORD_JWT_PRIVATE_KEY=private_key_pem, DISCORD_JWT_PUBLIC_KEY=public_key_pem)
    def test_token_from_encoded_token_and_get_data(self):
        """if the token is created from an encoded token, the data should be the same"""
        old_token = token_tools.AsymetricToken.create(
            self.token_type,
            settings.DISCORD_JWT_PRIVATE_KEY,
            self.ttl,
            data=self.data,
        )
        token = token_tools.AsymetricToken.load_and_check(old_token.encoded_token, settings.DISCORD_JWT_PUBLIC_KEY)
        assert token.data == old_token.data
        assert token.type_ == old_token.type_
        assert token.encoded_token == old_token.encoded_token
        assert token_tools.AsymetricToken.get_expiration_date(self.token_type, token.key_suffix).isoformat(
            timespec="hours"
        ) == (datetime.utcnow() + self.ttl).isoformat(timespec="hours")

        token = token_tools.AsymetricToken.load_without_checking(
            old_token.encoded_token,
        )
        assert token.data == old_token.data
        assert token.type_ == old_token.type_
        assert token.encoded_token == old_token.encoded_token
        assert token_tools.AsymetricToken.get_expiration_date(self.token_type, token.key_suffix).isoformat(
            timespec="hours"
        ) == (datetime.utcnow() + self.ttl).isoformat(timespec="hours")

    @pytest.mark.settings(DISCORD_JWT_PRIVATE_KEY=private_key_pem, DISCORD_JWT_PUBLIC_KEY=public_key_pem)
    def test_load_without_checking_wrong_public_key(self):
        """if the token has the wrong signature, an exception should be raised"""
        old_token = token_tools.AsymetricToken.create(
            self.token_type,
            settings.DISCORD_JWT_PRIVATE_KEY,
            self.ttl,
            data=self.data,
        )
        with pytest.raises(InvalidToken):
            token_tools.AsymetricToken.load_and_check(
                old_token.encoded_token,
                self.wrong_public_key,
            )


class PasswordLessLoginTokenTest:
    token_type = token_tools.TokenType.PASSWORDLESS_LOGIN
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

    @pytest.mark.settings(PASSWORDLESS_LOGIN_PRIVATE_KEY=private_pem_file)
    @mock.patch("flask.current_app.redis_client.set")
    @mock.patch("uuid.uuid4", return_value=uuid.uuid4())
    def test_can_create_password_less_login_token(self, mocked_uuid, mocked_redis_set):
        expected_jti = str(mocked_uuid())
        expected_ttl = timedelta(hours=8)
        expected_user_id = 1
        key_suffix = hashlib.sha256(
            json.dumps({"user_id": str(expected_user_id), "jti": expected_jti}).encode()
        ).hexdigest()
        redis_key = token_tools.PASSWORDLESS_REDIS_KEY_TEMPLATE % {
            "type_": token_tools.TokenType.PASSWORDLESS_LOGIN.value,
            "key_suffix": key_suffix,
        }
        token = token_tools.create_passwordless_login_token(expected_user_id, expected_ttl)

        mocked_redis_set.assert_called_once_with(
            redis_key, json.dumps({"user_id": str(expected_user_id), "jti": expected_jti}), ex=expected_ttl
        )

        payload = jwt.decode(token, self.public_pem_file, algorithms=["RS256"])

        assert payload["jti"] == expected_jti
        assert payload["exp"] - payload["iat"] == 8 * 3600
        assert payload["sub"] == str(expected_user_id)

    @pytest.mark.settings(
        PASSWORDLESS_LOGIN_PRIVATE_KEY=private_pem_file, PASSWORDLESS_LOGIN_PUBLIC_KEY=public_pem_file
    )
    @pytest.mark.parametrize("missing_claim", ["exp", "iat", "sub", "jti"])
    @mock.patch("pcapi.core.users.utils.encode_jwt_payload_rs256")
    @mock.patch("flask.current_app.redis_client.set")
    @mock.patch("uuid.uuid4", return_value=uuid.uuid4())
    def test_token_with_missing_mandatory_claim_raise_decode_error_accordingly(
        self, mocked_uuid, mocked_redis_set, mocked_encode_jwt_rs256, missing_claim
    ):
        jti = str(mocked_uuid())
        ttl = timedelta(hours=8)
        sub = 1
        issued_at = datetime.utcnow() - timedelta(hours=5)
        expiration_date = issued_at + ttl
        exp = int(expiration_date.timestamp())
        iat = int(issued_at.timestamp())

        payload = {}
        if missing_claim != "jti":
            payload["jti"] = jti
        if missing_claim != "exp":
            payload["exp"] = exp
        if missing_claim != "iat":
            payload["iat"] = iat
        if missing_claim != "sub":
            payload["sub"] = str(sub)

        mocked_encode_jwt_rs256.return_value = jwt.encode(
            payload, settings.PASSWORDLESS_LOGIN_PRIVATE_KEY, algorithm="RS256"
        )

        token = token_tools.create_passwordless_login_token(sub, ttl)
        with pytest.raises(InvalidToken) as exc_info:
            token_tools.validate_passwordless_token(token)

        assert isinstance(exc_info.value.__cause__, jwt.exceptions.MissingRequiredClaimError)
        assert str(exc_info.value.__cause__) == f'Token is missing the "{missing_claim}" claim'

    @pytest.mark.settings(
        PASSWORDLESS_LOGIN_PRIVATE_KEY=private_pem_file, PASSWORDLESS_LOGIN_PUBLIC_KEY=public_pem_file
    )
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.execute")
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.delete")
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.get")
    @mock.patch("pcapi.flask_app.redis.client.Redis.set")
    @mock.patch("uuid.uuid4", return_value=uuid.uuid4())
    def test_can_successfully_consume_passwordless_login_token(
        self, mocked_uuid, mocked_redis_set, mocked_pipeline_get, mocked_pipeline_del, mocked_pipeline_execute
    ):
        expected_jti = str(mocked_uuid())
        expected_ttl = timedelta(hours=8)
        expected_user_id = 1
        key_suffix = hashlib.sha256(
            json.dumps({"user_id": str(expected_user_id), "jti": expected_jti}).encode()
        ).hexdigest()
        redis_key = token_tools.PASSWORDLESS_REDIS_KEY_TEMPLATE % {
            "type_": token_tools.TokenType.PASSWORDLESS_LOGIN.value,
            "key_suffix": key_suffix,
        }
        token = token_tools.create_passwordless_login_token(expected_user_id, expected_ttl)

        mocked_redis_set.assert_called_once_with(
            redis_key, json.dumps({"user_id": str(expected_user_id), "jti": expected_jti}), ex=expected_ttl
        )

        mocked_pipeline_execute.return_value = [f'{{"user_id": "{expected_user_id}", "jti": "{expected_jti}"}}', 1]

        payload = token_tools.validate_passwordless_token(token)

        mocked_pipeline_get.assert_called_once_with(redis_key)
        mocked_pipeline_del.assert_called_once_with(redis_key)
        mocked_pipeline_execute.assert_called_once()

        assert payload["jti"] == expected_jti
        assert payload["exp"] - payload["iat"] == 8 * 3600
        assert payload["sub"] == str(expected_user_id)

    @pytest.mark.settings(
        PASSWORDLESS_LOGIN_PRIVATE_KEY=private_pem_file, PASSWORDLESS_LOGIN_PUBLIC_KEY=public_pem_file
    )
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.execute")
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.delete")
    @mock.patch("pcapi.flask_app.redis.client.Pipeline.get")
    @mock.patch("pcapi.flask_app.redis.client.Redis.set")
    @mock.patch("uuid.uuid4", return_value=uuid.uuid4())
    def test_aborting_auto_login_when_token_payload_and_redis_queue_mismatch(
        self, mocked_uuid, mocked_redis_set, mocked_pipeline_get, mocked_pipeline_del, mocked_pipeline_execute, caplog
    ):
        expected_jti = str(mocked_uuid())
        expected_ttl = timedelta(hours=8)
        expected_user_id = 1
        wrong_user_id = 2
        key_suffix = hashlib.sha256(
            json.dumps({"user_id": str(expected_user_id), "jti": expected_jti}).encode()
        ).hexdigest()
        redis_key = token_tools.PASSWORDLESS_REDIS_KEY_TEMPLATE % {
            "type_": token_tools.TokenType.PASSWORDLESS_LOGIN.value,
            "key_suffix": key_suffix,
        }
        token = token_tools.create_passwordless_login_token(expected_user_id, expected_ttl)

        mocked_redis_set.assert_called_once_with(
            redis_key, json.dumps({"user_id": str(expected_user_id), "jti": expected_jti}), ex=expected_ttl
        )

        mocked_pipeline_execute.return_value = [f'{{"user_id": "{wrong_user_id}", "jti": "{expected_jti}"}}', 1]

        with pytest.raises(InvalidToken), caplog.at_level(logging.ERROR):
            token_tools.validate_passwordless_token(token)

        mocked_pipeline_get.assert_called_once_with(redis_key)
        mocked_pipeline_del.assert_called_once_with(redis_key)
        mocked_pipeline_execute.assert_called_once()

        assert (
            caplog.records[0].message
            == f"Mismatch between the payload of an authentic passwordless login token and the corresponding redis value. Token: {token}"
        )

    @pytest.mark.settings(
        PASSWORDLESS_LOGIN_PRIVATE_KEY=private_pem_file, PASSWORDLESS_LOGIN_PUBLIC_KEY=public_pem_file
    )
    @mock.patch("uuid.uuid4", return_value=uuid.uuid4())
    def test_send_passwordless_login_token_twice(self, mocked_uuid):
        expected_jti = str(mocked_uuid())
        expected_ttl = timedelta(hours=8)
        expected_user_id = 1
        token = token_tools.create_passwordless_login_token(expected_user_id, expected_ttl)

        payload = token_tools.validate_passwordless_token(token)

        assert payload["jti"] == expected_jti
        assert payload["exp"] - payload["iat"] == 8 * 3600
        assert payload["sub"] == str(expected_user_id)

        with pytest.raises(InvalidToken):
            payload = token_tools.validate_passwordless_token(token)
