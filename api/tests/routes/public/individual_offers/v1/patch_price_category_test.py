import datetime
import decimal

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models

from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


pytestmark = pytest.mark.usefixtures("db_session")


class PatchPriceCategoryTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{offer_id}/price_categories/{price_category_id}"
    endpoint_method = "patch"
    default_path_params = {"offer_id": 1, "price_category_id": 2}

    @staticmethod
    def _get_base_payload() -> dict:
        return {"price": 303}

    def setup_base_resource(self, venue=None, provider=None) -> tuple[offers_models.Offer, offers_models.PriceCategory]:
        offer = offers_factories.EventOfferFactory(venue=venue or self.setup_venue(), lastProvider=provider)
        price_category = offers_factories.PriceCategoryFactory(offer=offer)
        return offer, price_category

    def test_should_raise_404_because_has_no_access_to_venue(self):
        plain_api_key, _ = self.setup_provider()
        offer, price_category = self.setup_base_resource()
        response = self.make_request(
            plain_api_key,
            {"offer_id": offer.id, "price_category_id": price_category.id},
            json_body=self._get_base_payload(),
        )

        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        offer, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        response = self.make_request(
            plain_api_key,
            {"offer_id": offer.id, "price_category_id": price_category.id},
            json_body=self._get_base_payload(),
        )
        assert response.status_code == 404

    @pytest.mark.parametrize("offer_id,price_category_id", [(12, None), (None, 12), (12, 12)])
    def test_should_raise_404_because_of_not_existing_resources(self, offer_id, price_category_id):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"offer_id": offer_id or offer.id, "price_category_id": price_category_id or price_category.id},
            json_body=self._get_base_payload(),
        )
        assert response.status_code == 404

    @pytest.mark.parametrize(
        "payload,expected_json",
        [
            ({"price": -1}, {"price": ["ensure this value is greater than or equal to 0"]}),
            ({"price": 300000}, {"price": ["ensure this value is less than or equal to 30000"]}),
            (
                {"oublie_que_tu_as_aucune_chance": True},
                {"oublie_que_tu_as_aucune_chance": ["extra fields not permitted"]},
            ),
            (
                {"idAtProvider": "sur_un_malentendu_ça_peut_passer"},
                {
                    "idAtProvider": [
                        "`sur_un_malentendu_ça_peut_passer` is already taken by another offer price category"
                    ]
                },
            ),
        ],
    )
    def test_should_raise_400(self, payload, expected_json):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offers_factories.PriceCategoryFactory(offer=offer, idAtProvider="sur_un_malentendu_ça_peut_passer")

        response = self.make_request(
            plain_api_key, {"offer_id": offer.id, "price_category_id": price_category.id}, json_body=payload
        )
        assert response.status_code == 400
        assert response.json == expected_json

    def test_update_price_category(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key,
            {"offer_id": offer.id, "price_category_id": price_category.id},
            json_body={"price": 2500, "label": "carre or", "idAtProvider": "updated_id_at_provider"},
        )
        assert response.status_code == 200

        assert price_category.price == decimal.Decimal("25")
        assert price_category.label == "carre or"
        assert price_category.idAtProvider == "updated_id_at_provider"

    def test_update_only_one_field(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = self.make_request(
            plain_api_key, {"offer_id": offer.id, "price_category_id": price_category.id}, json_body={"price": 2500}
        )

        assert response.status_code == 200
        assert price_category.price == decimal.Decimal("25")

    def test_stock_price_update(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offers_factories.EventStockFactory(offer=offer, priceCategory=price_category)
        offers_factories.EventStockFactory(offer=offer, priceCategory=price_category)
        expired_stock = offers_factories.EventStockFactory(
            offer=offer,
            priceCategory=price_category,
            beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=-2),
        )

        response = self.make_request(
            plain_api_key, {"offer_id": offer.id, "price_category_id": price_category.id}, json_body={"price": 25}
        )

        assert response.status_code == 200
        assert all((stock.price == decimal.Decimal("0.25") for stock in offer.stocks if not stock.isEventExpired))
        assert expired_stock.price != decimal.Decimal("0.25")
