import datetime
import logging
from unittest.mock import patch

import pytest
import time_machine

from pcapi.core.offerers import factories as offerers_factories
from pcapi.utils import siren as siren_utils

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
        offerers_factories.ClosedOffererFactory(id=23 + 28 * 3)  # not checked because closed
        offerers_factories.RejectedOffererFactory(id=23 + 28 * 4, isActive=True)  # not checked because rejected
        offerers_factories.OffererFactory(
            id=23 + 28 * 5, siren=siren_utils.rid7_to_siren("1234567")  # not checked because RID7 not in Sirene API
        )

        with time_machine.travel("2024-12-24 23:00:00"):
            run_command(app, "check_active_offerers")

        # Only check that the task is called; its behavior is tested in offerers/test_task.py
        mock_get_siren.assert_called_once_with(offerer.siren, with_address=False, raise_if_non_public=False)


class CheckClosedOfferersTest:
    @patch(
        "pcapi.connectors.entreprise.sirene.get_siren_closed_at_date",
        return_value=["222222226", "333333334", "444444442", "666666664"],
    )
    @patch("pcapi.connectors.entreprise.sirene.get_siren")
    def test_check_closed_offerers(self, mock_get_siren, mock_get_siren_closed_at_date, app):
        offerers_factories.OffererFactory(siren="111111118")
        offerers_factories.OffererFactory(siren="222222226")
        offerers_factories.OffererFactory(siren="333333334", isActive=False)
        offerers_factories.RejectedOffererFactory(siren="555555556")
        offerers_factories.NotValidatedOffererFactory(siren="666666664")

        run_command(app, "check_closed_offerers")

        mock_get_siren_closed_at_date.assert_called_once_with(datetime.date.today() - datetime.timedelta(days=2))

        # Only check that the task is called; its behavior is tested in offerers/test_task.py
        mock_get_siren.assert_called()
        assert mock_get_siren.call_count == 2
        assert {item.args[0] for item in mock_get_siren.call_args_list} == {"222222226", "666666664"}
        assert mock_get_siren.call_args.kwargs == {"raise_if_non_public": False, "with_address": False}

    @patch(
        "pcapi.connectors.entreprise.sirene.get_siren_closed_at_date",
        return_value=["222222226", "333333334"],
    )
    @patch("pcapi.connectors.entreprise.sirene.get_siren")
    def test_no_known_siren(self, mock_get_siren, mock_get_siren_closed_at_date, app):
        run_command(app, "check_closed_offerers")
        mock_get_siren_closed_at_date.assert_called_once_with(datetime.date.today() - datetime.timedelta(days=2))
        mock_get_siren.assert_not_called()


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
