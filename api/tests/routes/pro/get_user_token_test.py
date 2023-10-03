import pytest

from pcapi.core.users import factories as users_factories


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_activation_token_exists(self, client):
        # given
        token = "U2NCXTNB2"
        user = users_factories.BeneficiaryGrant18Factory()
        users_factories.PasswordResetTokenFactory(value=token, user=user)

        # when
        request = client.get("/users/token/" + token)

        # then
        assert request.status_code == 204


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_activation_token_does_not_exist(self, client):
        # when
        request = client.get("/users/token/3YU26FS")

        # then
        assert request.status_code == 404
