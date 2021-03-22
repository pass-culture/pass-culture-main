from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import MediationFactory
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import ProductFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.testing import assert_num_queries
from pcapi.models.offer_type import EventType
from pcapi.models.offer_type import ThingType

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


class OffersTest:
    @freeze_time("2020-01-01")
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
            description="desk cryption",
            name="l'offre du siècle",
            withdrawalDetails="modalité de retrait",
            extraData=extra_data,
            durationMinutes=33,
            visualDisabilityCompliant=True,
            externalTicketOfficeUrl="https://url.com",
            venue__name="il est venu le temps des names",
        )
        MediationFactory(id=111, offer=offer, thumbCount=1, credit="street credit")

        bookableStock = EventStockFactory(offer=offer, price=12.34, quantity=2)
        expiredStock = EventStockFactory(
            offer=offer, price=45.68, beginningDatetime=datetime.utcnow() - timedelta(days=1)
        )
        exhaustedStock = EventStockFactory(offer=offer, price=12.34, quantity=1)

        BookingFactory(stock=bookableStock)
        BookingFactory(stock=exhaustedStock)

        offer_id = offer.id
        with assert_num_queries(1):
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        assert response.json == {
            "id": offer.id,
            "accessibility": {
                "audioDisability": False,
                "mentalDisability": False,
                "motorDisability": False,
                "visualDisability": True,
            },
            "stocks": [
                {
                    "id": bookableStock.id,
                    "price": 1234,
                    "beginningDatetime": "2020-01-06T00:00:00Z",
                    "bookingLimitDatetime": "2020-01-05T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-03T00:00:00Z",
                    "isBookable": True,
                    "isSoldOut": False,
                    "isExpired": False,
                },
                {
                    "id": expiredStock.id,
                    "price": 4568,
                    "beginningDatetime": "2019-12-31T00:00:00Z",
                    "bookingLimitDatetime": "2019-12-30T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-01T00:00:00Z",
                    "isBookable": False,
                    "isSoldOut": False,
                    "isExpired": True,
                },
                {
                    "id": exhaustedStock.id,
                    "price": 1234,
                    "beginningDatetime": "2020-01-06T00:00:00Z",
                    "bookingLimitDatetime": "2020-01-05T23:00:00Z",
                    "cancellationLimitDatetime": "2020-01-03T00:00:00Z",
                    "isBookable": False,
                    "isSoldOut": True,
                    "isExpired": False,
                },
            ],
            "category": {"categoryType": "Event", "label": "Cinéma", "name": "CINEMA"},
            "description": "desk cryption",
            "externalTicketOfficeUrl": "https://url.com",
            "expenseDomains": ["all"],
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
            "image": {"url": "http://localhost/storage/thumbs/mediations/N4", "credit": "street credit"},
            "isActive": True,
            "isSoldOut": False,
            "isDuo": True,
            "isDigital": False,
            "isReleased": True,
            "name": "l'offre du siècle",
            "venue": {
                "id": offer.venue.id,
                "address": "1 boulevard Poissonnière",
                "city": "Paris",
                "coordinates": {
                    "latitude": 48.87004,
                    "longitude": 2.3785,
                },
                "name": "il est venu le temps des names",
                "offerer": {"name": offer.venue.managingOfferer.name},
                "postalCode": "75000",
                "publicName": "il est venu le temps des names",
            },
            "withdrawalDetails": "modalité de retrait",
        }

    def test_get_thing_offer(self, app):
        product = ProductFactory(thumbCount=1)
        offer_type = ThingType.MUSEES_PATRIMOINE_ABO
        offer = OfferFactory(type=str(offer_type), product=product)
        ThingStockFactory(offer=offer, price=12.34)

        offer_id = offer.id
        with assert_num_queries(1):
            response = TestClient(app.test_client()).get(f"/native/v1/offer/{offer_id}")

        assert response.status_code == 200
        assert not response.json["stocks"][0]["beginningDatetime"]
        assert response.json["stocks"][0]["price"] == 1234
        assert response.json["category"] == {
            "categoryType": "Thing",
            "label": "Musée, arts visuels et patrimoine",
            "name": "VISITE",
        }

    def test_get_offer_not_found(self, app):
        response = TestClient(app.test_client()).get("/native/v1/offer/1")

        assert response.status_code == 404
