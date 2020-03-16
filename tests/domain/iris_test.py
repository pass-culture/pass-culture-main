from unittest.mock import patch, MagicMock

from shapely.geometry import Polygon

from domain.iris import _link_venue_to_irises, link_valid_venue_to_irises
from models import IrisVenues
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_iris


class LinkVenueToIrisesTest:
    def test_should_not_add_venue_to_iris_venues_when_venue_is_virtual(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, is_virtual=True)

        # When
        _link_venue_to_irises(venue)

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
        _link_venue_to_irises(venue)

        # Then
        assert IrisVenues.query.count() == 2


class LinkVenueToIrisIfValidTest:
    def test_should_link_venue_to_iris_when_venue_and_offerer_are_validated(self):
        # Given
        mock_link_to_irises = MagicMock()
        venue = MagicMock()
        venue.isValidated = True
        venue.managingOfferer = MagicMock()
        venue.managingOfferer.isValidated = True

        # When
        link_valid_venue_to_irises(venue, mock_link_to_irises)

        # Then
        mock_link_to_irises.assert_called_once_with(venue)

    def test_should_not_link_venue_to_iris_when_venue_is_not_validated_and_offerer_is_validated(self):
        # Given
        mock_link_to_irises = MagicMock()
        venue = MagicMock()
        venue.isValidated = False
        venue.managingOfferer = MagicMock()
        venue.managingOfferer.isValidated = True

        # When
        link_valid_venue_to_irises(venue, mock_link_to_irises)

        # Then
        mock_link_to_irises.assert_not_called()

    def test_should_not_link_venue_to_iris_when_venue_is_validated_and_offerer_is_not_validated(self):
        # Given
        mock_link_to_irises = MagicMock()
        venue = MagicMock()
        venue.isValidated = True
        venue.managingOfferer = MagicMock()
        venue.managingOfferer.isValidated = False

        # When
        link_valid_venue_to_irises(venue, mock_link_to_irises)

        # Then
        mock_link_to_irises.assert_not_called()
