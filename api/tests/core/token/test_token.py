from datetime import datetime
from datetime import timedelta
from unittest import mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import fakeredis
import pytest
import time_machine

from pcapi import settings
from pcapi.core import token as token_tools
from pcapi.core.testing import override_settings
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
        public_exponent=65537,
        key_size=4096,
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
        public_exponent=65537,
        key_size=4096,
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

    @override_settings(DISCORD_JWT_PRIVATE_KEY=private_key_pem, DISCORD_JWT_PUBLIC_KEY=public_key_pem)
    def test_create_token_then_get_data(self):
        """testing the creation of a token and getting the data"""
        token = token_tools.AsymetricToken.create(
            self.token_type, settings.DISCORD_JWT_PRIVATE_KEY, settings.DISCORD_JWT_PUBLIC_KEY, self.ttl, self.data
        )
        assert token.data == self.data
        assert token.type_ == self.token_type
        assert token.encoded_token is not None
        assert token_tools.AsymetricToken.get_expiration_date(
            self.token_type,
            token.key_suffix,
        ).isoformat(
            timespec="hours"
        ) == (datetime.utcnow() + self.ttl).isoformat(timespec="hours")

    @override_settings(DISCORD_JWT_PRIVATE_KEY=private_key_pem, DISCORD_JWT_PUBLIC_KEY=public_key_pem)
    def test_create_token_with_non_corresponding_keys(self):
        """if the keys do not correspond, an exception should be raised"""

        with pytest.raises(InvalidToken):
            token_tools.AsymetricToken.create(
                self.token_type, settings.DISCORD_JWT_PRIVATE_KEY, self.wrong_public_key, self.ttl, self.data
            )

    @override_settings(DISCORD_JWT_PRIVATE_KEY=private_key_pem, DISCORD_JWT_PUBLIC_KEY=public_key_pem)
    def test_token_from_encoded_token_and_get_data(self):
        """if the token is created from an encoded token, the data should be the same"""
        old_token = token_tools.AsymetricToken.create(
            self.token_type,
            settings.DISCORD_JWT_PRIVATE_KEY,
            settings.DISCORD_JWT_PUBLIC_KEY,
            self.ttl,
            self.data,
        )
        token = token_tools.AsymetricToken.load_without_checking(
            old_token.encoded_token, settings.DISCORD_JWT_PUBLIC_KEY
        )
        assert token.data == old_token.data
        assert token.type_ == old_token.type_
        assert token.encoded_token == old_token.encoded_token
        assert token_tools.AsymetricToken.get_expiration_date(self.token_type, token.key_suffix).isoformat(
            timespec="hours"
        ) == (datetime.utcnow() + self.ttl).isoformat(timespec="hours")

    @override_settings(DISCORD_JWT_PRIVATE_KEY=private_key_pem, DISCORD_JWT_PUBLIC_KEY=public_key_pem)
    def test_load_without_checking_wrong_public_key(self):
        """if the token has the wrong signature, an exception should be raised"""
        old_token = token_tools.AsymetricToken.create(
            self.token_type,
            settings.DISCORD_JWT_PRIVATE_KEY,
            settings.DISCORD_JWT_PUBLIC_KEY,
            self.ttl,
            self.data,
        )
        with pytest.raises(InvalidToken):
            token_tools.AsymetricToken.load_without_checking(
                old_token.encoded_token,
                self.wrong_public_key,
            )
