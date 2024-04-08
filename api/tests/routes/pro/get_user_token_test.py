import pytest

from pcapi.core import token as token_utils
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.users import constants


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_activation_token_exists(self, client):
        # given
        user_offerer = offerers_factories.UserOffererFactory()
        token = token_utils.Token.create(
            token_utils.TokenType.RESET_PASSWORD,
            constants.RESET_PASSWORD_TOKEN_LIFE_TIME,
            user_offerer.user.id,
        )

        # when
        request = client.get("/users/token/" + token.encoded_token)

        # then
        assert request.status_code == 204


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_activation_token_does_not_exist(self, client):
        # when
        request = client.get("/users/token/3YU26FS")

        # then
        assert request.status_code == 404
