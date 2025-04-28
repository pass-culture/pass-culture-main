import decimal

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db

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
                {"price": 2500, "label": "carre or", "idAtProvider": "id_carre_or"},
                {"price": 1500, "label": "triangle argent", "idAtProvider": "id_triangle_argent"},
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

        [triangle_argent_category, carre_or_category] = (
            db.session.query(offers_models.PriceCategory).order_by(offers_models.PriceCategory.price).all()
        )
        assert carre_or_category.label == "carre or"
        assert carre_or_category.price == decimal.Decimal("25")
        assert carre_or_category.idAtProvider == "id_carre_or"

        assert triangle_argent_category.label == "triangle argent"
        assert triangle_argent_category.price == decimal.Decimal("15")
        assert triangle_argent_category.idAtProvider == "id_triangle_argent"

        assert response.json == {
            "priceCategories": [
                {"id": carre_or_category.id, "price": 2500, "label": "carre or", "idAtProvider": "id_carre_or"},
                {
                    "id": triangle_argent_category.id,
                    "price": 1500,
                    "label": "triangle argent",
                    "idAtProvider": "id_triangle_argent",
                },
            ],
        }

    def test_should_raise_400_because_of_duplicate_price_categories(self, client):
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

    def test_should_raise_400_because_of_duplicated_price_category_ids_at_provider(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        payload_with_duplicate_ids_at_provider = {
            "priceCategories": [
                {"price": 2500, "label": "carre or", "idAtProvider": "id_carre_or"},
                {
                    "price": 1500,
                    "label": "triangle argent",
                    "idAtProvider": "id_qui_apparait_dos_veces_dirait_les_espagnols",
                },
                {
                    "price": 1600,
                    "label": "triangle argent 2",
                    "idAtProvider": "id_qui_apparait_dos_veces_dirait_les_espagnols",
                },
            ],
        }
        # duplicate price category
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id), json=payload_with_duplicate_ids_at_provider
        )

        assert response.status_code == 400
        assert response.json == {
            "priceCategories": [
                "Price category `idAtProvider` must be unique. Duplicated value : id_qui_apparait_dos_veces_dirait_les_espagnols"
            ]
        }

    def test_should_raise_400_because_id_at_provider_is_already_taken(self, client):
        duplicated_id_at_provider = "mon_id_est_pas_is_ouf"
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offers_factories.PriceCategoryFactory(offer=event, idAtProvider=duplicated_id_at_provider)

        payload_with_duplicate_ids_at_provider = {
            "priceCategories": [{"price": 2500, "label": "carre or", "idAtProvider": duplicated_id_at_provider}],
        }
        # duplicate price category
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id), json=payload_with_duplicate_ids_at_provider
        )

        assert response.status_code == 400
        assert response.json == {
            "idAtProvider": ["`mon_id_est_pas_is_ouf` is already taken by another offer price category"]
        }

    def test_should_not_raise_if_price_category_id_at_provider_is_None(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        payload_with_duplicate_ids_at_provider = {
            "priceCategories": [
                {"price": 2500, "label": "carre or", "idAtProvider": None},
                {
                    "price": 1500,
                    "label": "triangle argent",
                    "idAtProvider": None,
                },
            ],
        }
        # duplicate price category
        response = client.with_explicit_token(plain_api_key).post(
            self.endpoint_url.format(event_id=event.id), json=payload_with_duplicate_ids_at_provider
        )

        assert response.status_code == 200

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
