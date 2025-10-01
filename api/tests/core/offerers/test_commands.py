import datetime
import logging
from dataclasses import asdict
from unittest.mock import patch

import pytest
import time_machine

from pcapi import settings
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils import siren as siren_utils

from tests.test_utils import run_command


pytestmark = pytest.mark.usefixtures("clean_database")


@pytest.fixture(name="siren_caduc_tag")
def siren_caduc_tag_fixture():
    return offerers_factories.OffererTagFactory(name="siren-caduc", label="SIREN caduc")


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


# TODO bulle test no siren closed
class CheckClosedOfferersTest:
    @pytest.mark.features(ENABLE_CODIR_OFFERERS_REPORT=True, ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("pcapi.core.offerers.api.close_offerer")
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value="report-file-id")
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
        mock_search_file,
        mock_append_to_spreadsheet,
        mock_close_offerer,
        client,
        siren_caduc_tag,
        app,
    ):
        # SIREN makes offerer inactive (because of 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer1 = offerers_factories.OffererFactory(siren="109599001")
        offerer2 = offerers_factories.OffererFactory(siren="109599002")
        offerer3 = offerers_factories.OffererFactory(siren="109599003")
        offerer4 = offerers_factories.OffererFactory(siren="909599004")  # non-diffusible

        run_command(app, "check_closed_offerers")

        assert offerer1.tags == offerer2.tags == offerer3.tags == offerer4.tags == [siren_caduc_tag]

        mock_search_file.call_count == 4
        mock_append_to_spreadsheet.call_count == 4
        mock_close_offerer.call_count == 4

    @pytest.mark.features(ENABLE_CODIR_OFFERERS_REPORT=False, ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("pcapi.core.offerers.api.close_offerer")
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value="report-file-id")
    @patch(
        "pcapi.connectors.api_sirene.get_siren_closed_at_date",
        return_value=[{"siren": "109599001", "closure_date": datetime.date(2025, 1, 16)}],
    )
    @time_machine.travel("2025-01-21 12:00:00")
    def test_no_report(
        self,
        mock_siren_closed_at_date,
        mock_search_file,
        mock_append_to_spreadsheet,
        mock_close_offerer,
        client,
        siren_caduc_tag,
        app,
    ):
        # SIREN makes offerer inactive (because of 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer = offerers_factories.OffererFactory(siren="109599001")
        run_command(app, "check_closed_offerers")

        assert offerer.tags == [siren_caduc_tag]

        mock_close_offerer.assert_called_once_with(
            offerer,
            closure_date=datetime.date(2025, 1, 16),
            author_user=None,
            comment="L'entité juridique est détectée comme fermée le 16/01/2025 via l'API Entreprise (données INSEE)",
            modified_info={"tags": {"new_info": "SIREN caduc"}},
        )
        mock_search_file.assert_not_called()

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=False)
    @pytest.mark.features(ENABLE_CODIR_OFFERERS_REPORT=True)
    @patch("pcapi.core.offerers.api.close_offerer")
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value="report-file-id")
    @patch(
        "pcapi.connectors.api_sirene.get_siren_closed_at_date",
        return_value=[{"siren": "109599001", "closure_date": datetime.date(2025, 1, 16)}],
    )
    @time_machine.travel("2025-01-21 12:00:00")
    def test_tag_inactive_offerer_no_delete(
        self,
        mock_siren_closed_at_date,
        mock_search_file,
        mock_append_to_spreadsheet,
        mock_close_offerer,
        client,
        siren_caduc_tag,
        app,
    ):
        # SIREN makes offerer inactive (because of 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer = offerers_factories.OffererFactory(siren="109599001")

        run_command(app, "check_closed_offerers")

        assert offerer.tags == [siren_caduc_tag]

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId is None
        assert action.offererId == offerer.id
        assert (
            action.comment
            == "L'entité juridique est détectée comme fermée le 16/01/2025 via l'API Entreprise (données INSEE)"
        )
        assert action.extraData == {"modified_info": {"tags": {"new_info": siren_caduc_tag.label}}}

        mock_search_file.assert_called_once()
        mock_append_to_spreadsheet.assert_called_once_with(
            "report-file-id",
            [
                [
                    datetime.date.today().strftime("%d/%m/%Y"),
                    offerer.siren,
                    "MINISTERE DE LA CULTURE",
                    "Non",
                    "REFUS",
                    "REFUS",
                    "Société à responsabilité limitée (sans autre indication)",
                    0,
                    0.0,
                    f"{settings.BACKOFFICE_URL}/pro/offerer/{offerer.id}",
                ]
            ],
        )
        mock_close_offerer.assert_not_called()

    @pytest.mark.features(ENABLE_CODIR_OFFERERS_REPORT=True, ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=False)
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value="report-file-id")
    @patch("pcapi.core.offerers.api.close_offerer")
    @patch(
        "pcapi.connectors.api_sirene.get_siren_closed_at_date",
        return_value=[{"siren": "109599001", "closure_date": datetime.date(2025, 1, 16)}],
    )
    def test_inactive_offerer_already_tagged(
        self,
        mock_siren_closed_at_date,
        mock_close_offerer,
        mock_search_file,
        mock_append_to_spreadsheet,
        client,
        siren_caduc_tag,
        app,
    ):
        # SIREN makes offerer inactive (because of 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer = offerers_factories.OffererFactory(siren="109599001", tags=[siren_caduc_tag])

        run_command(app, "check_closed_offerers")

        assert offerer.tags == [siren_caduc_tag]
        assert db.session.query(history_models.ActionHistory).count() == 0  # tag already set, no change made
        mock_search_file.assert_called_once()
        mock_append_to_spreadsheet.assert_called_once()
        mock_close_offerer.assert_not_called()

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True, ENABLE_CODIR_OFFERERS_REPORT=True)
    @patch("time.sleep")
    @patch("pcapi.core.offerers.api.close_offerer")
    @patch(
        "pcapi.connectors.api_sirene.get_siren_closed_at_date",
        return_value=[{"siren": "109599001", "closure_date": datetime.date(2025, 3, 5)}],
    )
    @time_machine.travel("2025-03-10 12:00:00")
    def test_close_inactive_offerer_already_tagged(
        self, mock_siren_closed_at_date, mock_close_offerer, mock_sleep, client, siren_caduc_tag, app
    ):
        # SIREN makes offerer inactive (because of 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer = offerers_factories.OffererFactory(siren="109599001", tags=[siren_caduc_tag])
        offerers_factories.UserOffererFactory(offerer=offerer)

        run_command(app, "check_closed_offerers")
        assert offerer.tags == [siren_caduc_tag]
        mock_close_offerer.assert_called_once_with(
            offerer,
            closure_date=datetime.date(2025, 3, 5),
            author_user=None,
            comment="L'entité juridique est détectée comme fermée le 05/03/2025 via l'API Entreprise (données INSEE)",
        )

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True, ENABLE_CODIR_OFFERERS_REPORT=True)
    @patch("time.sleep")
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value="report-file-id")
    @patch(
        "pcapi.connectors.api_sirene.get_siren_closed_at_date",
        return_value=[{"siren": "100099001", "closure_date": datetime.date(2025, 1, 16)}],
    )
    def test_reject_inactive_offerer_waiting_for_validation(
        self,
        mock_siren_closed_at_date,
        mock_search_file,
        mock_append_to_spreadsheet,
        mock_sleep,
        client,
        siren_caduc_tag,
        app,
    ):
        offerer = offerers_factories.PendingOffererFactory(siren="100099001")
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(offerer=offerer)

        run_command(app, "check_closed_offerers")

        assert offerer.isRejected
        assert offerer.tags == [siren_caduc_tag]

        offerer_action = (
            db.session.query(history_models.ActionHistory)
            .filter_by(actionType=history_models.ActionType.OFFERER_REJECTED)
            .one()
        )
        assert offerer_action.actionDate is not None
        assert offerer_action.authorUserId is None
        assert offerer_action.userId == user_offerer.user.id
        assert offerer_action.offererId == offerer.id
        assert offerer_action.extraData == {
            "modified_info": {"tags": {"new_info": siren_caduc_tag.label}},
            "rejection_reason": offerers_models.OffererRejectionReason.CLOSED_BUSINESS.name,
        }

        user_offerer_action = (
            db.session.query(history_models.ActionHistory)
            .filter_by(actionType=history_models.ActionType.USER_OFFERER_REJECTED)
            .one()
        )
        assert user_offerer_action.actionDate is not None
        assert user_offerer_action.authorUserId is None
        assert user_offerer_action.userId == user_offerer.user.id
        assert user_offerer_action.offererId == offerer.id

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user_offerer.user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.NEW_OFFERER_REJECTION.value)
        assert mails_testing.outbox[0]["params"] == {
            "OFFERER_NAME": offerer.name,
            "REJECTION_REASON": offerers_models.OffererRejectionReason.CLOSED_BUSINESS.name,
        }

        # Offerers report should only list validated offerers, not rejected
        mock_search_file.assert_not_called()
        mock_append_to_spreadsheet.assert_not_called()

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
