import pytest

from pcapi.core import testing
from pcapi.core.offerers.models import VenueTypeCode
from pcapi.core.users.factories import UserFactory


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def when_the_user_is_not_authenticated(self, client):
        with testing.assert_num_queries(0):
            response = client.get("/pro/venue-types")
            assert response.status_code == 401


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_the_user_is_authenticated(self, client):
        user = UserFactory()

        client = client.with_session_auth(user.email)
        with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
            response = client.get("/pro/venue-types")
            assert response.status_code == 200

        expected_venue_types = [{"id": venue_type.name, "label": venue_type.value} for venue_type in VenueTypeCode]
        expected_venue_types = sorted(expected_venue_types, key=lambda item: item["id"])

        response_venue_types = sorted(response.json, key=lambda item: item["id"])
        assert response_venue_types == expected_venue_types
