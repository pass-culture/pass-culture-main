from typing import List

from models import BookingSQLEntity, UserSQLEntity, StockSQLEntity, VenueSQLEntity, Offer
from sandboxes.scripts.creators.bookings_recap.bookings_recap import save_bookings_recap_sandbox
from tests.conftest import clean_database


class BookingsRecapTest:
    @clean_database
    def test_should_create_bookings_recap_sandbox(self, app):
        # When
        save_bookings_recap_sandbox()

        # Then
        assert BookingSQLEntity.query.count() == 11
        assert UserSQLEntity.query.count() == 4
        assert StockSQLEntity.query.count() == 5
        assert VenueSQLEntity.query.count() == 4
        assert Offer.query.count() == 5

        assert self._find_bookings_by_user_firstname("Riri") == 3
        assert self._find_bookings_by_user_firstname("Fifi") == 3
        assert self._find_bookings_by_user_firstname("Loulou") == 5

    def _find_bookings_by_user_firstname(self, name: str) -> List[BookingSQLEntity]:
        return BookingSQLEntity.query \
            .join(UserSQLEntity) \
            .filter(UserSQLEntity.firstName == name) \
            .count()
