import datetime
from unittest import mock

from flask import current_app as app
import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import api
from pcapi.core.offers import factories
from pcapi.models import api_errors
from pcapi.models.feature import override_features


@pytest.mark.usefixtures("db_session")
class CreateStockTest:
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_create_thing_offer(self, mocked_add_offer_id):
        offer = factories.ThingOfferFactory()

        stock = api.create_stock(offer=offer, price=10)

        assert stock.offer == offer
        assert stock.price == 10
        assert stock.quantity is None
        assert stock.beginningDatetime is None
        assert stock.bookingLimitDatetime is None
        mocked_add_offer_id.assert_called_once_with(client=app.redis_client, offer_id=offer.id)

    def test_create_event_offer(self):
        offer = factories.EventOfferFactory()
        beginning = datetime.datetime(2024, 1, 1, 12, 0, 0)
        booking_limit = datetime.datetime(2024, 1, 1, 9, 0, 0)

        stock = api.create_stock(
            offer=offer,
            price=10,
            quantity=7,
            beginning=beginning,
            booking_limit_datetime=booking_limit,
        )

        assert stock.offer == offer
        assert stock.price == 10
        assert stock.quantity == 7
        assert stock.beginningDatetime == beginning
        assert stock.bookingLimitDatetime == booking_limit

    @override_features(SYNCHRONIZE_ALGOLIA=False)
    @mock.patch("pcapi.connectors.redis.add_offer_id")
    def test_do_not_sync_algolia_if_feature_is_disabled(self, mocked_add_offer_id):
        offer = factories.ThingOfferFactory()

        api.create_stock(offer=offer, price=10, quantity=7)

        mocked_add_offer_id.assert_not_called()

    def test_fail_if_missing_dates(self):
        offer = factories.EventOfferFactory()

        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=10, beginning=None, booking_limit_datetime=None)

        assert "beginningDatetime" in error.value.errors

    def test_fail_if_offer_is_not_editable(self):
        offerer = offerers_factories.ProviderFactory()
        offer = factories.ThingOfferFactory(lastProvider=offerer, idAtProviders="1")

        with pytest.raises(api_errors.ApiErrors) as error:
            api.create_stock(offer=offer, price=10, beginning=None, booking_limit_datetime=None)

        assert error.value.errors == {"global": ["Les offres importées ne sont pas modifiables"]}
