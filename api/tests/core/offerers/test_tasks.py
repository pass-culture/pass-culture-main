from dataclasses import asdict
from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.connectors.entreprise import exceptions as sirene_exceptions
from pcapi.connectors.entreprise import models as sirene_models
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_KEY
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_VALUE


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="siren_caduc_tag")
def siren_caduc_tag_fixture():
    return offerers_factories.OffererTagFactory(name="siren-caduc", label="SIREN caduc")


class CheckOffererIsActiveTest:
    def test_active_offerer(self, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory()

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags

    @patch("pcapi.connectors.entreprise.sirene.get_siren")
    def test_tag_inactive_offerer(self, mock_get_siren, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory()

        mock_get_siren.return_value = sirene_models.SirenInfo(
            siren=offerer.siren,
            name=offerer.name,
            head_office_siret=offerer.siren + "00001",
            ape_code="6201Z",
            legal_category_code="1000",
            address=None,
            active=False,
            diffusible=True,
        )

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

    @patch("pcapi.connectors.entreprise.sirene.get_siren")
    def test_reject_inactive_offerer_waiting_for_validation(self, mock_get_siren, client, siren_caduc_tag):
        offerer = offerers_factories.PendingOffererFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(offerer=offerer)

        mock_get_siren.return_value = sirene_models.SirenInfo(
            siren=offerer.siren,
            name=offerer.name,
            head_office_siret=offerer.siren + "00001",
            ape_code="6201Z",
            legal_category_code="1000",
            address=None,
            active=False,
            diffusible=True,
        )

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

    @patch("pcapi.connectors.entreprise.sirene.get_siren")
    def test_do_not_tag_inactive_offerer(self, mock_get_siren, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory()

        mock_get_siren.return_value = sirene_models.SirenInfo(
            siren=offerer.siren,
            name=offerer.name,
            head_office_siret=offerer.siren + "00001",
            ape_code="6201Z",
            legal_category_code="1000",
            address=None,
            active=False,
            diffusible=True,
        )

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": False},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags

    @patch("pcapi.connectors.entreprise.sirene.get_siren", side_effect=sirene_exceptions.UnknownEntityException())
    def test_siren_not_found(self, mock_get_siren, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory()

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer_is_active",
            json={"siren": offerer.siren, "tag_when_inactive": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags
