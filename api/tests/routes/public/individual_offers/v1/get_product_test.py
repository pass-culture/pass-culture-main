import datetime
import decimal

import pytest

from pcapi.core import testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.utils import human_ids

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class GetProductTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/products/{product_id}"

    def test_should_raise_401_because_not_authenticated(self, client):
        response = client.get(self.endpoint_url.format(product_id=1))

        assert response.status_code == 401

    def test_should_raise_404_because_has_no_access_to_venue(self, client):
        plain_api_key, _ = self.setup_provider()
        venue = self.setup_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            idAtProvider="provider_id_at_provider",
        )

        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(product_id=product_offer.id))

        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            idAtProvider="provider_id_at_provider",
        )

        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(product_id=product_offer.id))

        assert response.status_code == 404

    def test_product_without_stock(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            idAtProvider="provider_id_at_provider",
        )

        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(product_id=product_offer.id))

        assert response.status_code == 200
        assert response.json == {
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
            "id": product_offer.id,
            "image": None,
            "itemCollectionDetails": None,
            "location": {"type": "physical", "venueId": product_offer.venueId},
            "name": "Vieux motard que jamais",
            "status": "SOLD_OUT",
            "stock": None,
            "idAtProvider": "provider_id_at_provider",
        }

    def test_books_can_be_retrieved(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id, extraData=None
        )
        # This overpriced stock can be removed once all stocks have a price under 300 €
        offers_factories.StockFactory(offer=product_offer, price=decimal.Decimal("400.12"))

        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(product_id=product_offer.id))

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {
            "author": None,
            "category": "LIVRE_PAPIER",
            "ean": None,
        }
        assert response.json["stock"]["price"] == 40012

    def test_product_with_not_selectable_category_can_be_retrieved(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.ABO_LUDOTHEQUE.id,
        )

        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(product_id=product_offer.id))

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {"category": "ABO_LUDOTHEQUE"}

    def test_product_with_stock_and_image(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        product_offer = offers_factories.ThingOfferFactory(venue=venue)
        offers_factories.StockFactory(offer=product_offer, isSoftDeleted=True)
        bookable_stock = offers_factories.StockFactory(
            offer=product_offer, price=12.34, quantity=10, bookingLimitDatetime=datetime.datetime(2022, 1, 15, 13, 0, 0)
        )
        bookings_factories.BookingFactory(stock=bookable_stock)
        mediation = offers_factories.MediationFactory(offer=product_offer, credit="Ph. Oto")
        product_offer_id = product_offer.id

        num_query = 1  # retrieve API key
        num_query += 1  # retrieve offer
        num_query += 1  # retrieve feature_flags for api key validation

        with testing.assert_num_queries(num_query):
            response = client.with_explicit_token(plain_api_key).get(f"/public/offers/v1/products/{product_offer_id}")

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

    def test_404_when_requesting_an_event(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        venue = venue_provider.venue
        event_offer = offers_factories.EventOfferFactory(venue=venue)

        response = client.with_explicit_token(plain_api_key).get(f"/public/offers/v1/products/{event_offer.id}")

        assert response.status_code == 404
        assert response.json == {"product_id": ["The product offer could not be found"]}
