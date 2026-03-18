import datetime
from unittest.mock import patch

import pytest
import time_machine

from pcapi import settings
from pcapi.connectors.entreprise.models import SirenInfo
from pcapi.core.history import models as history_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import tasks as offerers_tasks
from pcapi.models import db
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_KEY
from pcapi.tasks.cloud_task import AUTHORIZATION_HEADER_VALUE
from pcapi.utils import siren as siren_utils


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="siren_caduc_tag")
def siren_caduc_tag_fixture():
    return offerers_factories.OffererTagFactory(name="siren-caduc", label="SIREN caduc")


@pytest.mark.features(WIP_ASYNCHRONOUS_CELERY_CHECK_OFFERERS=True)
class CheckOffererSirenCeleryTaskTest:
    @patch("time.sleep")
    def test_active_offerer(self, mock_sleep, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory()

        offerers_tasks.check_offerer_siren_celery_task.run(
            offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=True)
        )

        assert not offerer.tags

    @patch("pcapi.core.offerers.api.close_offerer")
    def test_still_active_offerer_closed_in_the_future(
        self,
        mock_close_offerer,
        client,
        siren_caduc_tag,
    ):
        offerer = offerers_factories.OffererFactory(siren="111222337")
        closure_date = datetime.date.today() + datetime.timedelta(days=7)

        with patch(
            "pcapi.connectors.entreprise.api.get_siren_open_data",
            return_value=SirenInfo(
                siren=offerer.siren,
                name=offerer.name,
                head_office_siret=siren_utils.complete_siren_or_siret(offerer.siren + "0001"),
                ape_code="9001Z",
                ape_label="Arts du spectacle vivant",
                legal_category_code="5710",
                address=None,
                active=True,
                diffusible=True,
                creation_date=datetime.date(2024, 1, 1),
                closure_date=closure_date,
            ),
        ):
            offerers_tasks.check_offerer_siren_celery_task.run(
                offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=True)
            )

        assert not offerer.tags
        mock_close_offerer.assert_not_called()

    @patch("time.sleep")
    def test_untag_revalidated_offerer_still_tagged(self, mock_sleep, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory(tags=[siren_caduc_tag])
        offerers_factories.UserOffererFactory(offerer=offerer)

        offerers_tasks.check_offerer_siren_celery_task.run(
            offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=True)
        )

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId is None
        assert action.offererId == offerer.id
        assert action.comment == "L'entité juridique est détectée comme active via l'API Entreprise (données INSEE)"
        assert action.extraData == {"modified_info": {"tags": {"old_info": siren_caduc_tag.label}}}

    @patch("time.sleep")
    def test_active_offerer_waiting_for_validation(self, mock_sleep, client, siren_caduc_tag):
        offerer = offerers_factories.PendingOffererFactory()

        offerers_tasks.check_offerer_siren_celery_task.run(
            offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=True)
        )

        assert offerer.isWaitingForValidation
        assert not offerer.tags

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("pcapi.core.offerers.api.handle_closed_offerer")
    @time_machine.travel("2025-01-21 12:00:00")
    def test_inactive_offerer_is_handled(self, mock_handle_closed_offerer, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory(siren="109599001")
        closure_date = datetime.date(2025, 1, 16)

        with patch(
            "pcapi.connectors.entreprise.api.get_siren_open_data",
            return_value=SirenInfo(
                siren=offerer.siren,
                name=offerer.name,
                head_office_siret=siren_utils.complete_siren_or_siret(offerer.siren + "0001"),
                ape_code="9001Z",
                ape_label="Arts du spectacle vivant",
                legal_category_code="5710",
                address=None,
                active=False,
                diffusible=True,
                creation_date=datetime.date(2024, 1, 1),
                closure_date=closure_date,
            ),
        ):
            offerers_tasks.check_offerer_siren_celery_task.run(
                offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=True)
            )

        mock_handle_closed_offerer.assert_called_once_with(
            offerer,
            closure_date=datetime.date(2025, 1, 16),
        )

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("pcapi.core.offerers.api.handle_closed_offerer")
    def test_inactive_offerer_not_closed_when_flag_is_false(self, mock_handle_closed_offerer, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory(siren="109599001")
        closure_date = datetime.date(2025, 1, 16)

        with patch(
            "pcapi.connectors.entreprise.api.get_siren_open_data",
            return_value=SirenInfo(
                siren=offerer.siren,
                name=offerer.name,
                head_office_siret=siren_utils.complete_siren_or_siret(offerer.siren + "0001"),
                ape_code="9001Z",
                ape_label="Arts du spectacle vivant",
                legal_category_code="5710",
                address=None,
                active=False,
                diffusible=True,
                creation_date=datetime.date(2024, 1, 1),
                closure_date=closure_date,
            ),
        ):
            offerers_tasks.check_offerer_siren_celery_task.run(
                offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=False)
            )

        assert not offerer.tags
        mock_handle_closed_offerer.assert_not_called()

    @patch("time.sleep")
    def test_siren_not_found(self, mock_sleep, client, siren_caduc_tag):
        # Using TestingBackend: SIREN filled with zeros throws UnknownEntityException
        offerer = offerers_factories.OffererFactory(siren="000000000")

        offerers_tasks.check_offerer_siren_celery_task.run(
            offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=True)
        )

        assert not offerer.tags

    def test_invalid_siren_format(self, client, caplog):
        # Using TestingBackend: SIREN filled with zeros throws UnknownEntityException
        offerer = offerers_factories.OffererFactory(siren="123456789")

        offerers_tasks.check_offerer_siren_celery_task.run(
            offerers_tasks.CheckOffererSirenRequest(siren=offerer.siren, close_or_tag_when_inactive=False)
        )

        assert caplog.records[0].message == "Invalid SIREN format in the database"


