from unittest.mock import patch

import freezegun
import pytest

from pcapi import settings
from pcapi.connectors.api_demarches_simplifiees import DMSGraphQLClient
from pcapi.connectors.api_demarches_simplifiees import GraphQLApplicationStates
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import factories as users_factories
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus

from tests.scripts.beneficiary.fixture import make_single_application


@pytest.mark.usefixtures("db_session")
class DmsWebhookApplicationTest:
    def test_dms_request_no_token(self, client):
        response = client.post("/webhooks/dms/application_status")
        assert response.status_code == 403

    def test_dms_request_no_params_with_token(self, client):
        response = client.post(f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}")

        assert response.status_code == 400

    @patch.object(DMSGraphQLClient, "execute_query")
    def test_dms_request(self, execute_query, client):
        execute_query.return_value = make_single_application(12, state="closed")
        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": "en_construction",
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1

    @patch.object(DMSGraphQLClient, "execute_query")
    @pytest.mark.parametrize(
        "dms_status,import_status",
        [
            (GraphQLApplicationStates.draft, ImportStatus.DRAFT),
            (GraphQLApplicationStates.on_going, ImportStatus.ONGOING),
            (GraphQLApplicationStates.refused, ImportStatus.REJECTED),
        ],
    )
    def test_dms_request_with_existing_user(self, execute_query, dms_status, import_status, client):
        user = users_factories.UserFactory(hasCompletedIdCheck=False)
        execute_query.return_value = make_single_application(12, state="closed", email=user.email)
        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": dms_status.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1

        beneficiary_import = BeneficiaryImport.query.one()
        assert beneficiary_import.source == BeneficiaryImportSources.demarches_simplifiees.value
        assert beneficiary_import.beneficiary == user
        assert len(beneficiary_import.statuses) == 1

        status = beneficiary_import.statuses[0]
        assert status.detail == "Webhook status update"
        assert status.status == import_status
        assert status.author == None

        assert user.hasCompletedIdCheck

    @freezegun.freeze_time("2021-10-30 09:00:00")
    @patch.object(DMSGraphQLClient, "execute_query")
    def test_dms_request_draft_application(self, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(12, state="closed", email=user.email)

        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.draft.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert len(user.subscriptionMessages) == 1
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.FILE
        assert (
            user.subscriptionMessages[0].userMessage
            == "Nous avons bien reçu ton dossier le 30/10/2021. Rends toi sur la messagerie du site Démarches-Simplifiées pour être informé en temps réel."
        )

    @patch.object(DMSGraphQLClient, "execute_query")
    def test_dms_request_refused_application(self, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(12, state="closed", email=user.email)

        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.refused.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert len(user.subscriptionMessages) == 1
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.WARNING
        assert (
            user.subscriptionMessages[0].userMessage
            == "Ton dossier déposé sur le site Démarches-Simplifiées a été rejeté. Tu n’es malheureusement pas éligible au pass culture."
        )
