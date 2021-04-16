from unittest.mock import patch

import pytest

from pcapi.core.users.models import User
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.repository import repository

from tests.conftest import TestClient


class Patch:
    class Returns204:
        @pytest.mark.usefixtures("db_session")
        def expect_validation_token_to_be_set_to_none_and_email_validated(self, app):
            # Given
            user = create_user()
            user.generate_validation_token()
            repository.save(user)
            user_id = user.id

            # When
            response = TestClient(app.test_client()).patch(
                f"/validate/user/{user.validationToken}", headers={"origin": "http://localhost:3000"}
            )

            # Then
            validated_user = User.query.get(user_id)
            assert response.status_code == 204
            assert validated_user.isValidated
            assert validated_user.isEmailValidated

        @pytest.mark.usefixtures("db_session")
        @patch("pcapi.routes.pro.validate.maybe_send_offerer_validation_email", return_value=True)
        def test_maybe_send_offerer_validation_email(self, mock_maybe_send_offerer_validation_email, app):
            # Given
            pro = create_user()
            offerer = create_offerer(siren="775671464")
            user_offerer = create_user_offerer(pro, offerer)

            pro.generate_validation_token()

            repository.save(user_offerer)

            # When
            response = TestClient(app.test_client()).patch(
                f"/validate/user/{pro.validationToken}", headers={"origin": "http://localhost:3000"}
            )

            # Then
            assert response.status_code == 204
            mock_maybe_send_offerer_validation_email.assert_called_once_with(offerer, user_offerer)


class Returns404:
    @pytest.mark.usefixtures("db_session")
    def when_validation_token_is_not_found(self, app):
        # Given
        random_token = "0987TYGHHJMJ"

        # When
        response = TestClient(app.test_client()).patch(
            f"/validate/user/{random_token}", headers={"origin": "http://localhost:3000"}
        )

        # Then
        assert response.status_code == 404
        assert response.json["global"] == ["Ce lien est invalide"]
