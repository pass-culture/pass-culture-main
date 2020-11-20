from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import jwt
import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users.api import generate_and_save_token
from pcapi.core.users.api import get_user_with_valid_token
from pcapi.core.users.models import ALGORITHM_HS_256
from pcapi.core.users.models import Token
from pcapi.core.users.models import TokenType
from pcapi.flask_app import jwt_secret_key
from pcapi.repository import repository

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class GenerateAndSaveTokenTest:
    def test_generate_and_save_token(self, app):
        user = users_factories.UserFactory(email="py@test.com")
        token_type = TokenType.RESET_PASSWORD
        life_time = timedelta(hours=24)

        generated_token = generate_and_save_token(user, token_type, life_time)

        saved_token = Token.query.filter_by(user=user).first()

        assert generated_token.id == saved_token.id
        assert saved_token.type == token_type
        decoded = jwt.decode(saved_token.value, jwt_secret_key, algorithms=ALGORITHM_HS_256)
        assert decoded["userId"] == user.id
        assert decoded["type"] == token_type.value
        assert decoded["exp"] is not None

        with freeze_time(datetime.now() + timedelta(hours=48)):
            with pytest.raises(jwt.exceptions.ExpiredSignatureError):
                jwt.decode(saved_token.value, jwt_secret_key, algorithms=ALGORITHM_HS_256)

        # ensure token is not valid for authentication
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {saved_token.value}"}
        response = test_client.get("/native/v1/protected")
        assert response.status_code == 422

    def test_generate_and_save_token_without_expiration_date(self):
        user = users_factories.UserFactory(email="py@test.com")
        token_type = TokenType.RESET_PASSWORD

        generate_and_save_token(user, token_type)

        generated_token = Token.query.filter_by(user=user).first()

        assert generated_token.type == token_type
        assert generated_token.expirationDate is None

        decoded = jwt.decode(generated_token.value, jwt_secret_key, algorithms=ALGORITHM_HS_256)

        assert decoded["userId"] == user.id
        assert decoded["type"] == token_type.value
        assert "exp" not in decoded

    def test_generate_and_save_token_with_wrong_type(self):
        user = users_factories.UserFactory(email="py@test.com")
        token_type = "not-enum-type"

        with pytest.raises(AttributeError):
            generate_and_save_token(user, token_type)


class ValidateJwtTokenTest:
    token_value = jwt.encode(
        {"pay": "load"},
        jwt_secret_key,
        algorithm=ALGORITHM_HS_256,
    ).decode("ascii")

    def test_get_user_with_valid_token(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD
        expiration_date = datetime.now() + timedelta(hours=24)

        saved_token = Token(
            from_dict={
                "userId": user.id,
                "value": self.token_value,
                "type": token_type,
                "expirationDate": expiration_date,
            }
        )
        repository.save(saved_token)

        associated_user = get_user_with_valid_token(self.token_value, [token_type, "other-allowed-type"])

        assert associated_user.id == user.id

    def test_get_user_with_valid_token_without_expiration_date(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD

        saved_token = Token(from_dict={"userId": user.id, "value": self.token_value, "type": token_type})
        repository.save(saved_token)

        associated_user = get_user_with_valid_token(self.token_value, [token_type])

        assert associated_user.id == user.id

    def test_get_user_with_valid_token_wrong_token(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD

        saved_token = Token(from_dict={"userId": user.id, "value": self.token_value, "type": token_type})
        repository.save(saved_token)

        associated_user = get_user_with_valid_token("wrong-token-value", [token_type])

        assert associated_user is None

    def test_get_user_with_valid_token_wrong_type(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD

        saved_token = Token(from_dict={"userId": user.id, "value": self.token_value, "type": token_type})
        repository.save(saved_token)

        assert Token.query.filter_by(value=self.token_value).first() is not None

        associated_user = get_user_with_valid_token(self.token_value, ["other_type"])

        assert associated_user is None

    def test_get_user_with_valid_token_with_expired_date(self):
        user = users_factories.UserFactory()
        token_type = TokenType.RESET_PASSWORD

        saved_token = Token(
            from_dict={
                "userId": user.id,
                "value": self.token_value,
                "type": token_type,
                "expirationDate": datetime.now() - timedelta(hours=24),
            }
        )
        repository.save(saved_token)

        assert Token.query.filter_by(value=self.token_value).first() is not None

        associated_user = get_user_with_valid_token(self.token_value, [token_type])

        assert associated_user is None
