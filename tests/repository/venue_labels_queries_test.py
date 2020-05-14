from repository import repository
from repository.venue_labels_queries import get_all_venue_labels
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue_label


class VenueLabelsQueriesTest:
    class GetAllVenueLabels:
        @clean_database
        def test_should_return_the_venue_labels(self, app):
            # Given
            house = create_venue_label(label='Maison des illustres')
            monuments = create_venue_label(label='Monuments historiques')
            repository.save(house, monuments)

            # When
            venue_labels = get_all_venue_labels()

            # Then
            assert len(venue_labels) == 2
            assert house in venue_labels
            assert monuments in venue_labels
