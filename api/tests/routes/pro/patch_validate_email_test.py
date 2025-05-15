from typing import Any
from unittest import mock

import fakeredis
import pytest
import time_machine

import pcapi.core.token as token_utils
import pcapi.core.users.factories as users_factories
from pcapi.core.users import constants


pytestmark = pytest.mark.usefixtures("db_session")


class TokenPatchValidateEmailTest:
    current_email = "email@example.com"
    new_email = "update_" + current_email
    token_data = {
        "current_email": current_email,
        "new_email": new_email,
    }

    def test_validate_email(self, client: Any) -> None:
        pro = users_factories.ProFactory(email=self.current_email)

        token = token_utils.Token.create(
            token_utils.TokenType.EMAIL_CHANGE_VALIDATION,
            ttl=constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
            user_id=pro.id,
            data=self.token_data,
        )
        response = client.patch("/users/validate_email", json={"token": token.encoded_token})

        assert response.status_code == 204
        assert pro.email == self.new_email

    def test_expired_token(self, client: Any) -> None:
        with mock.patch("flask.current_app.redis_client", fakeredis.FakeStrictRedis()):
            with time_machine.travel("2023-10-10 12:00:00"):
                pro = users_factories.ProFactory(email=self.current_email)
                token = token_utils.Token.create(
                    token_utils.TokenType.EMAIL_CHANGE_VALIDATION,
                    constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
                    user_id=pro.id,
                    data=self.token_data,
                )
            with time_machine.travel("2023-10-16 13:00:00"):
                response = client.patch("/users/validate_email", json={"token": token.encoded_token})

                assert response.status_code == 400
                assert response.json["global"] == ["Token invalide"]
                assert pro.email == self.current_email

    def test_email_exists(self, client: Any) -> None:
        """
        Test that if the email already exists, an OK response is sent
        but nothing is changed (avoid user enumeration).
        """
        pro_changing = users_factories.ProFactory(email=self.current_email)
        users_factories.ProFactory(email=self.new_email, isEmailValidated=True)
        token = token_utils.Token.create(
            token_utils.TokenType.EMAIL_CHANGE_VALIDATION,
            constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
            user_id=pro_changing.id,
            data=self.token_data,
        )

        response = client.patch("/users/validate_email", json={"token": token.encoded_token})

        assert response.status_code == 204
        assert pro_changing.email == self.current_email

    def test_email_invalid_user_id(self, client: Any) -> None:
        """
        Test that if the email already exists
        """
        pro_changing = users_factories.ProFactory(email=self.current_email)
        pro = users_factories.ProFactory(email=self.new_email, isEmailValidated=True)

        token = token_utils.Token.create(
            token_utils.TokenType.EMAIL_CHANGE_VALIDATION,
            constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
            user_id=pro.id,
            data=self.token_data,
        )

        response = client.patch("/users/validate_email", json={"token": token})
        assert response.status_code == 400
        assert pro_changing.email == self.current_email
