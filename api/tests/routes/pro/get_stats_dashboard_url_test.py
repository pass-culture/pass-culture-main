import jwt
import pytest

from pcapi import settings
import pcapi.core.offerers.factories as offerers_factories


class OffererStatsTest:
    def test_allowed_user(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/offerers/{offerer.id}/dashboard")

        url = response.json["dashboardUrl"]
        token = url.split("/")[3].split("#")[0]
        payload = jwt.decode(token, settings.METABASE_SECRET_KEY, algorithms="HS256")

        assert response.status_code == 200
        assert payload["params"]["siren"] == [offerer.siren]
        assert payload["params"]["venueid"] == []

    def test_forbidden_user(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        forbidden_offerer = offerers_factories.OffererFactory()

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/offerers/{forbidden_offerer.id}/dashboard")

        assert response.status_code == 403


class VenueStatsTest:
    def test_allowed_user(self, client):
        venue = offerers_factories.VenueFactory()
        offerer = venue.managingOfferer
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/venues/{venue.id}/dashboard")

        url = response.json["dashboardUrl"]
        token = url.split("/")[3].split("#")[0]
        payload = jwt.decode(token, settings.METABASE_SECRET_KEY, algorithms="HS256")

        assert response.status_code == 200
        assert payload["params"]["siren"] == [offerer.siren]
        assert payload["params"]["venueid"] == [str(venue.id)]

    def test_forbidden_user(self, client):
        user_offerer = offerers_factories.UserOffererFactory()
        forbidden_venue = offerers_factories.VenueFactory()

        client = client.with_session_auth(user_offerer.user.email)
        response = client.get(f"/venues/{forbidden_venue.id}/dashboard")

        assert response.status_code == 403
