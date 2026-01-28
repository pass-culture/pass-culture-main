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
    @patch("pcapi.connectors.entreprise.api.get_siren_open_data")
    def test_check_active_offerers(self, mock_get_siren, app):
        offerers_factories.OffererTagFactory(name="siren-caduc")

        offerers_factories.OffererFactory(id=23 + 27)  # not checked today
        offerer = offerers_factories.OffererFactory(id=23 + 28)
        offerers_factories.OffererFactory(id=23 + 29)  # not checked today
        offerers_factories.OffererFactory(id=23 + 28 * 2, isActive=False)  # not checked because inactive
        offerers_factories.ClosedOffererFactory(id=23 + 28 * 3)  # not checked because closed
        offerers_factories.RejectedOffererFactory(id=23 + 28 * 4, isActive=True)  # not checked because rejected
        offerers_factories.OffererFactory(
            id=23 + 28 * 5,
            siren=siren_utils.rid7_to_siren("1234567"),  # not checked because RID7 not in Sirene API
        )

        with time_machine.travel("2024-12-24 23:00:00"):
            run_command(app, "check_active_offerers")

        # Only check that the task is called; its behavior is tested in offerers/test_task.py
        mock_get_siren.assert_called_once_with(offerer.siren, with_address=False)


class CheckClosedOfferersTest:
    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("pcapi.core.offerers.api.close_offerer")
    @patch(
        "pcapi.connectors.api_sirene.get_siren_closed_at_date",
        return_value=[
            {"siren": "109599001", "closure_date": datetime.date(2025, 1, 16)},
            {"siren": "109599002", "closure_date": datetime.date(2025, 1, 11)},
            {"siren": "109599003", "closure_date": datetime.date(2023, 1, 16)},
            {"siren": "909599004", "closure_date": datetime.date(2025, 1, 12)},  # non-diffusible
        ],
    )
    @time_machine.travel("2025-01-21 12:00:00")
    def test_multiple_inactive_offerers(
        self,
        mock_siren_closed_at_date,
        mock_close_offerer,
        client,
        app,
    ):
        siren_caduc_tag = offerers_factories.OffererTagFactory(name="siren-caduc", label="SIREN caduc")
        # SIREN makes offerer inactive (because of 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer1 = offerers_factories.OffererFactory(siren="109599001")
        offerer2 = offerers_factories.OffererFactory(siren="109599002")
        offerer3 = offerers_factories.OffererFactory(siren="109599003")
        offerer4 = offerers_factories.OffererFactory(siren="909599004")  # non-diffusible

        run_command(app, "check_closed_offerers")

        assert offerer1.tags == offerer2.tags == offerer3.tags == offerer4.tags == [siren_caduc_tag]

        mock_close_offerer.call_count == 4

    @patch("pcapi.core.offerers.tasks.check_offerer_siren_task")
    @patch(
        "pcapi.connectors.api_sirene.get_siren_closed_at_date",
        return_value=[
            {"siren": "222222226", "closure_date": datetime.date(2025, 1, 16)},
            {"siren": "333333334", "closure_date": datetime.date(2025, 1, 16)},
        ],
    )
    def test_no_known_siren(self, mock_get_siren_closed_at_date, mock_check_offerer_siren_task, app):
        offerer = offerers_factories.OffererFactory(siren="111111112")
        run_command(app, "check_closed_offerers")
        mock_get_siren_closed_at_date.assert_called_once_with(datetime.date.today() - datetime.timedelta(days=2))
        assert offerer.tags == []


class DeleteUserOfferersOnClosedOfferersTest:
    @patch("pcapi.core.offerers.api.auto_delete_attachments_on_closed_offerers")
    def test_delete_user_offerers_on_closed_offerers(self, mock_auto_delete_attachments_on_closed_offerers, app):
        run_command(app, "delete_user_offerers_on_closed_offerers")

        mock_auto_delete_attachments_on_closed_offerers.assert_called_once()


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
