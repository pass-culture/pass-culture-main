import pytest

from pcapi.core.offers.factories import OfferFactory
from pcapi.models.offer_type import EventType

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class OffersTest:
    def test_get_offer(self, app):
        offer_type = EventType.CINEMA

        offer = OfferFactory(type=str(offer_type), isDuo=True)

        response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer.id}")

        assert response.status_code == 200
        assert response.json == {
            "category": {"label": "Cinéma", "value": str(offer_type)},
            "id": offer.id,
            "imageUrl": None,
            "isDuo": True,
            "name": offer.name,
            "venue": {
                "city": offer.venue.city,
                "name": offer.venue.name,
                "offerer": {"name": offer.venue.managingOfferer.name},
                "publicName": offer.venue.publicName,
            },
        }

    def test_get_offer_not_found(self, app):
        response = TestClient(app.test_client()).get("/native/v1/offer/1")

        assert response.status_code == 404
