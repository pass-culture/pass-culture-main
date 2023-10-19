from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import Any
from unittest import mock

import fakeredis
from freezegun import freeze_time
import jwt
import pytest

from pcapi import settings
import pcapi.core.token as token_utils
from pcapi.core.users import constants
import pcapi.core.users.factories as users_factories
from pcapi.core.users.utils import ALGORITHM_HS_256


pytestmark = pytest.mark.usefixtures("db_session")


# TODO (yacine-pc) this class will be removed in PC-25024
class LegacyPatchValidateEmailTest:
    origin_email = "email@example.com"
    new_email = "update_" + origin_email

    def generate_token(self, email: str, user_id: int, expiration_delta: date = None) -> str:
        if not expiration_delta:
            expiration_delta = timedelta(hours=1)

        expiration = int((datetime.utcnow() + expiration_delta).timestamp())
        token_payload = {"exp": expiration, "current_email": email, "new_email": self.new_email, "user_id": user_id}
        token = jwt.encode(
            token_payload,
            settings.JWT_SECRET_KEY,
            algorithm=ALGORITHM_HS_256,
        )
        return token

    def test_validate_email(self, client: Any) -> None:
        pro = users_factories.ProFactory(email=self.origin_email)
        token = self.generate_token(pro.email, pro.id)
        response = client.patch("/users/validate_email", json={"token": token})

        assert response.status_code == 204
        assert pro.email == self.new_email

    def test_expired_token(self, client: Any) -> None:
        pro = users_factories.ProFactory(email=self.origin_email)
        token = self.generate_token(pro.email, pro.id, expiration_delta=-timedelta(hours=1))
        response = client.patch("/users/validate_email", json={"token": token})

        assert response.status_code == 400
        assert response.json["global"] == ["Token invalide"]
        assert pro.email == self.origin_email

    def test_email_invalid(self, client: Any) -> None:
        pro = users_factories.ProFactory()
        token = self.generate_token("not_an_email", pro.id)
        response = client.patch("/users/validate_email", json={"token": token})

        assert response.status_code == 400
        assert response.json["global"] == ["Adresse email invalide"]

    def test_email_exists(self, client: Any) -> None:
        """
        Test that if the email already exists, an OK response is sent
        but nothing is changed (avoid user enumeration).
        """
        pro_changing = users_factories.ProFactory(email=self.origin_email)
        pro = users_factories.ProFactory(email=self.new_email, isEmailValidated=True)

        token = self.generate_token(pro.email, pro.id)
        response = client.patch("/users/validate_email", json={"token": token})

        assert response.status_code == 204

        assert pro_changing.email == self.origin_email

    def test_email_invalid_user_id(self, client: Any) -> None:
        """
        Test that if the email already exists
        """
        pro_changing = users_factories.ProFactory(email=self.origin_email)
        pro = users_factories.ProFactory(email=self.new_email, isEmailValidated=True)

        token = self.generate_token(pro_changing.email, pro.id)

        response = client.patch("/users/validate_email", json={"token": token})
        assert response.status_code == 400
        assert pro_changing.email == self.origin_email


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
            with freeze_time("2023-10-10 12:00:00"):
                pro = users_factories.ProFactory(email=self.current_email)
                token = token_utils.Token.create(
                    token_utils.TokenType.EMAIL_CHANGE_VALIDATION,
                    constants.EMAIL_CHANGE_TOKEN_LIFE_TIME,
                    user_id=pro.id,
                    data=self.token_data,
                )
            with freeze_time("2023-10-16 13:00:00"):
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
