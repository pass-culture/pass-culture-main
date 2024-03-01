from dataclasses import asdict
import datetime
from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import override_features
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_KEY
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_VALUE


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="siren_caduc_tag")
def siren_caduc_tag_fixture():
    return offerers_factories.OffererTagFactory(name="siren-caduc", label="SIREN caduc")


class CheckOffererIsActiveTest:
    @override_features(ENABLE_CODIR_OFFERERS_REPORT=False)
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet")
    def test_active_offerer(self, mock_append_to_spreadsheet, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory()

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags

        mock_append_to_spreadsheet.assert_not_called()

    @override_features(ENABLE_CODIR_OFFERERS_REPORT=True)
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.create_spreadsheet", return_value="new-file-id")
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value="report-file-id")
    def test_active_offerer_with_report(
        self, mock_search_file, mock_create_spreadsheet, mock_append_to_spreadsheet, client, siren_caduc_tag
    ):
        offerer = offerers_factories.OffererFactory()

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": True},
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
                    "MINISTERE DE LA CULTURE",
                    "Oui",
                    "OK",
                    "N/A",
                    "Entrepreneur individuel",
                    0,
                    0.0,
                    f"{settings.BACKOFFICE_URL}/pro/offerer/{offerer.id}",
                ]
            ],
        )

    @override_features(ENABLE_CODIR_OFFERERS_REPORT=True)
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.create_spreadsheet", return_value="new-file-id")
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value=None)
    def test_active_offerer_with_first_report(
        self, mock_search_file, mock_create_spreadsheet, mock_append_to_spreadsheet, client, siren_caduc_tag
    ):
        offerer = offerers_factories.OffererFactory()

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": True},
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
                    "CA 2024",
                    "Lien Backoffice",
                ],
                [
                    datetime.date.today().strftime("%d/%m/%Y"),
                    offerer.siren,
                    "MINISTERE DE LA CULTURE",
                    "Oui",
                    "OK",
                    "N/A",
                    "Entrepreneur individuel",
                    0,
                    0.0,
                    f"{settings.BACKOFFICE_URL}/pro/offerer/{offerer.id}",
                ],
            ],
        )

    @override_features(ENABLE_CODIR_OFFERERS_REPORT=True)
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet", return_value=1)
    @patch("pcapi.connectors.googledrive.TestingBackend.search_file", return_value="report-file-id")
    def test_tag_inactive_offerer(self, mock_search_file, mock_append_to_spreadsheet, client, siren_caduc_tag):
        # Using TestingBackend:
        # SIREN makes offerer inactive (ends with 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer = offerers_factories.OffererFactory(siren="109500099")

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert offerer.tags == [siren_caduc_tag]

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId is None
        assert action.offererId == offerer.id
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

    @override_features(ENABLE_CODIR_OFFERERS_REPORT=False)
    def test_reject_inactive_offerer_waiting_for_validation(self, client, siren_caduc_tag):
        # Using TestingBackend: SIREN makes offerer inactive (ends with 99), EI
        offerer = offerers_factories.PendingOffererFactory(siren="100000099")
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(offerer=offerer)

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert offerer.isRejected
        assert offerer.tags == [siren_caduc_tag]

        offerer_action = history_models.ActionHistory.query.filter_by(
            actionType=history_models.ActionType.OFFERER_REJECTED
        ).one()
        assert offerer_action.actionDate is not None
        assert offerer_action.authorUserId is None
        assert offerer_action.userId == user_offerer.user.id
        assert offerer_action.offererId == offerer.id
        assert offerer_action.extraData == {"modified_info": {"tags": {"new_info": siren_caduc_tag.label}}}

        user_offerer_action = history_models.ActionHistory.query.filter_by(
            actionType=history_models.ActionType.USER_OFFERER_REJECTED
        ).one()
        assert user_offerer_action.actionDate is not None
        assert user_offerer_action.authorUserId is None
        assert user_offerer_action.userId == user_offerer.user.id
        assert user_offerer_action.offererId == offerer.id

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user_offerer.user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.NEW_OFFERER_REJECTION.value)

    @override_features(ENABLE_CODIR_OFFERERS_REPORT=False)
    def test_do_not_tag_inactive_offerer(self, client, siren_caduc_tag):
        # Using TestingBackend: SIREN makes offerer inactive (ends with 99), EI
        offerer = offerers_factories.OffererFactory(siren="100000099")

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": False},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags

    @override_features(ENABLE_CODIR_OFFERERS_REPORT=True)
    @patch("pcapi.connectors.googledrive.TestingBackend.append_to_spreadsheet")
    def test_siren_not_found(self, mock_append_to_spreadsheet, client, siren_caduc_tag):
        # Using TestingBackend: SIREN filled with zeros throws UnknownEntityException
        offerer = offerers_factories.OffererFactory(siren="000000000")

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags

        mock_append_to_spreadsheet.assert_not_called()
