from unittest.mock import patch

from domain.iris import link_venue_to_iris_venues
from models import IrisVenues
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue


class LinkVenueToIrisVenuesTest:
    def test_should_not_add_venue_to_iris_venues_when_venue_is_virtual(self,app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, is_virtual=True)

        # When
        link_venue_to_iris_venues(venue)

        # Then
        assert IrisVenues.query.count() == 0

    def test_should_not_add_venue_to_iris_venues_when_venue_is_not_validated(self,app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, validation_token='validation_in_progress')

        # When
        link_venue_to_iris_venues(venue)

        # Then
        assert IrisVenues.query.count() == 0

    @clean_database
    @patch('domain.iris.find_iris_located_near_venue')
    def test_should_link_venue_to_iris_venues(self, mock_find_iris_near_venue, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        repository.save(venue)

        mock_find_iris_near_venue.return_value = [1, 2]

        # When
        link_venue_to_iris_venues(venue)

        # Then
        assert IrisVenues.query.count() == 2
