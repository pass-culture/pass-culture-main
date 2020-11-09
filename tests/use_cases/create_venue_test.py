from unittest.mock import Mock
from unittest.mock import patch

from pcapi.models import VenueSQLEntity
from pcapi.use_cases.create_venue import create_venue


class CreateVenueTest:
    @patch('pcapi.use_cases.create_venue.link_valid_venue_to_irises')
    def test_should_save_a_venue(self, mocked_link_valid_venue_to_irises):
        # Given
        venue_properties = {
            'name': 'Mon théâtre préféré'
        }
        mocked_save = Mock()

        # When
        new_venue = create_venue(venue_properties, mocked_save)

        # Then
        assert isinstance(new_venue, VenueSQLEntity)
        assert new_venue.name == 'Mon théâtre préféré'
        mocked_save.assert_called_once_with(VenueSQLEntity(from_dict=venue_properties))

    @patch('pcapi.use_cases.create_venue.link_valid_venue_to_irises')
    def test_should_link_venue_to_irises(self, mocked_link_valid_venue_to_irises):
        # Given
        venue_properties = {
            'name': 'Mon théâtre préféré'
        }
        mocked_save = Mock()

        # When
        create_venue(venue_properties, mocked_save)

        # Then
        venue = VenueSQLEntity(from_dict=venue_properties)
        mocked_link_valid_venue_to_irises.assert_called_once_with(venue=venue)
