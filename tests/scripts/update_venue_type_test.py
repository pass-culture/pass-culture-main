import os
from pathlib import Path
from unittest.mock import patch

from models import VenueSQLEntity
from repository import repository
from scripts.update_venue_type import _read_venue_type_from_file, update_venue_type
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_venue_type


class UpdateVenueTypeTest:
    @patch('scripts.update_venue_type._read_venue_type_from_file')
    @clean_database
    def test_should_update_venue_type_whith_type_from_read_file_when_id_match(self, stub_read_venue_type_from_file, app):
        # Given
        offerer = create_offerer()
        old_venue_type = create_venue_type('old_type', 1)
        new_venue_type = create_venue_type('new_type', 2)
        venue = create_venue(offerer, idx=121,  venue_type_id=1)
        repository.save(venue, old_venue_type, new_venue_type)

        stub_read_venue_type_from_file.return_value = [
            ('121', 'new_type')
        ]

        # When
        update_venue_type('fake/path')

        # Then
        venue = VenueSQLEntity.query.one()
        print(venue.id)
        assert venue.venueTypeId == 2

    @patch('scripts.update_venue_type._read_venue_type_from_file')
    @clean_database
    def test_should_not_update_venue_type_whith_type_from_read_file_when_id_does_not_match(self, stub_read_venue_type_from_file, app):
        # Given
        offerer = create_offerer()
        old_venue_type = create_venue_type('old_type', 1)
        new_venue_type = create_venue_type('new_type', 2)
        venue = create_venue(offerer, idx=121,  venue_type_id=1)
        repository.save(venue, old_venue_type, new_venue_type)

        stub_read_venue_type_from_file.return_value = [
            ('666', 'new_type')
        ]

        # When
        update_venue_type('fake/path')

        # Then
        venue = VenueSQLEntity.query.one()
        assert venue.venueTypeId == 1

    @patch('scripts.update_venue_type._read_venue_type_from_file')
    @clean_database
    def test_should_not_update_venue_type_whith_type_from_read_file_when_type_label_does_not_match(self, stub_read_venue_type_from_file, app):
        # Given
        offerer = create_offerer()
        old_venue_type = create_venue_type('old_type', 1)
        venue = create_venue(offerer, idx=121,  venue_type_id=1)
        repository.save(venue, old_venue_type)

        stub_read_venue_type_from_file.return_value = [
            ('121', 'other_type')
        ]

        # When
        update_venue_type('fake/path')

        # Then
        venue = VenueSQLEntity.query.one()
        assert venue.venueTypeId == 1


    def test_read_venue_type_from_file(self):
        # Given
        current_directory = Path(os.path.dirname(os.path.realpath(__file__)))
        file_path = f'{current_directory}/../files/venue_type_to_update_test_file.csv'

        # When
        venue_id_and_type = _read_venue_type_from_file(file_path)

        # Then
        assert len(venue_id_and_type) == 2
        assert venue_id_and_type[0] == ('a_venue_id', 'a_type')
        assert venue_id_and_type[1] == ('another_venue_id', 'another_type')
