import decimal

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class PostPriceCategoriesTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{event_id}/price_categories"
    endpoint_method = "post"
    default_path_params = {"event_id": 1}

    def setup_base_resource(self, venue=None, provider=None) -> offers_models.Offer:
        return offers_factories.EventOfferFactory(
            venue=venue or self.setup_venue(),
            lastProvider=provider,
        )

    @staticmethod
    def _get_base_payload() -> dict:
        return {
            "priceCategories": [
                {"price": 2500, "label": "carre or"},
                {"price": 1500, "label": "triangle argent"},
            ],
        }

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        event = self.setup_base_resource()
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id), json=self._get_base_payload()
        )
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id), json=self._get_base_payload()
        )
        assert response.status_code == 404

    def test_should_raise_404_because_event_does_not_exist(self, client: TestClient):
        plain_api_key, _ = self.setup_active_venue_provider()
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id="inexistent_event_id"),
            json=self._get_base_payload(),
        )
        assert response.status_code == 404

    def test_should_raise_404_for_product_offer(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        product_offer = offers_factories.ThingOfferFactory(
            venue=venue_provider.venue, lastProvider=venue_provider.provider
        )

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=product_offer.id),
            json=self._get_base_payload(),
        )
        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}

    def test_create_price_categories(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id),
            json=self._get_base_payload(),
        )
        assert response.status_code == 200

        [triangle_argent_category, carre_or_category] = offers_models.PriceCategory.query.order_by(
            offers_models.PriceCategory.price
        ).all()
        assert carre_or_category.label == "carre or"
        assert carre_or_category.price == decimal.Decimal("25")

        assert triangle_argent_category.label == "triangle argent"
        assert triangle_argent_category.price == decimal.Decimal("15")

        assert response.json == {
            "priceCategories": [
                {"id": carre_or_category.id, "price": 2500, "label": "carre or"},
                {"id": triangle_argent_category.id, "price": 1500, "label": "triangle argent"},
            ],
        }

    def test_create_duplicate_price_categories(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        payload = self._get_base_payload()
        # duplicate price category
        payload["priceCategories"].append(payload["priceCategories"][0])
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id), json=payload
        )

        assert response.status_code == 400
        assert response.json == {
            "priceCategories": ["Price categories must be unique"],
        }

    def test_create_existing_price_categories(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        payload = self._get_base_payload()

        offers_factories.PriceCategoryFactory(
            offer=event,
            price=decimal.Decimal("25"),
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(label="carre or"),
        )

        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id),
            json=payload,
        )

        assert response.status_code == 400
        assert response.json == {
            "priceCategories": ["The price category carre or already exists"],
        }
