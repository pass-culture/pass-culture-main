import logging
from unittest.mock import patch

import pytest
import time_machine

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers.synchronize_venues_banners_with_google_places import PlaceDetails
from pcapi.core.offerers.synchronize_venues_banners_with_google_places import PlacePhoto

from tests.test_utils import run_command


pytestmark = pytest.mark.usefixtures("db_session")


class CheckActiveOfferersTest:
    @patch("pcapi.connectors.entreprise.sirene.get_siren")
    def test_check_active_offerers(self, mock_get_siren, app):
        tag = offerers_factories.OffererTagFactory(name="siren-caduc")

        offerers_factories.OffererFactory(id=23 + 27)  # not checked today
        offerer = offerers_factories.OffererFactory(id=23 + 28)
        offerers_factories.OffererFactory(id=23 + 29)  # not checked today
        offerers_factories.OffererFactory(id=23 + 28 * 2, isActive=False)  # not checked because inactive
        offerers_factories.OffererFactory(id=23 + 28 * 3, tags=[tag])  # not checked because already tagged

        with time_machine.travel("2024-12-24 23:00:00"):
            run_command(app, "check_active_offerers")

        # Only check that the task is called; its behavior is tested in offerers/test_task.py
        mock_get_siren.assert_called_once_with(offerer.siren, with_address=False, raise_if_non_public=False)


class SynchronizeVenuesBannerWithGooglePlacesTest:
    @pytest.mark.parametrize("day", [29, 30, 31])
    def test_does_not_execute_and_log_after_28th(self, day, caplog, app):
        with time_machine.travel(f"2024-12-{day:02d} 23:00:00"):
            with caplog.at_level(logging.INFO):
                run_command(app, "synchronize_venues_banners_with_google_places")

        assert (
            caplog.records[0].message
            == "[gmaps_banner_synchro] synchronize_venues_banners_with_google_places command does not execute after 28th"
        )

    @patch("pcapi.core.offerers.synchronize_venues_banners_with_google_places.get_venues_without_photo")
    @patch("pcapi.core.offerers.synchronize_venues_banners_with_google_places.get_place_id")
    @patch("pcapi.core.offerers.synchronize_venues_banners_with_google_places.get_place_photos_and_owner")
    @patch("pcapi.core.offerers.synchronize_venues_banners_with_google_places.save_photo_to_gcp")
    def test_synchronize_venues_banners_with_google_places_batching(
        self,
        mock_save_photo_to_gcp,
        mock_get_place_photos_and_owner,
        mock_get_place_id,
        mock_get_venues_without_photo,
        app,
    ):

        venues = [offerers_factories.VenueFactory() for _ in range(5)]
        mock_get_venues_without_photo.return_value = venues
        mock_get_place_photos_and_owner.return_value = PlaceDetails(
            name="test", photos=[PlacePhoto(height=100, photo_reference="test", width=100, html_attributions=[])]
        )
        mock_get_place_id.return_value = "test"
        mock_save_photo_to_gcp.return_value = "https://test.com/test.jpg"

        with patch("pcapi.models.db.session.commit") as mock_commit:
            run_command(app, "synchronize_venues_banners_with_google_places", "--batch-size", 2)

        assert mock_get_place_id.call_count == 5
        assert mock_get_place_photos_and_owner.call_count == 5
        assert mock_save_photo_to_gcp.call_count == 5
        assert mock_commit.call_count == 3
