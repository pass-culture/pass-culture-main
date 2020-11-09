from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from shapely.geometry import Polygon

from pcapi.domain.iris import MAXIMUM_DISTANCE_IN_METERS
from pcapi.model_creators.generic_creators import create_iris
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.models import IrisVenues
from pcapi.repository import repository
from pcapi.scripts.iris.link_iris_to_venues import _find_all_venue_ids_to_link
from pcapi.scripts.iris.link_iris_to_venues import link_irises_to_existing_physical_venues


class LinkIrisesToExistingPhysicalVenuesTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_link_existing_eligible_venue_to_existing_iris(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, longitude=2.351499, latitude=48.856610)
        polygon = Polygon([(2.086668, 49.440898), (2.086668, 49.440902),
                           (2.086672, 49.440902), (2.086672, 49.440898)])
        iris = create_iris(polygon)
        repository.save(iris, venue)

        # When
        link_irises_to_existing_physical_venues(MAXIMUM_DISTANCE_IN_METERS)

        # Then
        assert IrisVenues.query.count() == 1

    @pytest.mark.usefixtures("db_session")
    @patch('pcapi.scripts.iris.link_iris_to_venues._find_all_venue_ids_to_link')
    @patch('pcapi.scripts.iris.link_iris_to_venues.find_ids_of_irises_located_near_venue')
    @patch('pcapi.scripts.iris.link_iris_to_venues.link_irises_to_existing_physical_venues')
    def test_should_look_for_irises_located_near_each_venue_to_link(self, insert_venue_in_iris_venue,
                                                                    find_ids_of_irises_located_near_venue,
                                                                    _find_all_venues_to_link, app):
        # Given
        number_of_venues_to_link = 5
        mocked_venues_to_link = range(1, number_of_venues_to_link + 1)
        _find_all_venues_to_link.return_value = mocked_venues_to_link

        # When
        link_irises_to_existing_physical_venues(MAXIMUM_DISTANCE_IN_METERS)

        # Then
        assert find_ids_of_irises_located_near_venue.call_count == 5
        find_ids_of_irises_located_near_venue.assert_called_with(5, 100000)

    @pytest.mark.usefixtures("db_session")
    @patch('pcapi.scripts.iris.link_iris_to_venues._find_all_venue_ids_to_link')
    @patch('pcapi.scripts.iris.link_iris_to_venues.find_ids_of_irises_located_near_venue')
    @patch('pcapi.scripts.iris.link_iris_to_venues.insert_venue_in_iris_venue')
    def test_should_link_each_venue_to_nearby_irises(self, insert_venue_in_iris_venue,
                                                     find_ids_of_irises_located_near_venue, _find_all_venues_to_link,
                                                     app):
        # Given
        number_of_venues_to_link = 5
        mocked_venues_to_link = range(1, number_of_venues_to_link + 1)
        _find_all_venues_to_link.return_value = mocked_venues_to_link
        find_ids_of_irises_located_near_venue.return_value = [1, 2, 3]

        # When
        link_irises_to_existing_physical_venues(MAXIMUM_DISTANCE_IN_METERS)

        # Then
        assert insert_venue_in_iris_venue.call_count == 5
        insert_venue_in_iris_venue.assert_called_with(5, [1, 2, 3])


class FindAllVenueIdsToLinkTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_ids_of_virtual_venues(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, is_virtual=True, address=None, departement_code=None, postal_code=None,
                             siret=None)
        repository.save(venue)

        # When
        venues = _find_all_venue_ids_to_link()

        # Then
        assert len(venues) == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_non_validated_venue_ids(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, validation_token='1234567')
        repository.save(venue)

        # When
        venues = _find_all_venue_ids_to_link()

        # Then
        assert len(venues) == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_venue_ids_of_non_validated_offerers(self, app):
        # Given
        offerer = create_offerer(validation_token='1234567')
        venue = create_venue(offerer)
        repository.save(venue)

        # When
        venues = _find_all_venue_ids_to_link()

        # Then
        assert len(venues) == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_return_validated_physical_venue_ids(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        repository.save(venue)

        # When
        venues = _find_all_venue_ids_to_link()

        # Then
        assert venues == [venue.id]
