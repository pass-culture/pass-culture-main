import datetime
import decimal

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories

from . import utils


@pytest.mark.usefixtures("db_session")
class PatchPriceCategoryTest:
    def test_find_no_offer_returns_404(self, client):
        offerers_factories.ApiKeyFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).patch(
            "/public/offers/v1/events/inexistent_event_id/price_categories/inexistent_price_category_id",
            json={"price": 2500, "label": "carre or"},
        )
        assert response.status_code == 404

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
        assert response.json == {"unrecognized_key": ["Vous ne pouvez pas changer cette information"]}

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
