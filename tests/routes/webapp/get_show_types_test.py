import pytest

from pcapi.domain.show_types import show_types
from pcapi.model_creators.generic_creators import create_user
from pcapi.repository import repository

from tests.conftest import TestClient


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_list_show_types(self, app):
            # given
            user = create_user()
            repository.save(user)

            # when
            response = TestClient(app.test_client()).with_auth(user.email).get("/showTypes")

            # then
            response_json = response.json
            assert response.status_code == 200
            assert response_json == show_types