@pytest.mark.features(WIP_ASYNCHRONOUS_CELERY_CHECK_OFFERERS=False)
class CheckOffererSirenCloudTaskTest:
    @patch("time.sleep")
    def test_active_offerer(self, mock_sleep, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory()

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "must_fill_in_codir_report": False},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags

    @patch("pcapi.core.offerers.api.close_offerer")
    def test_still_active_offerer_closed_in_the_future(
        self,
        mock_close_offerer,
        client,
        siren_caduc_tag,
    ):
        offerer = offerers_factories.OffererFactory(siren="111222337")
        closure_date = datetime.date.today() + datetime.timedelta(days=7)

        with patch(
            "pcapi.connectors.entreprise.api.get_siren_open_data",
            return_value=SirenInfo(
                siren=offerer.siren,
                name=offerer.name,
                head_office_siret=siren_utils.complete_siren_or_siret(offerer.siren + "0001"),
                ape_code="9001Z",
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
        mock_close_offerer.assert_not_called()

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
        assert action.comment == "L'entité juridique est détectée comme active via l'API Entreprise (données INSEE)"
        assert action.extraData == {"modified_info": {"tags": {"old_info": siren_caduc_tag.label}}}

    @patch("time.sleep")
    def test_active_offerer_waiting_for_validation(self, mock_sleep, client, siren_caduc_tag):
        offerer = offerers_factories.PendingOffererFactory()

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": True},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert offerer.isWaitingForValidation
        assert not offerer.tags

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("pcapi.core.offerers.api.handle_closed_offerer")
    @time_machine.travel("2025-01-21 12:00:00")
    def test_inactive_offerer_is_handled(self, mock_handle_closed_offerer, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory(siren="109599001")
        closure_date = datetime.date(2025, 1, 16)

        with patch(
            "pcapi.connectors.entreprise.api.get_siren_open_data",
            return_value=SirenInfo(
                siren=offerer.siren,
                name=offerer.name,
                head_office_siret=siren_utils.complete_siren_or_siret(offerer.siren + "0001"),
                ape_code="9001Z",
                ape_label="Arts du spectacle vivant",
                legal_category_code="5710",
                address=None,
                active=False,
                diffusible=True,
                creation_date=datetime.date(2024, 1, 1),
                closure_date=closure_date,
            ),
        ):
            response = client.post(
                f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
                json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "must_fill_in_codir_report": False},
                headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
            )

        assert response.status_code == 204
        mock_handle_closed_offerer.assert_called_once_with(
            offerer,
            closure_date=datetime.date(2025, 1, 16),
        )

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("pcapi.core.offerers.api.handle_closed_offerer")
    def test_inactive_offerer_not_closed_when_flag_is_false(self, mock_handle_closed_offerer, client, siren_caduc_tag):
        offerer = offerers_factories.OffererFactory(siren="109599001")
        closure_date = datetime.date(2025, 1, 16)

        with patch(
            "pcapi.connectors.entreprise.api.get_siren_open_data",
            return_value=SirenInfo(
                siren=offerer.siren,
                name=offerer.name,
                head_office_siret=siren_utils.complete_siren_or_siret(offerer.siren + "0001"),
                ape_code="9001Z",
                ape_label="Arts du spectacle vivant",
                legal_category_code="5710",
                address=None,
                active=False,
                diffusible=True,
                creation_date=datetime.date(2024, 1, 1),
                closure_date=closure_date,
            ),
        ):
            response = client.post(
                f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
                json={"siren": offerer.siren, "close_or_tag_when_inactive": False, "must_fill_in_codir_report": False},
                headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
            )

        assert response.status_code == 204
        assert not offerer.tags
        mock_handle_closed_offerer.assert_not_called()

    @patch("time.sleep")
    def test_siren_not_found(self, mock_sleep, client, siren_caduc_tag):
        # Using TestingBackend: SIREN filled with zeros throws UnknownEntityException
        offerer = offerers_factories.OffererFactory(siren="000000000")

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": True, "fill_in_codir_report": False},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert not offerer.tags

    def test_invalid_siren_format(self, client, caplog):
        # Using TestingBackend: SIREN filled with zeros throws UnknownEntityException
        offerer = offerers_factories.OffererFactory(siren="123456789")

        response = client.post(
            f"{settings.API_URL}/cloud-tasks/offerers/check_offerer",
            json={"siren": offerer.siren, "close_or_tag_when_inactive": False, "fill_in_codir_report": False},
            headers={AUTHORIZATION_HEADER_KEY: AUTHORIZATION_HEADER_VALUE},
        )

        assert response.status_code == 204
        assert caplog.records[0].message == "Invalid SIREN format in the database"
