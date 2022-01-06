import pytest

from pcapi.core.users import factories as users_factories
from pcapi.models.user_session import UserSession

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def expect_the_existing_user_session_to_be_deleted_deleted(self, app):
        # given
        user = users_factories.ProFactory(email="test@mail.com")
        auth_request = TestClient(app.test_client()).with_session_auth(email=user.email)

        assert auth_request.get("/venues").status_code == 200

        # when
        response = auth_request.get("/users/signout")

        # then
        assert response.status_code == 200
        assert response.json == {"global": "Déconnecté"}
        session = UserSession.query.filter_by(userId=user.id).first()
        assert session is None
