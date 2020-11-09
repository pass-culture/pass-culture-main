import pytest

from pcapi.model_creators.generic_creators import create_venue_type
from pcapi.repository import repository
from pcapi.repository.venue_types_queries import get_all_venue_types


class GetAllVenueTypes:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_the_venue_types(self, app):
        # Given
        cinema = create_venue_type(label='Cinema', idx=1)
        musee = create_venue_type(label='Musée', idx=2)
        repository.save(cinema, musee)

        # When
        venue_types = get_all_venue_types()

        # Then
        assert len(venue_types) == 2
        assert cinema in venue_types
        assert musee in venue_types
