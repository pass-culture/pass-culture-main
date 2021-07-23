import pytest

from pcapi.core.users import factories as users_factories
from pcapi.domain.show_types import show_types

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_list_show_types(self, app):
        # given
        user = users_factories.UserFactory()

        # when
        response = TestClient(app.test_client()).with_auth(user.email).get("/showTypes")

        # then
        response_json = response.json
        assert response.status_code == 200
        assert response_json == show_types
