from datetime import datetime
from datetime import timedelta
from unittest import mock

import fakeredis
from freezegun import freeze_time
import pytest

from pcapi.core import token as token_tools
from pcapi.core.users.exceptions import InvalidToken
from pcapi.core.users.utils import encode_jwt_payload


class TokenTest:
    token_type = token_tools.TokenType.EMAIL_CHANGE_CONFIRMATION
    ttl = timedelta(days=1)
    data = {"key1": "value1", "key2": "value2"}
    user_id = 4597

    def test_creat_token_then_get_data(self):
        """testing the creation of a token and getting the data"""
        with freeze_time("2021-01-01"):
            token = token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
            assert token.data == self.data
            assert token.user_id == self.user_id
            assert token.type_ == self.token_type
            assert token.encoded_token is not None
            assert token_tools.Token.get_expiration_date(self.token_type, self.user_id) == datetime.utcnow() + self.ttl

    def test_create_token_with_no_data_no_ttl(self):
        """no data, no user and no ttl are provided"""
        with freeze_time("2021-01-01"):
            token = token_tools.Token.create(self.token_type, None, self.user_id)
            assert not token.data and isinstance(token.data, dict)
            assert token.user_id == self.user_id
            assert token.type_ == self.token_type
            assert token.encoded_token is not None
            assert token_tools.Token.get_expiration_date(self.token_type, self.user_id) is None

    def test_token_from_encoded_token_and_get_data(self):
        """if the token is created from an encoded token, the data should be the same"""
        with freeze_time("2021-01-01"):
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
            assert token_tools.Token.get_expiration_date(self.token_type, self.user_id) == datetime.utcnow() + self.ttl

    def test_get_expiration_date_used_token(self):
        """if the token has been expired using expire_token, the expiration date should be None"""
        token = token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
        token.expire()
        assert token_tools.Token.get_expiration_date(self.token_type, self.user_id) is None

    def test_get_expiration_date_expired_token(self):
        """if the token has been expired using expire_token, the expiration date should be None"""
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            with freeze_time("2021-01-01"):
                token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
            with freeze_time("2021-01-03"):
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
            with freeze_time("2021-01-01"):
                token = token_tools.Token.create(self.token_type, self.ttl, self.user_id, self.data)
            with freeze_time("2021-01-03"):
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
