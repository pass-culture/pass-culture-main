from typing import List

import pytest
from pytest import fixture

from pcapi.models import Booking
from pcapi.models import Offer
from pcapi.models import StockSQLEntity
from pcapi.models import UserSQLEntity
from pcapi.models import VenueSQLEntity
from pcapi.sandboxes.scripts.creators.bookings_recap.bookings_recap import save_bookings_recap_sandbox


class BookingsRecapTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_create_bookings_recap_sandbox(self, app: fixture):
        # When
        save_bookings_recap_sandbox()

        # Then
        assert Booking.query.count() == 14
        assert UserSQLEntity.query.count() == 4
        assert Offer.query.count() == 6
        assert StockSQLEntity.query.count() == 6
        assert VenueSQLEntity.query.count() == 4

        assert self._find_bookings_by_user_firstname("Riri") == 4
        assert self._find_bookings_by_user_firstname("Fifi") == 4
        assert self._find_bookings_by_user_firstname("Loulou") == 6

    def _find_bookings_by_user_firstname(self, name: str) -> List[Booking]:
        return Booking.query \
            .join(UserSQLEntity) \
            .filter(UserSQLEntity.firstName == name) \
            .count()
