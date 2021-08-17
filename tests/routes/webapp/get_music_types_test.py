import pytest

from pcapi.core.users import factories as users_factories
from pcapi.domain.music_types import music_types

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_list_music_types(self, app):
        # given
        user = users_factories.UserFactory()

        # when
        response = TestClient(app.test_client()).with_session_auth(user.email).get("/musicTypes")

        # then
        response_json = response.json
        assert response.status_code == 200
        assert response_json == music_types
