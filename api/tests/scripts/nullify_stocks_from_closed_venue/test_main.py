import pytest

from pcapi.core.offerers.factories import VenueFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.offers.models import Stock
from pcapi.scripts.nullify_stocks_from_closed_venue.main import run


pytestmark = pytest.mark.usefixtures("db_session")


def test_run():
    venue = VenueFactory()
    other_venue = VenueFactory()

    stocks = [
        StockFactory(offer__venue=venue, idAtProviders="123@abc"),
        StockFactory(offer__venue=venue, idAtProviders="456@abc"),
    ]

    # similar idAtProviders, different venue
    # -> should not be updated
    other_stocks = [
        StockFactory(offer__venue=other_venue, idAtProviders="1@abc"),
        StockFactory(offer__venue=other_venue, idAtProviders="2@abc"),
    ]

    run(venue.id)

    query = Stock.query.filter(Stock.id.in_({s.id for s in stocks}))
    id_at_providers = {stock.idAtProviders for stock in query}
    assert id_at_providers == {None}

    query = Stock.query.filter(Stock.id.in_({s.id for s in other_stocks}))
    other_id_at_providers = {stock.idAtProviders for stock in query}
    assert other_id_at_providers == {"1@abc", "2@abc"}
