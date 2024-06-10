import datetime
import decimal

import pytest

from pcapi.core import testing
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.utils import human_ids

from . import utils


@pytest.mark.usefixtures("db_session")
class GetProductTest:
    def test_product_without_stock(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            idAtProvider="provider_id_at_provider",
        )
        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.get(f"/public/offers/v1/products/{product_offer.id}")

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
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id, extraData=None
        )
        # This overpriced stock can be removed once all stocks have a price under 300 €
        offers_factories.StockFactory(offer=product_offer, price=decimal.Decimal("400.12"))

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.get(f"/public/offers/v1/products/{product_offer.id}")

            assert response.status_code == 200
            assert response.json["categoryRelatedFields"] == {
                "author": None,
                "category": "LIVRE_PAPIER",
                "ean": None,
            }
            assert response.json["stock"]["price"] == 40012

    def test_product_with_not_selectable_category_can_be_retrieved(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
            subcategoryId=subcategories.ABO_LUDOTHEQUE.id,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.get(f"/public/offers/v1/products/{product_offer.id}")

            assert response.status_code == 200
            assert response.json["categoryRelatedFields"] == {"category": "ABO_LUDOTHEQUE"}

    def test_product_with_stock_and_image(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
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

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(num_query):
            response = client.get(f"/public/offers/v1/products/{product_offer_id}")

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
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.get(f"/public/offers/v1/products/{event_offer.id}")

            assert response.status_code == 404
            assert response.json == {"product_id": ["The product offer could not be found"]}

    def test_404_when_inactive_venue_provider(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.get(f"/public/offers/v1/products/{product_offer.id}")
            assert response.status_code == 404
