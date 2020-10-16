import os
from datetime import datetime
from pathlib import Path
import pytest
from unittest.mock import patch, call

from pcapi.models import VenueSQLEntity
from pcapi.repository import repository
from pcapi.scripts.update_venue_creation_date import _read_venue_creation_date_from_file, update_venue_creation_date
from pcapi.model_creators.generic_creators import create_offerer, create_venue


class UpdateVenueCreationDateTest:
    @patch('pcapi.scripts.update_venue_creation_date.logger.info')
    @patch('pcapi.scripts.update_venue_creation_date._read_venue_creation_date_from_file')
    @pytest.mark.usefixtures("db_session")
    def test_should_update_venue_creation_date_whith_date_from_read_file_when_id_match(self, stub_read_venue_date_creation_from_file, mock_logger_info, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer, idx=121)
        repository.save(venue)

        stub_read_venue_date_creation_from_file.return_value = [
            ('121', '2018-12-17 11:22:26.690575')
        ]

        # When
        update_venue_creation_date('fake/path')

        # Then
        updated_venue = VenueSQLEntity.query.one()
        assert updated_venue.dateCreated == datetime(2018, 12, 17, 11, 22, 26, 690575)
        mock_logger_info.assert_called_once_with("1 venues have been updated")

    @patch('pcapi.scripts.update_venue_creation_date.logger.info')
    @patch('pcapi.scripts.update_venue_creation_date._read_venue_creation_date_from_file')
    @pytest.mark.usefixtures("db_session")
    def test_should_not_be_stuck_because_of_unexpected_error_and_print_a_list_of_errored_venues(self, stub_read_venue_date_creation_from_file, mock_logger_info, app):
        # Given
        offerer = create_offerer(siren=None)
        venue1 = create_venue(offerer, name='Nice venue name', idx=121, siret='12345678912354')
        venue2 = create_venue(offerer, idx=99)
        repository.save(venue1, venue2)

        stub_read_venue_date_creation_from_file.return_value = [
            ('121', '2018-12-17 11:22:26.690575'),
            ('99', '2018-12-17 11:22:26.690575')
        ]

        # When
        update_venue_creation_date('fake/path')

        # Then
        updated_venue1 = VenueSQLEntity.query.filter_by(id=121).one()
        updated_venue2 = VenueSQLEntity.query.filter_by(id=99).one()
        assert updated_venue1.dateCreated != datetime(2018, 12, 17, 11, 22, 26, 690575)
        assert updated_venue2.dateCreated != datetime(2018, 12, 17, 11, 22, 26, 690575)
        assert mock_logger_info.call_args_list == [call("Venues in error : 121, 99"),
                                                   call("0 venues have been updated")]

    def test_read_venue_date_creation_from_file(self):
        # Given
        current_directory = Path(os.path.dirname(os.path.realpath(__file__)))
        file_path = f'{current_directory}/../files/venue_creation_date_to_update_test_file.csv'

        # When
        venue_id_and_date = _read_venue_creation_date_from_file(file_path)

        # Then
        assert len(venue_id_and_date) == 1
        assert venue_id_and_date[0] == ('2', '2018-12-17 11:22:26.690575')

