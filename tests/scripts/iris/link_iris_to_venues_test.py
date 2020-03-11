from unittest.mock import patch, MagicMock

from shapely.geometry import Polygon

from models import IrisVenues
from repository import repository
from scripts.iris.link_iris_to_venues import link_irises_to_existing_physical_venues, _find_all_venues_to_link
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_iris, create_venue, create_offerer


class LinkIrisesToExistingPhysicalVenuesTest:
    @clean_database
    def test_should_link_existing_eligible_venue_to_existing_iris(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, longitude=2.351499, latitude=48.856610)
        polygon = Polygon([(2.086668, 49.440898), (2.086668, 49.440902),
                           (2.086672, 49.440902), (2.086672, 49.440898)])
        iris = create_iris(polygon)
        repository.save(iris, venue)

        # When
        link_irises_to_existing_physical_venues()

        # Then
        iris_venues = IrisVenues.query.all()
        assert len(iris_venues) == 1

    @clean_database
    @patch('scripts.iris.link_iris_to_venues._find_all_venues_to_link')
    @patch('scripts.iris.link_iris_to_venues.find_ids_of_irises_located_near_venue')
    @patch('scripts.iris.link_iris_to_venues.link_irises_to_existing_physical_venues')
    def test_should_look_for_irises_located_near_each_venue_to_link(self, insert_venue_in_iris_venue,
                                                                    find_ids_of_irises_located_near_venue,
                                                                    _find_all_venues_to_link, app):
        # Given
        number_of_venues_to_link = 5
        mocked_venues_to_link = [MagicMock(id=i) for i in range(number_of_venues_to_link)]
        _find_all_venues_to_link.return_value = mocked_venues_to_link

        # When
        link_irises_to_existing_physical_venues()

        # Then
        assert find_ids_of_irises_located_near_venue.call_count == 5
        find_ids_of_irises_located_near_venue.assert_called_with(4)

    @clean_database
    @patch('scripts.iris.link_iris_to_venues._find_all_venues_to_link')
    @patch('scripts.iris.link_iris_to_venues.find_ids_of_irises_located_near_venue')
    @patch('scripts.iris.link_iris_to_venues.insert_venue_in_iris_venue')
    def test_should_link_each_venue_to_nearby_irises(self, insert_venue_in_iris_venue,
                                                     find_ids_of_irises_located_near_venue, _find_all_venues_to_link,
                                                     app):
        # Given
        number_of_venues_to_link = 5
        mocked_venues_to_link = [MagicMock(id=i) for i in range(number_of_venues_to_link)]
        _find_all_venues_to_link.return_value = mocked_venues_to_link
        find_ids_of_irises_located_near_venue.return_value = [1, 2, 3]

        # When
        link_irises_to_existing_physical_venues()

        # Then
        assert insert_venue_in_iris_venue.call_count == 5
        insert_venue_in_iris_venue.assert_called_with(4, [1, 2, 3])


class FindAllVenuesToLinkTest:
    @clean_database
    def test_should_not_return_virtual_venues(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, is_virtual=True, address=None, departement_code=None, postal_code=None,
                             siret=None)
        repository.save(venue)

        # When
        venues = _find_all_venues_to_link()

        # Then
        assert len(venues) == 0

    @clean_database
    def test_should_not_return_non_validated_venues(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, validation_token='1234567')
        repository.save(venue)

        # When
        venues = _find_all_venues_to_link()

        # Then
        assert len(venues) == 0

    @clean_database
    def test_should_not_return_venues_of_non_validated_offerers(self, app):
        # Given
        offerer = create_offerer(validation_token='1234567')
        venue = create_venue(offerer)
        repository.save(venue)

        # When
        venues = _find_all_venues_to_link()

        # Then
        assert len(venues) == 0

    @clean_database
    def test_should_return_validated_physical_venues(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        repository.save(venue)

        # When
        venues = _find_all_venues_to_link()

        # Then
        assert len(venues) == 1
