from pcapi.domain.venues import is_algolia_indexing
from pcapi.model_creators.generic_creators import create_offerer, create_venue
from pcapi.routes.serialization import as_dict


class IsAlgoliaIndexingTest:
    def when_changes_on_name_are_triggered(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, name='old names')
        payload = {
            'name': 'my new name'
        }

        # When
        result = is_algolia_indexing(venue, payload)

        # Then
        assert result == True

    def when_changes_on_public_name_are_triggered(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, public_name='old name')
        payload = {
            'publicName': 'my new name'
        }

        # When
        result = is_algolia_indexing(venue, payload)

        # Then
        assert result == True

    def when_changes_on_city_are_triggered(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, city='old City')
        payload = {
            'city': 'My new city'
        }

        # When
        result = is_algolia_indexing(venue, payload)

        # Then
        assert result == True

    def when_changes_are_not_on_algolia_fields_it_should_return_false(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        payload = {
            'siret': '7896542311234',
            'banana': None
        }

        # When
        result = is_algolia_indexing(venue, payload)

        # Then
        assert result == False

    def when_changes_in_payload_are_same_as_previous_it_should_return_false(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, city='old City')
        payload = {
            'city': 'old City'
        }

        # When
        result = is_algolia_indexing(venue, payload)

        # Then
        assert result == False

