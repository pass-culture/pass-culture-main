import os
from pathlib import Path
from unittest.mock import patch

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offerers.models import Venue
from pcapi.scripts.update_venue_type import _read_venue_type_from_file
from pcapi.scripts.update_venue_type import update_venue_type


class UpdateVenueTypeTest:
    @patch("pcapi.scripts.update_venue_type._read_venue_type_from_file")
    @pytest.mark.usefixtures("db_session")
    def test_should_update_venue_type_whith_type_from_read_file_when_id_match(
        self, stub_read_venue_type_from_file, app, capsys
    ):
        # Given
        offerers_factories.VenueTypeFactory(label="old_type", id=1)
        offerers_factories.VenueTypeFactory(label="new_type", id=2)
        offerers_factories.VenueFactory(id=121, venueTypeId=1)

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
        self, stub_read_venue_type_from_file, app
    ):
        # Given
        offerer = offerers_factories.OffererFactory(siren=None)
        old_venue_type = offerers_factories.VenueTypeFactory(label="old_type")
        offerers_factories.VenueTypeFactory(label="new_type")
        venue1 = offerers_factories.VenueFactory(managingOfferer=offerer, name="CMOI", venueType=old_venue_type)
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=offerer, name="AUSSI MOI", siret="12345678912354", venueType=old_venue_type
        )

        stub_read_venue_type_from_file.return_value = [("121", "new_type"), ("99", "new_type")]

        # When
        update_venue_type("fake/path")

        # Then
        updated_venue1 = Venue.query.get(venue1.id)
        updated_venue2 = Venue.query.get(venue2.id)
        assert updated_venue1.venueTypeId == old_venue_type.id
        assert updated_venue2.venueTypeId == old_venue_type.id

    @patch("pcapi.scripts.update_venue_type._read_venue_type_from_file")
    @pytest.mark.usefixtures("db_session")
    def test_should_not_update_venue_type_whith_type_from_read_file_when_venue_id_does_not_match(
        self, stub_read_venue_type_from_file, app
    ):
        # Given
        old_venue_type = offerers_factories.VenueTypeFactory(label="old_type")
        offerers_factories.VenueTypeFactory(label="new_type", id=2)
        offerers_factories.VenueFactory(venueType=old_venue_type)

        stub_read_venue_type_from_file.return_value = [("666", "new_type")]

        # When
        update_venue_type("fake/path")

        # Then
        updated_venue = Venue.query.one()
        assert updated_venue.venueTypeId == old_venue_type.id

    @patch("pcapi.scripts.update_venue_type._read_venue_type_from_file")
    @pytest.mark.usefixtures("db_session")
    def test_should_not_update_venue_type_whith_type_from_read_file_when_type_label_does_not_match(
        self, stub_read_venue_type_from_file, app
    ):
        # Given
        old_venue_type = offerers_factories.VenueTypeFactory(label="old_type")
        offerers_factories.VenueFactory(venueType=old_venue_type)

        stub_read_venue_type_from_file.return_value = [("121", "other_type")]

        # When
        update_venue_type("fake/path")

        # Then
        updated_venue = Venue.query.one()
        assert updated_venue.venueTypeId == old_venue_type.id

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
