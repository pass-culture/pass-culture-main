import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class E2EOfferTest:
    def test_unauthorized(self, client):
        response = client.post("/e2e/offer", {"name": "Test Offer", "subcategory_id": "SEANCE_CINE", "price": 13.2})
        assert response.status_code == 401

    def test_forbidden(self, client, settings):
        settings.E2E_API_KEY = "titi"
        response = client.post("/e2e/offer", json={}, headers={"x-api-key": "toto"})
        assert response.status_code == 401

    def test_create_offer(self, auth_client):
        response = auth_client.post("/e2e/offer", {"name": "Test Offer", "subcategory_id": "SEANCE_CINE", "price": 8.2})
        assert response.status_code == 200

        offers = db.session.query(offers_models.Offer).all()

        assert len(offers) == 1
        offer = offers[0]
        assert offer.publicationDatetime is not None
        assert offer.name == "Test Offer"
        assert offer.subcategoryId == "SEANCE_CINE"

        assert response.json["id"] == offer.id
        assert response.json["name"] == "Test Offer"
        assert response.json["subcategoryId"] == "SEANCE_CINE"
        assert response.json["venueId"] == offer.venueId

    def test_create_offer_missing_subcategory(self, auth_client):
        response = auth_client.post("/e2e/offer", {"name": "Test Offer", "price": 8.2})

        assert response.status_code == 400
        assert response.json == {"subcategory_id": ["Information obligatoire"]}

    def test_create_offer_invalid_subcategory(self, auth_client):
        response = auth_client.post("/e2e/offer", {"name": "Test Offer", "price": 4.5, "subcategory_id": "RENCONTRE"})

        assert response.status_code == 400
        assert response.json == {"subcategory_id": ["Not a valid choice."]}


class E2EOfferDeactivateTest:
    def test_unauthorized(self, client):
        offer = offers_factories.OfferFactory()
        response = client.post(f"/e2e/offer/{offer.id}/deactivate", json={})
        assert response.status_code == 401

    def test_forbidden(self, client, settings):
        settings.E2E_API_KEY = "titi"
        offer = offers_factories.OfferFactory()
        response = client.post(f"/e2e/offer/{offer.id}/deactivate", json={}, headers={"x-api-key": "toto"})
        assert response.status_code == 401

    def test_deactivate_offer(self, auth_client):
        offer = offers_factories.OfferFactory()
        assert offer.publicationDatetime is not None
        response = auth_client.post(f"/e2e/offer/{offer.id}/deactivate", json={})
        assert response.status_code == 200, response.json
        assert offer.publicationDatetime is None
