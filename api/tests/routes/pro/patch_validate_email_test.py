from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import Any

import jwt
import pytest

from pcapi import settings
import pcapi.core.users.factories as users_factories
from pcapi.core.users.utils import ALGORITHM_HS_256


pytestmark = pytest.mark.usefixtures("db_session")


class PatchValidateEmailTest:
    origin_email = "email@example.com"
    new_email = "update_" + origin_email

    def generate_token(self, email: str, expiration_delta: date = None) -> str:
        if not expiration_delta:
            expiration_delta = timedelta(hours=1)

        expiration = int((datetime.utcnow() + expiration_delta).timestamp())
        token_payload = {"exp": expiration, "current_email": email, "new_email": self.new_email}
        token = jwt.encode(
            token_payload,
            settings.JWT_SECRET_KEY,  # type: ignore # known as str in build assertion
            algorithm=ALGORITHM_HS_256,
        )
        return token

    def test_validate_email(self, client: Any) -> None:
        pro = users_factories.ProFactory(email=self.origin_email)
        token = self.generate_token(pro.email)
        response = client.patch("/users/validate_email", json={"token": token})

        assert response.status_code == 204
        assert pro.email == self.new_email

    def test_expired_token(self, client: Any) -> None:
        pro = users_factories.ProFactory(email=self.origin_email)
        token = self.generate_token(pro.email, expiration_delta=-timedelta(hours=1))
        response = client.patch("/users/validate_email", json={"token": token})

        assert response.status_code == 400
        assert response.json["global"] == ["Token invalide"]
        assert pro.email == self.origin_email

    def test_email_invalid(self, client: Any) -> None:
        token = self.generate_token("not_an_email")
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

        token = self.generate_token(pro.email)
        response = client.patch("/users/validate_email", json={"token": token})

        assert response.status_code == 204

        assert pro_changing.email == self.origin_email
