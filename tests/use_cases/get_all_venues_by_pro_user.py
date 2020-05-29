from unittest.mock import MagicMock

from domain.venue.venue import Venue
from infrastructure.repository.venue.venue_sql_repository import VenueSQLRepository
from use_cases.get_all_venues_by_pro_user import GetAllVenuesByProUser


class GetAllVenuesByProUserTest:
    def setup_method(self):
        self.venue_repository = VenueSQLRepository()
        self.venue_repository.get_all_by_pro_identifier = MagicMock()
        self.get_all_venues_by_pro_user = GetAllVenuesByProUser(venue_repository=self.venue_repository)

    def test_user_can_book_an_offer(self, app):
        # Given
        venue = Venue(id=10, name='Librairie Kléber')
        self.venue_repository.get_all_by_pro_identifier.return_value = [venue]

        # When
        pro_venues = self.get_all_venues_by_pro_user.execute(pro_identifier=24)

        # Then
        assert len(pro_venues) == 1
        assert venue in pro_venues
