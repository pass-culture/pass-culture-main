import pytest

from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class E2EOfferTest:
    endpoint_url = "/e2e/venue"

    def _base_payload(self):
        return {"name": "Cinérama", "activity": "CINEMA"}

    def test_unauthorized(self, client):
        response = client.post(self.endpoint_url, self._base_payload())
        assert response.status_code == 401

    def test_forbidden(self, client, settings):
        settings.E2E_API_KEY = "titi"
        response = client.post(self.endpoint_url, json={}, headers={"x-api-key": "toto"})
        assert response.status_code == 401

    def test_create_venue(self, auth_client):
        response = auth_client.post(self.endpoint_url, self._base_payload())
        assert response.status_code == 200

        venues = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.name == "Cinérama").all()

        assert len(venues) == 1
        venue = venues[0]
        assert venue.name == "Cinérama"
        assert venue.activity == offerers_models.Activity.CINEMA

        assert response.json["id"] == venue.id
        assert response.json["name"] == "Cinérama"
        assert response.json["activity"] == "CINEMA"
        assert response.json["timezone"] == "Europe/Paris"
