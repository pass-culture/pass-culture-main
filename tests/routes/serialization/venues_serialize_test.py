from domain.venue.venue import Venue
from routes.serialization.venues_serialize import serialize_venues
from utils.human_ids import humanize


class SerializeVenuesTest:
    def test_should_return_json_with_expected_information(self):
        # Given
        venue_1 = Venue(id=1, name='Librairie Kléber', is_virtual=True)
        venue_2 = Venue(id=2, name='Librairie Réjean', is_virtual=False)

        # When
        response = serialize_venues([venue_1, venue_2])

        # Then
        assert response == [
            {
                'id': f'{humanize(venue_1.id)}',
                'name': venue_1.name,
                'isVirtual': venue_1.is_virtual,
            },
            {
                'id': f'{humanize(venue_2.id)}',
                'name': venue_2.name,
                'isVirtual': venue_2.is_virtual,
            }
        ]
