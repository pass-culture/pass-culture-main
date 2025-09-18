import datetime
import decimal

import pytest
import time_machine

from pcapi.core import testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.utils import human_ids

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class GetProductTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/products/{offer_id}"
    endpoint_method = "get"
    default_path_params = {"offer_id": 1}

    num_queries_404 = 1  # select api_key, offerer and provider
    num_queries_404 += 1  # select offers
    num_queries_404 += 1  # rollback atomic

    num_queries = 1  # select price categories
    num_queries += 1  # select api_key, offerer and provider
    num_queries += 1  # select price categories
    num_queries += 1  # select mediations
    num_queries += 1  # select stocks

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        offer_id = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            idAtProvider="provider_id_at_provider",
        ).id

        with testing.assert_num_queries(self.num_queries_404):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        offer_id = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            idAtProvider="provider_id_at_provider",
        ).id

        with testing.assert_num_queries(self.num_queries_404):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 404

    @time_machine.travel(datetime.datetime(2025, 6, 25, 12, 30, tzinfo=datetime.timezone.utc), tick=False)
    def test_product_without_stock(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            idAtProvider="provider_id_at_provider",
        )
        offer_id = offer.id

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 200

        assert response.json == {
            "bookingAllowedDatetime": None,
            "publicationDatetime": "2025-06-25T12:25:00Z",
            "bookingContact": None,
            "bookingEmail": None,
            "categoryRelatedFields": {"category": "CARTE_CINE_ILLIMITE"},
            "description": "Un livre de contrepèterie",
            "accessibility": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": False,
                "visualDisabilityCompliant": False,
            },
            "enableDoubleBookings": False,
            "externalTicketOfficeUrl": None,
            "id": offer.id,
            "image": None,
            "itemCollectionDetails": None,
            "location": {"type": "physical", "venueId": offer.venueId},
            "name": "Vieux motard que jamais",
            "status": "SOLD_OUT",
            "stock": None,
            "idAtProvider": "provider_id_at_provider",
        }

    def test_books_can_be_retrieved(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        offer = offers_factories.ThingOfferFactory(
            venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id, extraData=None
        )
        offer_id = offer.id
        # This overpriced stock can be removed once all stocks have a price under 300 €
        offers_factories.StockFactory(offer=offer, price=decimal.Decimal("400.12"))

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 200

        assert response.json["categoryRelatedFields"] == {
            "author": None,
            "category": "LIVRE_PAPIER",
            "ean": None,
        }
        assert response.json["stock"]["price"] == 40012

    def test_product_with_not_selectable_category_can_be_retrieved(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        offer_id = offers_factories.ThingOfferFactory(venue=venue, subcategoryId=subcategories.ABO_LUDOTHEQUE.id).id

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 200

        assert response.json["categoryRelatedFields"] == {"category": "ABO_LUDOTHEQUE"}

    def test_product_with_stock_and_image(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        offer = offers_factories.ThingOfferFactory(venue=venue)
        offers_factories.StockFactory(offer=offer, isSoftDeleted=True)
        bookable_stock = offers_factories.StockFactory(
            offer=offer, price=12.34, quantity=10, bookingLimitDatetime=datetime.datetime(2022, 1, 15, 13, 0, 0)
        )
        bookings_factories.BookingFactory(stock=bookable_stock)
        mediation = offers_factories.MediationFactory(offer=offer, credit="Ph. Oto")
        offer_id = offer.id

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})

        assert response.status_code == 200
        assert response.json["stock"] == {
            "price": 1234,
            "quantity": 10,
            "bookedQuantity": 1,
            "bookingLimitDatetime": "2022-01-15T13:00:00Z",
        }
        assert response.json["image"] == {
            "credit": "Ph. Oto",
            "url": f"http://localhost/storage/thumbs/mediations/{human_ids.humanize(mediation.id)}",
        }
        assert response.json["status"] == "EXPIRED"

    def test_404_when_requesting_an_event(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        event_offer_id = offers_factories.EventOfferFactory(venue=venue).id

        with testing.assert_num_queries(self.num_queries_404):
            response = self.make_request(plain_api_key, path_params={"offer_id": event_offer_id})
            assert response.status_code == 404
        assert response.json == {"product_id": ["The product offer could not be found"]}
