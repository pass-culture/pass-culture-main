import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.token as token_utils


class ValidateUserTest:
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
