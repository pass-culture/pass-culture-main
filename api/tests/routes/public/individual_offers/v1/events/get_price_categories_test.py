import decimal

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class PostPriceCategoriesTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{event_id}/price_categories"
    endpoint_method = "get"
    default_path_params = {"event_id": 1}

    def setup_base_resource(self, venue=None, provider=None) -> offers_models.Offer:
        return offers_factories.EventOfferFactory(
            venue=venue or self.setup_venue(),
            lastProvider=provider,
        )

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        event = self.setup_base_resource()
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event.id))
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event.id))
        assert response.status_code == 404

    def test_should_return_price_categories(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        price_category_1 = offers_factories.PriceCategoryFactory(
            offer=event,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(
                label="Carré d'or", venue=venue_provider.venue
            ),
            price=decimal.Decimal("30"),
        )
        price_category_2 = offers_factories.PriceCategoryFactory(
            offer=event,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(
                label="Triangle d'argent", venue=venue_provider.venue
            ),
            price=decimal.Decimal("15"),
            idAtProvider="silver_triangle",
        )
        offers_factories.PriceCategoryFactory()  # should not appear in result
        response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event.id))
        assert response.status_code == 200
        assert response.json == {
            "priceCategories": [
                {"id": price_category_1.id, "idAtProvider": None, "label": "Carré d'or", "price": 3000},
                {
                    "id": price_category_2.id,
                    "idAtProvider": "silver_triangle",
                    "label": "Triangle d'argent",
                    "price": 1500,
                },
            ]
        }

    def test_should_filter_price_categories_by_id_at_provider(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        # should not appear in result
        offers_factories.PriceCategoryFactory(
            offer=event,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(
                label="Carré d'or", venue=venue_provider.venue
            ),
            price=decimal.Decimal("30"),
        )
        offers_factories.PriceCategoryFactory(
            offer=event,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(
                label="Triangle d'argent", venue=venue_provider.venue
            ),
            price=decimal.Decimal("15"),
            idAtProvider="silver_triangle",
        )
        offers_factories.PriceCategoryFactory()
        # expected in result
        price_category_3 = offers_factories.PriceCategoryFactory(
            offer=event,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(
                label="Cercle de bronze", venue=venue_provider.venue
            ),
            price=decimal.Decimal("10"),
            idAtProvider="bronze_circle",
        )
        price_category_4 = offers_factories.PriceCategoryFactory(
            offer=event,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(
                label="Hexagone en chocolat", venue=venue_provider.venue
            ),
            price=decimal.Decimal("5"),
            idAtProvider="chocolate_hexagon",
        )
        response = client.with_explicit_token(plain_api_key).get(
            self.endpoint_url.format(event_id=event.id), params={"ids_at_provider": "bronze_circle,chocolate_hexagon"}
        )
        assert response.status_code == 200
        assert response.json == {
            "priceCategories": [
                {
                    "id": price_category_3.id,
                    "idAtProvider": "bronze_circle",
                    "label": "Cercle de bronze",
                    "price": 1000,
                },
                {
                    "id": price_category_4.id,
                    "idAtProvider": "chocolate_hexagon",
                    "label": "Hexagone en chocolat",
                    "price": 500,
                },
            ]
        }
