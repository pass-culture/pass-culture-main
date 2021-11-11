import os
from pathlib import Path
from unittest.mock import patch

import pytest

from pcapi.core.offerers.factories import VenueTypeFactory
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.models import Venue
from pcapi.scripts.update_venue_type import _read_venue_type_from_file
from pcapi.scripts.update_venue_type import update_venue_type


class UpdateVenueTypeTest:
    @patch("pcapi.scripts.update_venue_type._read_venue_type_from_file")
    @pytest.mark.usefixtures("db_session")
    def test_should_update_venue_type_whith_type_from_read_file_when_id_match(
        self, stub_read_venue_type_from_file, app, capsys
    ):
        # Given
        VenueTypeFactory(label="old_type", id=1)
        VenueTypeFactory(label="new_type", id=2)
        VenueFactory(id=121, venueTypeId=1)

        stub_read_venue_type_from_file.return_value = [("121", "new_type")]

        # When
        update_venue_type("fake/path")

        # Then
        captured = capsys.readouterr()
        updated_venue = Venue.query.one()
        assert updated_venue.venueTypeId == 2
        assert "1 venues have been updated" in captured.out

    @patch("pcapi.scripts.update_venue_type._read_venue_type_from_file")
    @pytest.mark.usefixtures("db_session")
    def test_should_not_be_stuck_because_of_no_siren_offerer_and_print_a_list_of_errored_venues(
        self, stub_read_venue_type_from_file, app, capsys
    ):
        # Given
        offerer = OffererFactory(siren=None)
        VenueTypeFactory(label="old_type", id=1)
        VenueTypeFactory(label="new_type", id=25)
        VenueFactory(managingOfferer=offerer, name="CMOI", id=121, venueTypeId=1)
        VenueFactory(managingOfferer=offerer, name="AUSSI MOI", id=99, siret="12345678912354", venueTypeId=1)

        stub_read_venue_type_from_file.return_value = [("121", "new_type"), ("99", "new_type")]

        # When
        update_venue_type("fake/path")

        # Then
        captured = capsys.readouterr()
        updated_venue1 = Venue.query.filter_by(id=121).one()
        updated_venue2 = Venue.query.filter_by(id=99).one()
        assert updated_venue1.venueTypeId == 1
        assert updated_venue2.venueTypeId == 1
        assert "0 venues have been updated" in captured.out
        assert "Venues in error : 121, 99" in captured.out

    @patch("pcapi.scripts.update_venue_type._read_venue_type_from_file")
    @pytest.mark.usefixtures("db_session")
    def test_should_not_update_venue_type_whith_type_from_read_file_when_venue_id_does_not_match(
        self, stub_read_venue_type_from_file, app, capsys
    ):
        # Given
        VenueTypeFactory(label="old_type", id=1)
        VenueTypeFactory(label="new_type", id=2)
        VenueFactory(id=121, venueTypeId=1)

        stub_read_venue_type_from_file.return_value = [("666", "new_type")]

        # When
        update_venue_type("fake/path")

        # Then
        captured = capsys.readouterr()
        updated_venue = Venue.query.one()
        assert updated_venue.venueTypeId == 1
        assert "venue not found for id : 666" in captured.out
        assert "0 venues have been updated" in captured.out

    @patch("pcapi.scripts.update_venue_type._read_venue_type_from_file")
    @pytest.mark.usefixtures("db_session")
    def test_should_not_update_venue_type_whith_type_from_read_file_when_type_label_does_not_match(
        self, stub_read_venue_type_from_file, app, capsys
    ):
        # Given
        VenueTypeFactory(label="old_type", id=1)
        VenueFactory(id=121, venueTypeId=1)

        stub_read_venue_type_from_file.return_value = [("121", "other_type")]

        # When
        update_venue_type("fake/path")

        # Then
        captured = capsys.readouterr()
        updated_venue = Venue.query.one()
        assert updated_venue.venueTypeId == 1
        assert "venue type id not found for label : other_type and venueId : 121" in captured.out
        assert "0 venues have been updated" in captured.out

    def test_read_venue_type_from_file(self):
        # Given
        current_directory = Path(os.path.dirname(os.path.realpath(__file__)))
        file_path = f"{current_directory}/../files/venue_type_to_update_test_file.csv"

        # When
        venue_id_and_type = _read_venue_type_from_file(file_path)

        # Then
        assert len(venue_id_and_type) == 3
        assert venue_id_and_type[0] == ("a_venue_id", "a_type")
        assert venue_id_and_type[1] == ("another_venue_id", "another_type")
        assert venue_id_and_type[2] == ("venue_id", "another_type, with a comma")
