from domain.venue.venue_label.venue_label import VenueLabel
from routes.serialization.venue_labels_serialize import serialize_venue_label


class SerializeVenueLabelsTest:
    def test_should_return_dict_with_expected_information(self):
        # Given
        venue_label = VenueLabel(identifier=12, label='Maison des illustres')

        # When
        response = serialize_venue_label(venue_label)

        # Then
        assert response == {
            'id': 'BQ',
            'label': 'Maison des illustres'
        }
