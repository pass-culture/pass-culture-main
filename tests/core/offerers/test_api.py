from unittest.mock import patch

import pytest

from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers.models import ApiKey
import pcapi.core.offers.factories as offers_factories
from pcapi.models import api_errors
from pcapi.utils.token import random_token


class EditVenueTest:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.redis.add_venue_id")
    def when_changes_on_name_algolia_indexing_is_triggered(self, mocked_add_venue_id, app) -> None:
        # Given
        venue = offers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
        )

        # When
        json_data = {"name": "my new name"}
        offerers_api.update_venue(venue, **json_data)

        # Then
        assert mocked_add_venue_id.called_once()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.redis.add_venue_id")
    def when_changes_on_public_name_algolia_indexing_is_triggered(self, mocked_add_venue_id, app) -> None:
        # Given
        venue = offers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
        )

        # When
        json_data = {"publicName": "my new name"}
        offerers_api.update_venue(venue, **json_data)

        # Then
        assert mocked_add_venue_id.called_once()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.redis.add_venue_id")
    def when_changes_on_city_algolia_indexing_is_triggered(self, mocked_add_venue_id, app) -> None:
        # Given
        venue = offers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
        )

        # When
        json_data = {"city": "My new city"}
        offerers_api.update_venue(venue, **json_data)

        # Then
        assert mocked_add_venue_id.called_once()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.redis.add_venue_id")
    def when_changes_are_not_on_algolia_fields_it_should_not_trigger_indexing(self, mocked_add_venue_id, app) -> None:
        # Given
        venue = offers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
            bookingEmail="old@email.com",
        )

        # When
        json_data = {"bookingEmail": "new@email.com"}
        offerers_api.update_venue(venue, **json_data)

        # Then
        assert mocked_add_venue_id.not_called()

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.redis.add_venue_id")
    def when_changes_in_payload_are_same_as_previous_it_should_not_trigger_indexing(
        self, mocked_add_venue_id, app
    ) -> None:
        # Given
        venue = offers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
        )

        # When
        json_data = {"city": "old City"}
        offerers_api.update_venue(venue, **json_data)

        # Then
        assert mocked_add_venue_id.not_called()

    @pytest.mark.usefixtures("db_session")
    def test_empty_siret_is_editable(self, app) -> None:
        # Given
        venue = offers_factories.VenueFactory(
            comment="Pas de siret",
            siret=None,
        )

        venue_data = {
            "siret": venue.managingOfferer.siren + "11111",
        }

        # when
        updated_venue = offerers_api.update_venue(venue, **venue_data)

        # Then
        assert updated_venue.siret == venue_data["siret"]

    @pytest.mark.usefixtures("db_session")
    def test_existing_siret_is_not_editable(self, app) -> None:
        # Given
        venue = offers_factories.VenueFactory()

        # when
        venue_data = {
            "siret": venue.managingOfferer.siren + "54321",
        }
        with pytest.raises(api_errors.ApiErrors) as error:
            offerers_api.update_venue(venue, **venue_data)

        # Then
        assert error.value.errors["siret"] == ["Vous ne pouvez pas modifier le siret d'un lieu"]

    @pytest.mark.usefixtures("db_session")
    def test_latitude_and_longitude_wrong_format(self, app) -> None:
        # given
        venue = offers_factories.VenueFactory(
            isVirtual=False,
        )

        # when
        venue_data = {
            "latitude": -98.82387,
            "longitude": "112°3534",
        }
        with pytest.raises(api_errors.ApiErrors) as error:
            offerers_api.update_venue(venue, **venue_data)

        # Then
        assert error.value.errors["latitude"] == ["La latitude doit être comprise entre -90.0 et +90.0"]
        assert error.value.errors["longitude"] == ["Format incorrect"]

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.delete_venue_from_iris_venues")
    @patch("pcapi.core.offerers.api.link_valid_venue_to_irises")
    def test_edit_physical_venue_iris_process(
        self, mock_link_venue_to_iris_if_valid, mock_delete_venue_from_iris_venues, app
    ) -> None:
        # Given
        venue = offers_factories.VenueFactory(
            isVirtual=False,
        )

        # when
        venue_coordinates = {"latitude": 2, "longitude": 48}
        updated_venue = offerers_api.update_venue(venue, **venue_coordinates)

        # Then
        mock_delete_venue_from_iris_venues.assert_called_once_with(updated_venue.id)
        mock_link_venue_to_iris_if_valid.assert_called_once_with(updated_venue)

    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.core.offerers.api.delete_venue_from_iris_venues")
    def test_edit_virtual_venue_iris_process(self, mock_delete_venue_from_iris_venues, app) -> None:
        # Given
        venue = offers_factories.VenueFactory(
            siret=None,
            isVirtual=True,
        )

        # when
        venue_coordinates = {"latitude": 2, "longitude": 48}
        offerers_api.update_venue(venue, **venue_coordinates)

        # Then
        mock_delete_venue_from_iris_venues.assert_not_called()


@pytest.mark.usefixtures("db_session")
class ApiKeyTest:
    def test_generate_and_save_api_key(self):
        offerer = offers_factories.OffererFactory()

        generated_key = offerers_api.generate_and_save_api_key(offerer.id)

        found_api_key = offerers_api.find_api_key(generated_key)

        assert found_api_key.offerer == offerer

    def test_legacy_api_key(self):
        offerer = offers_factories.OffererFactory()
        value = random_token(64)
        ApiKey(value=value, offerer=offerer)

        found_api_key = offerers_api.find_api_key(value)

        assert found_api_key.offerer == offerer

    def test_no_key_found(self):
        assert not offerers_api.find_api_key("legacy-key")
        assert not offerers_api.find_api_key("development_prefix_value")
