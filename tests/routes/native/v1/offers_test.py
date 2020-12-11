from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.models.offer_type import EventType

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class OffersTest:
    def test_get_offer(self, app):
        offer_type = EventType.CINEMA
        offer = OfferFactory(type=str(offer_type), isDuo=True, withdrawalDetails="modalité de retrait")

        bookableStock = EventStockFactory(offer=offer, price=12.34)
        EventStockFactory(offer=offer, beginningDatetime=datetime.utcnow() - timedelta(days=1))  # not bookable stock

        response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer.id}")

        assert response.status_code == 200
        assert response.json == {
            "id": offer.id,
            "bookableStocks": [
                {
                    "id": bookableStock.id,
                    "price": 12.34,
                    "beginningDatetime": bookableStock.beginningDatetime.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                }
            ],
            "category": {"label": "Cinéma", "value": str(offer_type)},
            "description": offer.description,
            "imageUrl": None,
            "isDuo": True,
            "isDigital": offer.isDigital,
            "name": offer.name,
            "venue": {
                "id": offer.venue.id,
                "address": offer.venue.address,
                "city": offer.venue.city,
                "name": offer.venue.name,
                "offerer": {"name": offer.venue.managingOfferer.name},
                "postalCode": offer.venue.postalCode,
                "publicName": offer.venue.publicName,
            },
            "withdrawalDetails": offer.withdrawalDetails,
        }

    def test_get_offer_not_found(self, app):
        response = TestClient(app.test_client()).get("/native/v1/offer/1")

        assert response.status_code == 404
