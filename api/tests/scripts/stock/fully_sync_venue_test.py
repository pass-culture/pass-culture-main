import pytest
import requests_mock

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.factories as providers_factories
from pcapi.scripts.stock import fully_sync_venue


@pytest.mark.usefixtures("db_session")
def test_fully_sync_venue():
    api_url = "https://example.com/provider/api"
    provider = providers_factories.APIProviderFactory(apiUrl=api_url)
    venue_provider = providers_factories.VenueProviderFactory(provider=provider)
    venue = venue_provider.venue
    stock = offers_factories.StockFactory(quantity=10, offer__venue=venue, offer__idAtProvider="1")
    bookings_factories.BookingFactory(stock=stock)
    product2 = offers_factories.ProductFactory(
        idAtProviders="1234",
        extraData={"prix_livre": 10},
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )

    with requests_mock.Mocker() as mock:
        response = {
            "total": 1,
            "stocks": [{"ref": "1234", "available": 5, "price": 10}],
        }
        mock.get(f"{api_url}/{venue_provider.venueIdAtOfferProvider}", [{"json": response}, {"json": {"stocks": []}}])
        fully_sync_venue.fully_sync_venue(venue)

    # Check that the quantity of existing stocks has been reset.
    assert stock.quantity == 1
    # Check that offers and stocks have been created or updated.
    offer2 = offers_models.Offer.query.filter_by(product=product2).one()
    assert offer2.stocks[0].quantity == 5
