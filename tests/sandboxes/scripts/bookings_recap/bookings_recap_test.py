from typing import List

from pytest import fixture

from models import BookingSQLEntity, UserSQLEntity, StockSQLEntity, VenueSQLEntity, OfferSQLEntity
from sandboxes.scripts.creators.bookings_recap.bookings_recap import save_bookings_recap_sandbox
import pytest


class BookingsRecapTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_create_bookings_recap_sandbox(self, app: fixture):
        # When
        save_bookings_recap_sandbox()

        # Then
        assert BookingSQLEntity.query.count() == 14
        assert UserSQLEntity.query.count() == 4
        assert OfferSQLEntity.query.count() == 6
        assert StockSQLEntity.query.count() == 6
        assert VenueSQLEntity.query.count() == 4

        assert self._find_bookings_by_user_firstname("Riri") == 4
        assert self._find_bookings_by_user_firstname("Fifi") == 4
        assert self._find_bookings_by_user_firstname("Loulou") == 6

    def _find_bookings_by_user_firstname(self, name: str) -> List[BookingSQLEntity]:
        return BookingSQLEntity.query \
            .join(UserSQLEntity) \
            .filter(UserSQLEntity.firstName == name) \
            .count()
