import datetime
import decimal

import pytest

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.routes.public.individual_offers.v1.services import products as products_service
from pcapi.utils import date as date_utils


@pytest.mark.usefixtures("db_session")
class CreateOrUpdateEanOffersTest:

    @staticmethod
    def _get_isoformat_date(date_to_format: datetime.datetime | None = None) -> tuple[datetime.datetime, str]:
        in_ten_minutes = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(minutes=10)
        date_to_format = date_to_format or in_ten_minutes
        date_to_format_in_non_utc_tz = date_utils.utc_datetime_to_department_timezone(date_to_format, "973")
        return date_to_format, date_to_format_in_non_utc_tz.isoformat()

    def setup_product(
        self, ean: str = "1234567890123", subcategoryId: str | None = None
    ) -> tuple[str, offers_models.Product]:
        product = offers_factories.ThingProductFactory(
            subcategoryId=subcategoryId or subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            extraData={"ean": ean},
        )
        return ean, product

    def test_should_update_existing_stock_of_existing_offer(self):
        provider = providers_factories.PublicApiProviderFactory()
        venue = offerers_factories.VenueFactory()
        ean, product = self.setup_product()
        offer = offers_factories.ThingOfferFactory(
            product=product,
            venue=venue,
            lastProvider=provider,
            extraData=product.extraData,
        )
        stock = offers_factories.ThingStockFactory(offer=offer, quantity=10, price=100)
        booking_limit_date, booking_limit_isoformat = self._get_isoformat_date()
        products_service.create_or_update_ean_offers(
            {ean: {"quantity": 20, "price": 3456, "booking_limit_datetime": booking_limit_isoformat}},
            venue_id=venue.id,
            provider_id=provider.id,
        )

        assert stock.quantity == 20
        assert stock.price == decimal.Decimal("34.56")
        assert stock.offerId == offer.id
        assert stock.bookingLimitDatetime == booking_limit_date

    def test_should_create_stock_of_existing_offer(self):
        provider = providers_factories.PublicApiProviderFactory()
        venue = offerers_factories.VenueFactory()
        ean, product = self.setup_product()
        offer = offers_factories.ThingOfferFactory(
            product=product,
            venue=venue,
            lastProvider=provider,
            extraData=product.extraData,
        )
        assert len(offer.stocks) == 0

        products_service.create_or_update_ean_offers(
            {ean: {"quantity": 20, "price": 3456, "booking_limit_datetime": None}},
            venue_id=venue.id,
            provider_id=provider.id,
        )

        assert len(offer.stocks) == 1
        stock = offer.stocks[0]
        assert stock.quantity == 20
        assert stock.price == decimal.Decimal("34.56")
        assert stock.offerId == offer.id
