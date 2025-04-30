import jwt
import pytest

from pcapi import settings
from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class OffererStatsTest:
    num_queries = testing.AUTHENTICATION_QUERIES
    num_queries += 1  # select offerer
    num_queries += 1  # check user_offerer exists

    def test_allowed_user(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer

        client = client.with_session_auth(user_offerer.user.email)
        offerer_id = offerer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{offerer_id}/dashboard")
            assert response.status_code == 200

        url = response.json["dashboardUrl"]
        token = url.split("/")[3].split("#")[0]
        payload = jwt.decode(token, settings.METABASE_SECRET_KEY, algorithms="HS256")

        assert payload["params"]["siren"] == [offerer.siren]
        assert payload["params"]["venueid"] == []

    def test_forbidden_user(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        forbidden_offerer = offerers_factories.OffererFactory()
        forbidden_offerer_id = forbidden_offerer.id
        client = client.with_session_auth(user_offerer.user.email)
        with testing.assert_num_queries(self.num_queries):
            response = client.get(f"/offerers/{forbidden_offerer_id}/dashboard")
            assert response.status_code == 403


class VenueStatsTest:
    def test_allowed_user(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)
        venue_id = venue.id
        client = client.with_session_auth(user_offerer.user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select venue
        num_queries += 1  # check user_offerer exists
        num_queries += 1  # select offerer
        with testing.assert_num_queries(num_queries):
            response = client.get(f"/venues/{venue_id}/dashboard")
            assert response.status_code == 200

        url = response.json["dashboardUrl"]
        token = url.split("/")[3].split("#")[0]
        payload = jwt.decode(token, settings.METABASE_SECRET_KEY, algorithms="HS256")

        assert payload["params"]["siren"] == [offerer.siren]
        assert payload["params"]["venueid"] == [str(venue.id)]

    def test_forbidden_user(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        forbidden_venue = offerers_factories.VenueFactory()

        forbidden_venue_id = forbidden_venue.id
        client = client.with_session_auth(user_offerer.user.email)
        num_queries = testing.AUTHENTICATION_QUERIES
        num_queries += 1  # select venue
        num_queries += 1  # check user_offerer exists
        with testing.assert_num_queries(num_queries):
            response = client.get(f"/venues/{forbidden_venue_id}/dashboard")
            assert response.status_code == 403
