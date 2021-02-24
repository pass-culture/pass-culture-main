import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.repository.booking_queries import count_active_bookings_for_venue


class GetActiveBookingsCountTest:
    @pytest.mark.usefixtures("db_session")
    def test_return_bookings_quantity_for_venue(self):
        # Given
        booking = bookings_factories.BookingFactory()
        venue = booking.stock.offer.venue
        bookings_factories.BookingFactory(stock__offer__venue=venue)

        # When
        active_bookings_count = count_active_bookings_for_venue(venue.id)

        # Then
        assert active_bookings_count == 2

    @pytest.mark.usefixtures("db_session")
    def test_excludes_used_or_cancelled_bookings(self):
        # Given
        booking = bookings_factories.BookingFactory()
        venue = booking.stock.offer.venue
        bookings_factories.BookingFactory(isUsed=True, stock__offer__venue=venue)
        bookings_factories.BookingFactory(isCancelled=True, stock__offer__venue=venue)

        # When
        active_bookings_count = count_active_bookings_for_venue(venue.id)

        # Then
        assert active_bookings_count == 1

    @pytest.mark.usefixtures("db_session")
    def test_excludes_other_venues_bookings(self):
        # Given
        booking = bookings_factories.BookingFactory()
        venue = booking.stock.offer.venue
        another_venue = offers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        bookings_factories.BookingFactory(stock__offer__venue=another_venue)

        # When
        active_bookings_count = count_active_bookings_for_venue(venue.id)

        # Then
        assert active_bookings_count == 1
