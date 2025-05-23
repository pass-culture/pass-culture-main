import datetime
import json
from dataclasses import asdict
from unittest.mock import patch

import pytest
import time_machine

from pcapi import settings
from pcapi.connectors.entreprise.models import SirenInfo
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_KEY
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_VALUE
from pcapi.utils import siren as siren_utils


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="siren_caduc_tag")
def siren_caduc_tag_fixture():
    return offerers_factories.OffererTagFactory(name="siren-caduc", label="SIREN caduc")


class CheckOffererTest:
    @patch("time.sleep")
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet")
    def test_active_offerer(self, mock_append_to_spreadsheet, mock_sleep, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory()

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": False},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags

        mock_append_to_spreadsheet.assert_not_called()

    @pytest.mark.parametrize(
        "already_in_redis,expected_set_in_redis",
        [
            (None, json.dumps(["111222337"])),
            (json.dumps(["999999999"]), json.dumps(["999999999", "111222337"])),
        ],
    )
    @patch("time.sleep")
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet")
    @patch("flask.current_app.redis_client.set")
    @patch("flask.current_app.redis_client.get")
    def test_still_active_offerer_closed_in_the_future(
        self,
        mock_redis_client_get,
        mock_redis_client_set,
        mock_append_to_spreadsheet,
        mock_sleep,
        client,
        siren_caduc_tag,
        already_in_redis,
        expected_set_in_redis,
    ):
        offerer = offerers_factories.OffererFactory(siren="111222337")
        closure_date = datetime.date.today() + datetime.timedelta(days=7)
        mock_redis_client_get.return_value = already_in_redis

        with patch(
            "pcapi.connectors.entreprise.sirene.get_siren",
            return_value=SirenInfo(
                siren=offerer.siren,
                name=offerer.name,
                head_office_siret=siren_utils.complete_siren_or_siret(offerer.siren + "0001"),
                ape_code="90.01Z",
                ape_label="Arts du spectacle vivant",
                legal_category_code="5710",
                address=None,
                active=True,
                diffusible=True,
                creation_date=datetime.date(2024, 1, 1),
                closure_date=closure_date,
            ),
        ):
            response = client.post(
                f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
                json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": False},
                headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
            )

        assert response.status_code == 204
        assert not offerer.tags

        mock_redis_client_get.assert_called_once_with(
            f"check_closed_offerers:scheduled:{closure_date.isoformat()}",
        )
        mock_redis_client_set.assert_called_once_with(
            f"check_closed_offerers:scheduled:{closure_date.isoformat()}",
            expected_set_in_redis,
            ex=86400 * (7 + 30),
        )
        mock_append_to_spreadsheet.assert_not_called()

    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.create_spreadsheet", return_value="new-file-id")
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value="report-file-id")
    def test_active_offerer_with_report(
        self, mock_search_file, mock_create_spreadsheet, mock_append_to_spreadsheet, client, siren_caduc_tag
    ):
        offerer = offerers_factories.OffererFactory(siren="900150004")  # See TestingBackend for SIREN digits

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags

        mock_search_file.assert_called_once()
        mock_create_spreadsheet.assert_not_called()
        mock_append_to_spreadsheet.assert_called_once_with(
            "report-file-id",
            [
                [
                    datetime.date.today().strftime("%d/%m/%Y"),
                    offerer.siren,
                    "[ND]",
                    "Oui",
                    "OK",
                    "N/A : Hors périmètre",
                    "Entrepreneur individuel",
                    0,
                    0.0,
                    f"{settings.BACKOFFICE_URL}/pro/offerer/{offerer.id}",
                ]
            ],
        )

    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.create_spreadsheet", return_value="new-file-id")
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value=None)
    def test_active_offerer_with_first_report(
        self, mock_search_file, mock_create_spreadsheet, mock_append_to_spreadsheet, client, siren_caduc_tag
    ):
        offerer = offerers_factories.OffererFactory(siren="010500007")  # See TestingBackend for SIREN digits

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags

        mock_search_file.assert_called_once()
        mock_create_spreadsheet.assert_called_once()
        mock_append_to_spreadsheet.assert_called_once_with(
            "new-file-id",
            [
                [
                    "Date de vérification",
                    "SIREN",
                    "Nom",
                    "En activité",
                    "Attestation Urssaf",
                    "Attestation IS",
                    "Forme juridique",
                    "Offres réservables",
                    f"CA {datetime.date.today().year}",
                    "Lien Backoffice",
                ],
                [
                    datetime.date.today().strftime("%d/%m/%Y"),
                    offerer.siren,
                    "MINISTERE DE LA CULTURE",
                    "Oui",
                    "OK",
                    "N/A : Entreprise créée dans l'année en cours",
                    "Société à responsabilité limitée (sans autre indication)",
                    0,
                    0.0,
                    f"{settings.BACKOFFICE_URL}/pro/offerer/{offerer.id}",
                ],
            ],
        )

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=False)
    @patch("pcapi.core.offerers.api.close_offerer")
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value="report-file-id")
    @time_machine.travel("2025-01-21 12:00:00")
    def test_tag_inactive_offerer(
        self, mock_search_file, mock_append_to_spreadsheet, mock_close_offerer, client, siren_caduc_tag
    ):
        # Using TestingBackend:
        # SIREN makes offerer inactive (because of 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer = offerers_factories.OffererFactory(siren="109599001")

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert offerer.tags == [siren_caduc_tag]

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId is None
        assert action.offererId == offerer.id
        assert action.comment == "L'entité juridique est détectée comme fermée le 16/01/2025 via l'API Sirene (INSEE)"
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

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("time.sleep")
    @patch("pcapi.core.offerers.api.close_offerer")
    @time_machine.travel("2025-01-21 12:00:00")
    def test_close_inactive_offerer(self, mock_close_offerer, mock_sleep, client, siren_caduc_tag):
        # Using TestingBackend:
        # SIREN makes offerer inactive (because of 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer = offerers_factories.OffererFactory(siren="109599001")

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": False},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        mock_close_offerer.assert_called_once_with(
            offerer,
            closure_date=datetime.date(2025, 1, 16),
            author_user=None,
            comment="L'entité juridique est détectée comme fermée le 16/01/2025 via l'API Sirene (INSEE)",
            modified_info={"tags": {"new_info": "SIREN caduc"}},
        )

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=False)
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value="report-file-id")
    @patch("pcapi.core.offerers.api.close_offerer")
    def test_inactive_offerer_already_tagged(
        self, mock_close_offerer, mock_search_file, mock_append_to_spreadsheet, client, siren_caduc_tag
    ):
        # Using TestingBackend:
        # SIREN makes offerer inactive (because of 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer = offerers_factories.OffererFactory(siren="109599001", tags=[siren_caduc_tag])

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert offerer.tags == [siren_caduc_tag]
        assert db.session.query(history_models.ActionHistory).count() == 0  # tag already set, no change made

        mock_search_file.assert_called_once()
        mock_append_to_spreadsheet.assert_called_once()
        mock_close_offerer.assert_not_called()

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("time.sleep")
    @patch("pcapi.core.offerers.api.close_offerer")
    @time_machine.travel("2025-03-10 12:00:00")
    def test_close_inactive_offerer_already_tagged(self, mock_close_offerer, mock_sleep, client, siren_caduc_tag):
        # Using TestingBackend:
        # SIREN makes offerer inactive (because of 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer = offerers_factories.OffererFactory(siren="109599001", tags=[siren_caduc_tag])
        offerers_factories.UserOffererFactory(offerer=offerer)

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        mock_close_offerer.assert_called_once_with(
            offerer,
            closure_date=datetime.date(2025, 3, 5),
            author_user=None,
            comment="L'entité juridique est détectée comme fermée le 05/03/2025 via l'API Sirene (INSEE)",
        )

    @patch("time.sleep")
    def test_untag_revalidated_offerer_still_tagged(self, mock_sleep, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory(tags=[siren_caduc_tag])
        offerers_factories.UserOffererFactory(offerer=offerer)

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId is None
        assert action.offererId == offerer.id
        assert action.comment == "L'entité juridique est détectée comme active via l'API Sirene (INSEE)"
        assert action.extraData == {"modified_info": {"tags": {"old_info": siren_caduc_tag.label}}}

    @patch("time.sleep")
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value="report-file-id")
    def test_reject_inactive_offerer_waiting_for_validation(
        self, mock_search_file, mock_append_to_spreadsheet, mock_sleep, client, siren_caduc_tag
    ):
        # Using TestingBackend: SIREN makes offerer inactive (because of 99), EI
        offerer = offerers_factories.PendingOffererFactory(siren="100099001")
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(offerer=offerer)

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
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

    @patch("time.sleep")
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value="report-file-id")
    def test_active_offerer_waiting_for_validation(
        self, mock_search_file, mock_append_to_spreadsheet, mock_sleep, client, siren_caduc_tag
    ):
        offerer = offerers_factories.PendingOffererFactory()

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert offerer.isWaitingForValidation
        assert not offerer.tags

        # Offerers report should only list validated offerers, not waiting for validation
        mock_search_file.assert_not_called()
        mock_append_to_spreadsheet.assert_not_called()

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("time.sleep")
    @patch("pcapi.core.offerers.api.close_offerer")
    def test_do_not_close_or_tag_inactive_offerer(self, mock_close_offerer, mock_sleep, client, siren_caduc_tag):
        # Using TestingBackend: SIREN makes offerer inactive (because of 99), EI
        offerer = offerers_factories.OffererFactory(siren="100099001")

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": False, "fill_in_codir_report": False},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags
        mock_close_offerer.assert_not_called()

    @patch("time.sleep")
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet")
    def test_siren_not_found(self, mock_sleep, mock_append_to_spreadsheet, client, siren_caduc_tag):
        # Using TestingBackend: SIREN filled with zeros throws UnknownEntityException
        offerer = offerers_factories.OffererFactory(siren="000000000")

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": False},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags

        mock_append_to_spreadsheet.assert_not_called()

    def test_invalid_siren_format(self, client, caplog):
        # Using TestingBackend: SIREN filled with zeros throws UnknownEntityException
        offerer = offerers_factories.OffererFactory(siren="123456789")

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": False},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert caplog.records[0].message == "Invalid SIREN format in the database"
