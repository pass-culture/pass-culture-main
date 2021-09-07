import pytest

from pcapi.core import search
import pcapi.core.bookings.api as bookings_api
import pcapi.core.offers.factories as offers_factories
import pcapi.core.search.testing as search_testing
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_offer_indexation_on_booking_cycle(app):
    beneficiary = users_factories.BeneficiaryGrant18Factory()
    stock = offers_factories.StockFactory(quantity=1)
    offer = stock.offer
    assert search_testing.search_store == {}

    search.async_index_offer_ids([offer.id])
    assert search_testing.search_store == {}

    search.index_offers_in_queue()
    assert offer.id in search_testing.search_store

    booking = bookings_api.book_offer(beneficiary, stock.id, quantity=1)
    search.index_offers_in_queue()
    assert offer.id not in search_testing.search_store

    bookings_api.cancel_booking_by_beneficiary(beneficiary, booking)
    search.index_offers_in_queue()
    assert offer.id in search_testing.search_store


def test_offer_indexation_on_venue_cycle(app):
    stock = offers_factories.StockFactory(quantity=1)
    offer = stock.offer
    venue = offer.venue
    assert search_testing.search_store == {}

    search.async_index_venue_ids([venue.id])
    assert search_testing.search_store == {}

    search.index_venues_in_queue()
    assert offer.id in search_testing.search_store
