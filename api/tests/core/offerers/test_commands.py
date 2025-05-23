import datetime
import json
import logging
from unittest.mock import patch

import pytest
import time_machine

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import tasks as offerers_tasks
from pcapi.models import db
from pcapi.utils import siren as siren_utils

from tests.test_utils import run_command


pytestmark = pytest.mark.usefixtures("clean_database")


class CheckActiveOfferersTest:
    @patch("pcapi.connectors.entreprise.sirene.get_siren")
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
        mock_get_siren.assert_called_once_with(offerer.siren, with_address=False, raise_if_non_public=False)


class CheckClosedOfferersTest:
    @patch("pcapi.core.offerers.tasks.check_offerer_siren_task")
    @patch(
        "pcapi.connectors.entreprise.sirene.get_siren_closed_at_date",
        return_value=["222222226", "333333334", "444444442", "666666664"],
    )
    def test_check_closed_offerers(self, mock_get_siren_closed_at_date, mock_check_offerer_siren_task, app):
        offerers_factories.OffererFactory(siren="111111118")
        offerers_factories.OffererFactory(siren="222222226")
        offerers_factories.OffererFactory(siren="333333334", isActive=False)
        offerers_factories.RejectedOffererFactory(siren="555555556")
        offerers_factories.NewOffererFactory(siren="666666664")
        db.session.flush()
        db.session.commit()

        run_command(app, "check_closed_offerers")

        mock_get_siren_closed_at_date.assert_called_once_with(datetime.date.today() - datetime.timedelta(days=2))

        # Only check that the task is called; its behavior is tested in offerers/test_tasks.py
        mock_check_offerer_siren_task.delay.assert_called()
        assert mock_check_offerer_siren_task.delay.call_count == 2
        assert sorted(
            [item.args[0] for item in mock_check_offerer_siren_task.delay.call_args_list], key=lambda r: r.siren
        ) == [
            offerers_tasks.CheckOffererSirenRequest(
                siren="222222226", close_or_tag_when_inactive=True, fill_in_codir_report=False
            ),
            offerers_tasks.CheckOffererSirenRequest(
                siren="666666664", close_or_tag_when_inactive=True, fill_in_codir_report=False
            ),
        ]

    @patch("pcapi.core.offerers.tasks.check_offerer_siren_task")
    @patch(
        "pcapi.connectors.entreprise.sirene.get_siren_closed_at_date",
        return_value=["222222226", "333333334"],
    )
    def test_no_known_siren(self, mock_get_siren_closed_at_date, mock_check_offerer_siren_task, app):
        run_command(app, "check_closed_offerers")
        mock_get_siren_closed_at_date.assert_called_once_with(datetime.date.today() - datetime.timedelta(days=2))
        mock_check_offerer_siren_task.assert_not_called()

    @patch("pcapi.core.offerers.tasks.check_offerer_siren_task")
    @patch("flask.current_app.redis_client.get", return_value=json.dumps(["111222337"]))
    @patch("pcapi.connectors.entreprise.sirene.get_siren_closed_at_date", return_value=[])
    def test_check_scheduled_offerers(
        self, mock_get_siren_closed_at_date, mock_redis_client_get, mock_check_offerer_siren_task, app
    ):
        offerers_factories.OffererFactory(siren="111222337")

        run_command(app, "check_closed_offerers")

        mock_get_siren_closed_at_date.assert_called_once_with(datetime.date.today() - datetime.timedelta(days=2))
        mock_redis_client_get.assert_called_once_with(
            f"check_closed_offerers:scheduled:{datetime.date.today().isoformat()}"
        )

        # Only check that the task is called; its behavior is tested in offerers/test_tasks.py
        mock_check_offerer_siren_task.delay.assert_called_once()
        assert mock_check_offerer_siren_task.delay.call_args.args == (
            offerers_tasks.CheckOffererSirenRequest(
                siren="111222337", close_or_tag_when_inactive=True, fill_in_codir_report=False
            ),
        )


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
