from unittest.mock import patch

from shapely.geometry import Polygon

from domain.iris import link_venue_to_irises
from models import IrisVenues
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_iris


class LinkVenueToIrisesTest:
    def test_should_not_add_venue_to_iris_venues_when_venue_is_virtual(self,app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, is_virtual=True)

        # When
        link_venue_to_irises(venue)

        # Then
        assert IrisVenues.query.count() == 0


    @clean_database
    @patch('domain.iris.find_ids_of_irises_located_near_venue')
    def test_should_link_venue_to_iris_venues(self, mock_find_iris_near_venue, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)

        polygon_1 = Polygon([(0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)])
        polygon_2 = Polygon([(0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)])

        iris_1 = create_iris(polygon_1)
        iris_2 = create_iris(polygon_2)

        repository.save(venue, iris_1, iris_2)

        mock_find_iris_near_venue.return_value = [iris_1.id, iris_2.id]

        # When
        link_venue_to_irises(venue)

        # Then
        assert IrisVenues.query.count() == 2
