from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.models.offer_type import EventType
from pcapi.models.offer_type import ThingType

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class OffersTest:
    def test_get_event_offer(self, app):
        offer_type = EventType.CINEMA
        extra_data = {
            "author": "mandibule",
            "isbn": "3838",
            "musicSubType": "502",
            "musicType": "501",
            "performer": "interprète",
            "showSubType": "101",
            "showType": "100",
            "stageDirector": "metteur en scène",
            "speaker": "intervenant",
            "visa": "vasi",
        }
        offer = OfferFactory(
            type=str(offer_type),
            isDuo=True,
            withdrawalDetails="modalité de retrait",
            extraData=extra_data,
            durationMinutes=33,
            visualDisabilityCompliant=True,
        )

        bookableStock = EventStockFactory(offer=offer, price=12.34)
        notBookableStock = EventStockFactory(
            offer=offer, price=45.68, beginningDatetime=datetime.utcnow() - timedelta(days=1)
        )

        response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer.id}")

        assert response.status_code == 200
        assert response.json == {
            "id": offer.id,
            "accessibility": {
                "audioDisability": None,
                "mentalDisability": None,
                "motorDisability": None,
                "visualDisability": True,
            },
            "stocks": [
                {
                    "id": bookableStock.id,
                    "price": 12.34,
                    "beginningDatetime": bookableStock.beginningDatetime.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    "isBookable": True,
                },
                {
                    "id": notBookableStock.id,
                    "price": 45.68,
                    "isBookable": False,
                    "beginningDatetime": notBookableStock.beginningDatetime.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                },
            ],
            "category": {"categoryType": "Event", "label": "Cinéma", "name": "CINEMA"},
            "description": offer.description,
            "extraData": {
                "author": "mandibule",
                "isbn": "3838",
                "durationMinutes": 33,
                "musicSubType": "Acid Jazz",
                "musicType": "Jazz",
                "performer": "interprète",
                "showSubType": "Carnaval",
                "showType": "Arts de la rue",
                "speaker": "intervenant",
                "stageDirector": "metteur en scène",
                "visa": "vasi",
            },
            "imageUrl": None,
            "isDuo": True,
            "isDigital": offer.isDigital,
            "name": offer.name,
            "venue": {
                "id": offer.venue.id,
                "address": offer.venue.address,
                "city": offer.venue.city,
                "coordinates": {
                    "latitude": float(offer.venue.latitude) if offer.venue.latitude else None,
                    "longitude": float(offer.venue.longitude) if offer.venue.longitude else None,
                },
                "name": offer.venue.name,
                "offerer": {"name": offer.venue.managingOfferer.name},
                "postalCode": offer.venue.postalCode,
                "publicName": offer.venue.publicName,
            },
            "withdrawalDetails": offer.withdrawalDetails,
        }

    def test_get_thing_offer(self, app):
        offer_type = ThingType.MUSEES_PATRIMOINE_ABO
        offer = OfferFactory(type=str(offer_type))
        ThingStockFactory(offer=offer, price=12.34)

        response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer.id}")

        assert response.status_code == 200
        assert not response.json["stocks"][0]["beginningDatetime"]
        assert response.json["stocks"][0]["price"] == 12.34
        assert response.json["category"] == {
            "categoryType": "Thing",
            "label": "Musée, arts visuels et patrimoine",
            "name": "VISITE",
        }

    def test_get_offer_not_found(self, app):
        response = TestClient(app.test_client()).get("/native/v1/offer/1")

        assert response.status_code == 404
