import pytest

from pcapi.core.offerers.factories import VenueTypeFactory
from pcapi.core.users.factories import UserFactory

from tests.conftest import TestClient


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def when_the_user_is_not_authenticated(self, app):
        # When
        response = TestClient(app.test_client()).get("/venue-types")

        # then
        assert response.status_code == 401


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_the_user_is_authenticated(self, app):
        # Given
        user = UserFactory()
        VenueTypeFactory(label="Centre culturel", id=1)
        VenueTypeFactory(label="Musée", id=2)

        # When
        response = TestClient(app.test_client()).with_auth(user.email).get("/venue-types")

        # then
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json == [{"id": "AE", "label": "Centre culturel"}, {"id": "A9", "label": "Musée"}]
