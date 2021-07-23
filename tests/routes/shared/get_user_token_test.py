import pytest

from pcapi.core.users import factories as users_factories

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_activation_token_exists(self, app):
        # given
        token = "U2NCXTNB2"
        user = users_factories.BeneficiaryFactory()
        users_factories.ResetPasswordToken(value=token, user=user)

        # when
        request = TestClient(app.test_client()).get("/users/token/" + token)

        # then
        assert request.status_code == 200
        assert request.json == {}


class Returns404Test:
    @pytest.mark.usefixtures("db_session")
    def when_activation_token_does_not_exist(self, app):
        # when
        request = TestClient(app.test_client()).get("/users/token/3YU26FS")

        # then
        assert request.status_code == 404
