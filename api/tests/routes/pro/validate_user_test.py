import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.token as token_utils


class ValidateUserTest:
    @pytest.mark.usefixtures("db_session")
    def test_validate_user_token(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__isEmailValidated=False)
        token = token_utils.Token.create(token_utils.TokenType.EMAIL_VALIDATION, None, user_id=user_offerer.user.id)
        response = client.patch(f"/pro/validate/user/{token.encoded_token}")
        assert response.status_code == 204
        assert user_offerer.user.isEmailValidated

    @pytest.mark.usefixtures("db_session")
    def test_fail_if_unknown_token(self, client):
        response = client.patch("/pro/validate/user/unknown-token")

        assert response.status_code == 404
        assert response.json["global"] == ["Ce lien est invalide"]
