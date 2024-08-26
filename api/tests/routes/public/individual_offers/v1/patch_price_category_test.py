import contextlib
import datetime
import decimal

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import db

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


pytestmark = pytest.mark.usefixtures("db_session")


@contextlib.contextmanager
def assert_event_and_price_category_did_not_change(event, price_category):
    old_price = price_category.price
    old_label = price_category.priceCategoryLabel
    old_event_prices = {stock.id: (stock.price, stock.priceCategoryId) for stock in event.stocks}

    yield

    db.session.refresh(price_category)
    db.session.refresh(event)

    new_price = price_category.price
    new_label = price_category.priceCategoryLabel
    new_event_prices = {stock.id: (stock.price, stock.priceCategoryId) for stock in event.stocks}

    assert new_price == old_price
    assert new_label == old_label
    assert new_event_prices == old_event_prices


@pytest.fixture(name="event_with_stock")
def event_with_stock_fixture(stock):
    return stock.offer


class PatchPriceCategoryTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{event_id}/price_categories/{price_category_id}"
    endpoint_method = "patch"
    default_path_params = {"event_id": 1, "price_category_id": 2}

    @staticmethod
    def _get_base_payload() -> dict:
        return {"price": 303}

    def _get_base_resource_url(self, event_id: int, price_category_id: int) -> str:
        return self.endpoint_url.format(event_id=event_id, price_category_id=price_category_id)

    def setup_base_resource(self, venue=None, provider=None) -> tuple[offers_models.Offer, offers_models.PriceCategory]:
        event = offers_factories.EventOfferFactory(venue=venue or self.setup_venue(), lastProvider=provider)
        price_category = offers_factories.PriceCategoryFactory(offer=event)
        return event, price_category

    def test_should_raise_401_because_not_authenticated(self, client: TestClient):
        event, price_category = self.setup_base_resource()
        response = client.patch(self._get_base_resource_url(event.id, price_category.id), json={})
        assert response.status_code == 401

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        event, price_category = self.setup_base_resource()
        response = client.with_explicit_token(plain_api_key).patch(
            self._get_base_resource_url(event.id, price_category.id), json=self._get_base_payload()
        )
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        event, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        response = client.with_explicit_token(plain_api_key).patch(
            self._get_base_resource_url(event.id, price_category.id), json=self._get_base_payload()
        )
        assert response.status_code == 404

    def test_should_raise_404_because_of_not_existing_resources(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        # unknown event
        with assert_event_and_price_category_did_not_change(event, price_category):
            response = client.with_explicit_token(plain_api_key).patch(
                self._get_base_resource_url(123455, price_category.id), json=self._get_base_payload()
            )
            assert response.status_code == 404

        # unknown price category
        with assert_event_and_price_category_did_not_change(event, price_category):
            response = client.with_explicit_token(plain_api_key).patch(
                self._get_base_resource_url(event.id, 12344556), json=self._get_base_payload()
            )
            assert response.status_code == 404

        # unknown price category & event
        with assert_event_and_price_category_did_not_change(event, price_category):
            response = client.with_explicit_token(plain_api_key).patch(
                self._get_base_resource_url(12345, 12344556), json=self._get_base_payload()
            )
            assert response.status_code == 404

    def test_should_raise_400_because_of_negative_price(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        with assert_event_and_price_category_did_not_change(event, price_category):
            response = client.with_explicit_token(plain_api_key).patch(
                self._get_base_resource_url(event.id, price_category.id), json={"price": -1}
            )
            assert response == 400

    def test_should_raise_400_because_of_price_too_high(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        with assert_event_and_price_category_did_not_change(event, price_category):
            response = client.with_explicit_token(plain_api_key).patch(
                self._get_base_resource_url(event.id, price_category.id), json={"price": 300000}
            )
            assert response == 400

    def test_should_raise_400_because_does_not_accept_extra_fields(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = client.with_explicit_token(plain_api_key).patch(
            self._get_base_resource_url(event.id, price_category.id),
            json={"price": 2500, "label": "carre or", "unrecognized_key": True},
        )

        assert response.status_code == 400
        assert response.json == {"unrecognized_key": ["extra fields not permitted"]}

    def test_update_price_category(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = client.with_explicit_token(plain_api_key).patch(
            self._get_base_resource_url(event.id, price_category.id),
            json={"price": 2500, "label": "carre or"},
        )
        assert response.status_code == 200

        assert price_category.price == decimal.Decimal("25")
        assert price_category.label == "carre or"

    def test_update_only_one_field(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = client.with_explicit_token(plain_api_key).patch(
            self._get_base_resource_url(event.id, price_category.id),
            json={"price": 2500},
        )

        assert response.status_code == 200
        assert price_category.price == decimal.Decimal("25")

    def test_stock_price_update(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, price_category = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        offers_factories.EventStockFactory(offer=event, priceCategory=price_category)
        offers_factories.EventStockFactory(offer=event, priceCategory=price_category)
        expired_stock = offers_factories.EventStockFactory(
            offer=event,
            priceCategory=price_category,
            beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=-2),
        )

        response = client.with_explicit_token(plain_api_key).patch(
            self._get_base_resource_url(event.id, price_category.id),
            json={"price": 25},
        )

        assert response.status_code == 200
        assert all((stock.price == decimal.Decimal("0.25") for stock in event.stocks if not stock.isEventExpired))
        assert expired_stock.price != decimal.Decimal("0.25")
