import pytest

import pcapi.core.offerers.factories as offerers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class VenueStatisticsTest:
    def test_get_statistics(self, client):
        # no need to run deep into checks since the Clickhouse where
        # all the real computations happens is mocked.
        venue = offerers_factories.VenueFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)

        response = client.with_session_auth(email=user_offerer.user.email).get(f"/venues/{venue.id}/stats")
        assert response.status_code == 200
        assert response.json == {
            "incomeByYear": {
                "2024": {"revenue": {"collective": 12.12, "individual": 12.12, "total": 24.24}},
                "2022": {"revenue": {"collective": 22.12, "individual": 22.12, "total": 44.24}},
                "2023": {},
            }
        }

    def test_user_without_access_to_venue_should_get_an_error(self, client):
        venue = offerers_factories.VenueFactory()
        user_offerer = offerers_factories.UserOffererFactory()

        response = client.with_session_auth(email=user_offerer.user.email).get(f"/venues/{venue.id}/stats")
        assert response.status_code == 403

    def test_unauthenticated_user_should_get_an_error(self, client):
        venue = offerers_factories.VenueFactory()
        offerers_factories.UserOffererFactory(offerer=venue.managingOfferer)

        response = client.get(f"/venues/{venue.id}/stats")
        assert response.status_code == 401

    def test_unknown_venue_should_return_an_error(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        response = client.with_session_auth(email=user_offerer.user.email).get("/venues/0/stats")
        assert response.status_code == 404
