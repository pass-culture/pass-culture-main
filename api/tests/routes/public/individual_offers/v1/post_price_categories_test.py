import decimal

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models

from . import utils


@pytest.mark.usefixtures("db_session")
class PostPriceCategoriesTest:
    def test_create_price_categories(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{event_offer.id}/price_categories",
            json={
                "priceCategories": [
                    {"price": 2500, "label": "carre or"},
                    {"price": 1500, "label": "triangle argent"},
                ],
            },
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

    def test_invalid_offer_id(self, client):
        utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events/inexistent_event_id/price_categories",
            json={
                "priceCategories": [
                    {"price": 2500, "label": "carre or"},
                ],
            },
        )

        assert response.status_code == 404

    def test_404_for_other_offerer_offer(self, client):
        utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{event_offer.id}/price_categories",
            json={
                "priceCategories": [
                    {"price": 2500, "label": "carre or"},
                ],
            },
        )
        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}

    def test_404_for_product_offer(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product_offer = offers_factories.ThingOfferFactory(venue=venue)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{product_offer.id}/price_categories",
            json={
                "priceCategories": [
                    {"price": 2500, "label": "carre or"},
                ],
            },
        )
        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}

    def test_create_duplicate_price_categories(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{event_offer.id}/price_categories",
            json={
                "priceCategories": [
                    {"price": 2500, "label": "carre or"},
                    {"price": 1500, "label": "triangle argent"},
                    {"price": 2500, "label": "carre or"},
                ],
            },
        )
        assert response.status_code == 400

        assert response.json == {
            "priceCategories": ["Price categories must be unique"],
        }

    def test_create_existing_price_categories(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )

        offers_factories.PriceCategoryFactory(
            offer=event_offer,
            price=decimal.Decimal("25"),
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(label="carre or"),
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            f"/public/offers/v1/events/{event_offer.id}/price_categories",
            json={
                "priceCategories": [
                    {"price": 1500, "label": "triangle argent"},
                    {"price": 2500, "label": "carre or"},
                ],
            },
        )
        assert response.status_code == 400

        assert response.json == {
            "priceCategories": ["The price category carre or already exists"],
        }
