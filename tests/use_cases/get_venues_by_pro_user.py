from unittest.mock import MagicMock

from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from pcapi.infrastructure.repository.venue.venue_with_offerer_name.venue_with_offerer_name_sql_repository import \
    VenueWithOffererNameSQLRepository
from pcapi.use_cases.get_venues_by_pro_user import GetVenuesByProUser


class GetAllVenuesByProUserTest:
    def setup_method(self) -> None:
        self.venue_repository = VenueWithOffererNameSQLRepository()
        self.venue_repository.get_by_pro_identifier = MagicMock()
        self.get_all_venues_by_pro_user = GetVenuesByProUser(venue_repository=self.venue_repository)

    def test_get_all_venue_by_pro_user(self) -> None:
        # Given
        venue = VenueWithOffererName(identifier=10, name='Librairie Kléber', offerer_name='Gilbert Joseph',
                                     is_virtual=False)
        self.venue_repository.get_by_pro_identifier.return_value = [venue]

        # When
        pro_venues = self.get_all_venues_by_pro_user.execute(pro_identifier=24, user_is_admin=False)

        # Then
        assert len(pro_venues) == 1
        assert venue in pro_venues
