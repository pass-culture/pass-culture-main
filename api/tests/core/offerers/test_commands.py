import logging
from unittest.mock import patch

import pytest
import time_machine

from pcapi.core.offerers import factories as offerers_factories

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
