import pytest

from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.offers.models import Offer
from pcapi.scripts.deactivate_300e_thing_offers import deactivate_300e_thing_offers


class Deactivate300eThingOffersTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_deactivate_thing_offers_that_are_higher_than_300e(self):
        # Given
        ThingStockFactory(price=305)
        ThingStockFactory(price=315)
        ThingStockFactory(price=103)
        ThingStockFactory(price=300)
        EventStockFactory(price=310)
        EventStockFactory(price=297)

        # When
        deactivate_300e_thing_offers()

        # Then
        deactivated_offers = Offer.query.filter_by(isActive=False).all()
        assert len(deactivated_offers) == 2
