import pytest
import requests_mock

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.scripts.stock import fully_sync_venue


@pytest.mark.usefixtures("db_session")
def test_fully_sync_venue():
    api_url = "https://example.com/provider/api"
    provider = offerers_factories.APIProviderFactory(apiUrl=api_url)
    venue_provider = offerers_factories.VenueProviderFactory(provider=provider)
    venue = venue_provider.venue
    stock = offers_factories.StockFactory(quantity=10, offer__venue=venue, offer__idAtProviders="1")
    bookings_factories.BookingFactory(stock=stock)
    product2 = offers_factories.ProductFactory(
        idAtProviders="1234",
        extraData={"prix_livre": 10},
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )

    with requests_mock.Mocker() as mock:
        response = {
            "total": 1,
            "stocks": [{"ref": "1234", "available": 5}],
        }
        mock.get(f"{api_url}/{venue_provider.venueIdAtOfferProvider}", [{"json": response}, {"json": {"stocks": []}}])
        fully_sync_venue.fully_sync_venue(venue)

    # Check that the quantity of existing stocks has been reset.
    assert stock.quantity == 1
    # Check that offers and stocks have been created or updated.
    offer2 = offers_models.Offer.query.filter_by(product=product2).one()
    assert offer2.stocks[0].quantity == 5


@pytest.mark.usefixtures("db_session")
def test_fully_sync_venue_with_new_provider():
    api_url = "https://example.com/provider/api"
    provider = offerers_factories.APIProviderFactory()
    venue_provider = offerers_factories.VenueProviderFactory(provider=provider)
    venue = venue_provider.venue
    stock = offers_factories.StockFactory(quantity=10, offer__venue=venue, offer__idAtProviders="1")
    bookings_factories.BookingFactory(stock=stock)
    product2 = offers_factories.ProductFactory(
        idAtProviders="1234",
        extraData={"prix_livre": 10},
        subcategoryId=subcategories.LIVRE_PAPIER.id,
    )
    new_provider = offerers_factories.APIProviderFactory(apiUrl=api_url)

    with requests_mock.Mocker() as mock:
        response = {
            "total": 1,
            "stocks": [{"ref": "1234", "available": 5}],
        }
        mock.get(f"{api_url}/{venue_provider.venueIdAtOfferProvider}", [{"json": response}, {"json": {"stocks": []}}])
        fully_sync_venue.fully_sync_venue_with_new_provider(venue, new_provider.id)

    # Check venue_provider has change provider
    assert len(venue.venueProviders) == 1
    assert venue.venueProviders[0].providerId == new_provider.id
    # Check that the quantity of existing stocks has been reset.
    assert stock.quantity == 1
    assert stock.offer.lastProviderId == new_provider.id
    # Check that offers and stocks have been created or updated.
    offer2 = offers_models.Offer.query.filter_by(product=product2).one()
    assert offer2.stocks[0].quantity == 5
    assert offer2.lastProviderId == new_provider.id


@pytest.mark.usefixtures("db_session")
def test_reset_stock_quantity():
    offer = offers_factories.OfferFactory(idAtProviders="1")
    venue = offer.venue
    stock1_no_bookings = offers_factories.StockFactory(offer=offer, quantity=10)
    stock2_only_cancelled_bookings = offers_factories.StockFactory(offer=offer, quantity=10)
    bookings_factories.BookingFactory(
        stock=stock2_only_cancelled_bookings, isCancelled=True, status=BookingStatus.CANCELLED
    )
    stock3_mix_of_bookings = offers_factories.StockFactory(offer=offer, quantity=10)
    bookings_factories.BookingFactory(stock=stock3_mix_of_bookings)
    bookings_factories.BookingFactory(stock=stock3_mix_of_bookings, isCancelled=True, status=BookingStatus.CANCELLED)
    manually_added_offer = offers_factories.OfferFactory(venue=venue)
    stock4_manually_added = offers_factories.StockFactory(offer=manually_added_offer, quantity=10)
    stock5_other_venue = offers_factories.StockFactory(quantity=10)

    fully_sync_venue._reset_stock_quantity(venue)

    assert stock1_no_bookings.quantity == 0
    assert stock2_only_cancelled_bookings.quantity == 0
    assert stock3_mix_of_bookings.quantity == 1
    assert stock4_manually_added.quantity == 10
    assert stock5_other_venue.quantity == 10
