import datetime
import decimal

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories
from pcapi.core.offers import models
from pcapi.core.offers import schemas
from pcapi.core.offers.tasks import _update_offer_and_related_stock
from pcapi.core.providers import factories as providers_factories
from pcapi.models import db
from pcapi.utils import date as utils_date


NOW = datetime.datetime.now(datetime.UTC)
ONE_DAY_AGO = NOW - datetime.timedelta(days=1)
ONE_DAY_FROM_NOW = NOW + datetime.timedelta(days=1)


@pytest.mark.usefixtures("db_session")
class UpdateOfferAndRelatedStockTest:
    def _get_serialized_stock_dict(
        self, stock: models.Stock, partial_dict: dict | None = None
    ) -> schemas.SerializedProductsStock:
        partial_dict = partial_dict or {}

        base_dict = {
            "quantity": stock.remainingQuantity,
            "price": int(stock.price * 100),
            "booking_limit_datetime": stock.bookingLimitDatetime,
            "publication_datetime": stock.offer.publicationDatetime,
            "booking_allowed_datetime": stock.offer.bookingAllowedDatetime,
        }
        base_dict.update(**partial_dict)

        return base_dict

    def test_should_update_offer_provider(self):
        provider_1 = providers_factories.PublicApiProviderFactory()
        provider_2 = providers_factories.PublicApiProviderFactory()
        stock = factories.ThingStockFactory(offer__lastProvider=provider_1)
        has_been_updated, updated_offer = _update_offer_and_related_stock(
            stock.offer,
            self._get_serialized_stock_dict(stock),
            provider=provider_2,
            offerer_address=stock.offer.offererAddress,
        )
        assert has_been_updated
        assert updated_offer.lastProvider == provider_2

    def test_should_update_offer_address(self):
        provider_1 = providers_factories.PublicApiProviderFactory()
        offerer_address = offerers_factories.OffererAddressFactory()

        stock = factories.ThingStockFactory(offer__lastProvider=provider_1)
        has_been_updated, updated_offer = _update_offer_and_related_stock(
            stock.offer,
            self._get_serialized_stock_dict(stock),
            provider=provider_1,
            offerer_address=offerer_address,
        )
        assert has_been_updated
        assert updated_offer.offererAddress == offerer_address

    @pytest.mark.parametrize(
        "initial_publication_datetime,input_publication_datetime,final_publication_datetime",
        [
            (None, NOW, NOW),
            (ONE_DAY_AGO, NOW, ONE_DAY_AGO),
            (ONE_DAY_AGO, None, None),
            (ONE_DAY_FROM_NOW, NOW, NOW),
            (NOW, ONE_DAY_FROM_NOW, ONE_DAY_FROM_NOW),
        ],
    )
    def test_should_update_offer_publication_datetime(
        self,
        initial_publication_datetime,
        input_publication_datetime,
        final_publication_datetime,
    ):
        provider_1 = providers_factories.PublicApiProviderFactory()
        stock = factories.ThingStockFactory(
            offer__lastProvider=provider_1,
            offer__publicationDatetime=initial_publication_datetime,
        )
        _, updated_offer = _update_offer_and_related_stock(
            stock.offer,
            self._get_serialized_stock_dict(stock, {"publication_datetime": input_publication_datetime}),
            provider=provider_1,
            offerer_address=stock.offer.offererAddress,
        )
        assert updated_offer.publicationDatetime == final_publication_datetime

    @pytest.mark.parametrize(
        "initial_booking_allowed_datetime,input_booking_allowed_datetime,final_booking_allowed_datetime",
        [
            (None, NOW, NOW),
            (ONE_DAY_AGO, NOW, NOW),
            (ONE_DAY_AGO, None, None),
            (ONE_DAY_FROM_NOW, NOW, NOW),
            (NOW, ONE_DAY_FROM_NOW, ONE_DAY_FROM_NOW),
        ],
    )
    def test_should_update_offer_booking_allowed_datetime(
        self,
        initial_booking_allowed_datetime,
        input_booking_allowed_datetime,
        final_booking_allowed_datetime,
    ):
        provider_1 = providers_factories.PublicApiProviderFactory()
        stock = factories.ThingStockFactory(
            offer__lastProvider=provider_1,
            offer__bookingAllowedDatetime=initial_booking_allowed_datetime,
        )
        _, updated_offer = _update_offer_and_related_stock(
            stock.offer,
            self._get_serialized_stock_dict(stock, {"booking_allowed_datetime": input_booking_allowed_datetime}),
            provider=provider_1,
            offerer_address=stock.offer.offererAddress,
        )
        assert updated_offer.bookingAllowedDatetime == final_booking_allowed_datetime

    def test_should_create_stock(self):
        provider_1 = providers_factories.PublicApiProviderFactory()
        offer = factories.OfferFactory(lastProvider=provider_1)
        has_been_updated, update_offer = _update_offer_and_related_stock(
            offer,
            {
                "quantity": 10,
                "price": 550,
                "booking_limit_datetime": None,
                "publication_datetime": offer.publicationDatetime,
                "booking_allowed_datetime": offer.bookingAllowedDatetime,
            },
            provider=provider_1,
            offerer_address=offer.offererAddress,
        )
        assert has_been_updated
        stock = db.session.query(models.Stock).first()
        assert stock.offer == update_offer
        assert stock.price == decimal.Decimal("5.50")
        assert stock.bookingLimitDatetime == None
        assert stock.quantity == 10

    def test_should_update_stock_price(self):
        provider_1 = providers_factories.PublicApiProviderFactory()
        stock = factories.ThingStockFactory(offer__lastProvider=provider_1)
        has_been_updated, _ = _update_offer_and_related_stock(
            stock.offer,
            self._get_serialized_stock_dict(stock, {"price": 550}),
            provider=provider_1,
            offerer_address=stock.offer.offererAddress,
        )
        assert has_been_updated
        assert stock.price == decimal.Decimal("5.50")

    @pytest.mark.parametrize(
        "quantity, expected_quantity",
        [(None, None), (0, 5), (10, 15)],
    )
    def test_should_update_stock_quantity(self, quantity, expected_quantity):
        provider_1 = providers_factories.PublicApiProviderFactory()
        stock = factories.ThingStockFactory(quantity=20, dnBookedQuantity=5, offer__lastProvider=provider_1)
        has_been_updated, _ = _update_offer_and_related_stock(
            stock.offer,
            self._get_serialized_stock_dict(stock, {"quantity": quantity}),
            provider=provider_1,
            offerer_address=stock.offer.offererAddress,
        )
        assert has_been_updated
        assert stock.quantity == expected_quantity

    def test_should_update_stock_quantity_from_unlimited_to_0(self):
        provider_1 = providers_factories.PublicApiProviderFactory()
        stock = factories.ThingStockFactory(quantity=None, dnBookedQuantity=5, offer__lastProvider=provider_1)
        has_been_updated, _ = _update_offer_and_related_stock(
            stock.offer,
            self._get_serialized_stock_dict(stock, {"quantity": 0}),
            provider=provider_1,
            offerer_address=stock.offer.offererAddress,
        )
        assert has_been_updated
        assert stock.quantity == 5

    def test_should_update_stock_booking_limit_datetime(self):
        provider_1 = providers_factories.PublicApiProviderFactory()
        new_booking_limit_datetime = utils_date.get_naive_utc_now() + datetime.timedelta(days=1)
        stock = factories.ThingStockFactory(offer__lastProvider=provider_1)
        has_been_updated, _ = _update_offer_and_related_stock(
            stock.offer,
            self._get_serialized_stock_dict(stock, {"booking_limit_datetime": new_booking_limit_datetime}),
            provider=provider_1,
            offerer_address=stock.offer.offererAddress,
        )
        assert has_been_updated
        assert stock.bookingLimitDatetime == new_booking_limit_datetime

    def test_should_not_update(self):
        provider_1 = providers_factories.PublicApiProviderFactory()
        stock = factories.ThingStockFactory(offer__lastProvider=provider_1)
        has_been_updated, _ = _update_offer_and_related_stock(
            stock.offer,
            self._get_serialized_stock_dict(stock),
            provider=provider_1,
            offerer_address=stock.offer.offererAddress,
        )
        assert not has_been_updated
