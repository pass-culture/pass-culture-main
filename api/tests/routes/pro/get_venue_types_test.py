import pytest

from pcapi.core.offerers.models import VENUE_TYPE_CODE_MAPPING
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
    def when_the_user_is_authenticated(self, client):
        # Given
        user = UserFactory()

        # When
        response = client.with_session_auth(user.email).get("/venue-types")

        # then
        assert response.status_code == 200

        expected_venue_types = [{"id": code_id, "label": label} for code_id, label in VENUE_TYPE_CODE_MAPPING.items()]
        expected_venue_types = sorted(expected_venue_types, key=lambda item: item["id"])

        response_venue_types = sorted(response.json, key=lambda item: item["id"])
        assert response_venue_types == expected_venue_types
