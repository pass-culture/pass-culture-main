import collections
import contextlib
import datetime
import decimal

from flask import url_for
import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.models import db
from pcapi.routes.shared.price import convert_to_cent

from . import utils


pytestmark = pytest.mark.usefixtures("db_session")


EmptyGenerator = collections.abc.Generator[None, None, None]


@contextlib.contextmanager
def assert_event_and_price_category_did_not_change(event, price_category) -> EmptyGenerator:
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


class PatchPriceCategoryErrorsTest:
    endpoint = "public_api.v1_public_api.individual_offers.v1_blueprint.patch_event_price_categories"

    def test_cannot_access_resource_from_other_api_key(self, other_auth_client, event_with_stock, price_category):
        kwargs = {"event_id": event_with_stock.id, "price_category_id": price_category.id}
        json_data = {"price": convert_to_cent(price_category.price * 3)}

        with assert_event_and_price_category_did_not_change(event_with_stock, price_category):
            assert other_auth_client.patch(url_for(self.endpoint, **kwargs), json=json_data).status_code == 404

    def test_unauthenticated(self, client, event_with_stock, price_category):
        kwargs = {"event_id": event_with_stock.id, "price_category_id": price_category.id}
        json_data = {"price": convert_to_cent(price_category.price * 3)}

        with assert_event_and_price_category_did_not_change(event_with_stock, price_category):
            assert client.patch(url_for(self.endpoint, **kwargs), json=json_data).status_code == 401

    def test_unknown_event(self, auth_client, event_with_stock, price_category):
        kwargs = {"event_id": event_with_stock.id * 16, "price_category_id": price_category.id}
        json_data = {"price": convert_to_cent(price_category.price * 3)}

        with assert_event_and_price_category_did_not_change(event_with_stock, price_category):
            assert auth_client.patch(url_for(self.endpoint, **kwargs), json=json_data).status_code == 404

    def test_unknown_price_category(self, auth_client, event_with_stock, price_category):
        kwargs = {"event_id": event_with_stock.id, "price_category_id": price_category.id * 16}
        json_data = {"price": convert_to_cent(price_category.price * 3)}

        with assert_event_and_price_category_did_not_change(event_with_stock, price_category):
            assert auth_client.patch(url_for(self.endpoint, **kwargs), json=json_data).status_code == 404

    def test_both_event_and_price_category_unknown(self, auth_client, event_with_stock, price_category):
        kwargs = {"event_id": event_with_stock.id * 16, "price_category_id": price_category.id * 16}
        json_data = {"price": convert_to_cent(price_category.price * 3)}

        with assert_event_and_price_category_did_not_change(event_with_stock, price_category):
            assert auth_client.patch(url_for(self.endpoint, **kwargs), json=json_data).status_code == 404

    def test_negative_price(self, auth_client, event_with_stock, price_category):
        kwargs = {"event_id": event_with_stock.id, "price_category_id": price_category.id}
        json_data = {"price": -1}

        with assert_event_and_price_category_did_not_change(event_with_stock, price_category):
            assert auth_client.patch(url_for(self.endpoint, **kwargs), json=json_data).status_code == 400

    def test_price_too_high(self, auth_client, event_with_stock, price_category):
        kwargs = {"event_id": event_with_stock.id, "price_category_id": price_category.id}
        json_data = {"price": convert_to_cent(301)}

        with assert_event_and_price_category_did_not_change(event_with_stock, price_category):
            assert auth_client.patch(url_for(self.endpoint, **kwargs), json=json_data).status_code == 400


class PatchPriceCategoryTest:
    def test_update_price_category(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}/price_categories/{price_category.id}",
            json={"price": 2500, "label": "carre or"},
        )
        assert response.status_code == 200

        assert price_category.price == decimal.Decimal("25")
        assert price_category.label == "carre or"

    def test_update_only_one_field(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)

        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}/price_categories/{price_category.id}",
            json={"price": 2500},
        )
        assert response.status_code == 200

        assert price_category.price == decimal.Decimal("25")

    def test_update_with_error(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}/price_categories/{price_category.id}",
            json={"price": -1},
        )
        assert response.status_code == 400

    def test_does_not_accept_extra_fields(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}/price_categories/{price_category.id}",
            json={"price": 2500, "label": "carre or", "unrecognized_key": True},
        )
        assert response.status_code == 400
        assert response.json == {"unrecognized_key": ["extra fields not permitted"]}

    def test_stock_price_update(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        offer = offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)
        price_category = offers_factories.PriceCategoryFactory(
            offer=offer,
            priceCategoryLabel=offers_factories.PriceCategoryLabelFactory(label="Already exists", venue=offer.venue),
        )
        offers_factories.EventStockFactory(offer=offer, priceCategory=price_category)
        offers_factories.EventStockFactory(offer=offer, priceCategory=price_category)
        expired_stock = offers_factories.EventStockFactory(
            offer=offer,
            priceCategory=price_category,
            beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=-2),
        )

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{offer.id}/price_categories/{price_category.id}",
            json={"price": 25},
        )

        assert response.status_code == 200
        assert all((stock.price == decimal.Decimal("0.25") for stock in offer.stocks if not stock.isEventExpired))
        assert expired_stock.price != decimal.Decimal("0.25")

    def test_find_no_offer_returns_404(self, client):
        utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/events/inexistent_event_id/price_categories/inexistent_price_category_id",
            json={"price": 2500, "label": "carre or"},
        )
        assert response.status_code == 404

    def test_inactive_provider_returns_404(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        event_offer = offers_factories.EventOfferFactory(venue=venue, lastProvider=api_key.provider)
        price_category = offers_factories.PriceCategoryFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            f"/public/offers/v1/events/{event_offer.id}/price_categories/{price_category.id}",
            json={"price": 2500, "label": "carre or"},
        )
        assert response.status_code == 404
