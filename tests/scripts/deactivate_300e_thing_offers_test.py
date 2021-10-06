import pytest

from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.repository import repository

from pcapi.core.offers.models import Offer
from pcapi.scripts.deactivate_300e_thing_offers import deactivate_300e_thing_offers


class Deactivate300eThingOffersTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_deactivate_thing_offers_that_are_higher_than_300e(self):
        # Given
        stock_to_deactivate = ThingStockFactory(price=305)
        stock_to_deactivate_1 = ThingStockFactory(price=315)
        thing_stock_to_keep = ThingStockFactory(price=103)
        thing_stock_to_keep_1 = ThingStockFactory(price=300)
        event_stock_to_keep = EventStockFactory(price=310)
        event_stock_to_keep_1 = EventStockFactory(price=297)

        # When
        deactivate_300e_thing_offers()

        # Then
        deactivated_offers = Offer.query.filter_by(isActive=False).all()
        assert len(deactivated_offers) == 2
