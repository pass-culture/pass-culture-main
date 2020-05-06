from typing import List

from models import Booking, User, Stock, Venue, Offer
from sandboxes.scripts.creators.bookings_recap.bookings_recap import save_bookings_recap_sandbox
from tests.conftest import clean_database


class BookingsRecapTest:
    @clean_database
    def test_should_create_bookings_recap_sandbox(self, app):
        # When
        save_bookings_recap_sandbox()

        # Then
        assert Booking.query.count() == 10
        assert User.query.count() == 4
        assert Stock.query.count() == 4
        assert Venue.query.count() == 3
        assert Offer.query.count() == 4

        assert self._find_bookings_by_user_firstname("Riri") == 3
        assert self._find_bookings_by_user_firstname("Fifi") == 3
        assert self._find_bookings_by_user_firstname("Loulou") == 4

    def _find_bookings_by_user_firstname(self, name: str) -> List[Booking]:
        return Booking.query \
            .join(User) \
            .filter(User.firstName == name) \
            .count()
