from repository import repository
from repository.venue_types_queries import get_all_venue_types
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue_type


class VenueTypesQueriesTest:
    class GetAllVenueTypes:
        @clean_database
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
