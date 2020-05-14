from unittest.mock import Mock

from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue_label
from use_cases.get_venue_labels import get_venue_labels


class GetVenueLabelsTest:
    @clean_database
    def test_should_return_the_list(self, app):
        # Given
        venue_labels = [create_venue_label(label='Maison des illustres')]
        get_all_venue_labels = Mock(return_value=venue_labels)

        # When
        result = get_venue_labels(get_all_venue_labels)

        # Then
        get_all_venue_labels.assert_called_once()
        assert result == venue_labels
