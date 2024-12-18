import pytest

from pcapi.core import testing
from pcapi.core import token as token_utils
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.users import constants


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_activation_token_exists(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        token = token_utils.Token.create(
            token_utils.TokenType.RESET_PASSWORD,
            constants.RESET_PASSWORD_TOKEN_LIFE_TIME,
            user_offerer.user.id,
        )
        with testing.assert_num_queries(0):
            request = client.get("/pro/users/token/" + token.encoded_token)
            assert request.status_code == 204


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_activation_token_does_not_exist(self, client):
        with testing.assert_num_queries(0):
            request = client.get("/pro/users/token/3YU26FS")
            assert request.status_code == 404
