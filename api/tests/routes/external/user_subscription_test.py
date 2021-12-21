import datetime
import json
import time
from unittest.mock import patch
import uuid

from dateutil import relativedelta
import freezegun
import pytest

from pcapi import settings
from pcapi.connectors.api_demarches_simplifiees import DMSGraphQLClient
from pcapi.connectors.api_demarches_simplifiees import GraphQLApplicationStates
from pcapi.core import testing
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.repository import repository
from pcapi.validation.routes import ubble as ubble_routes

from tests.core.subscription import test_factories
from tests.scripts.beneficiary.fixture import make_single_application
from tests.test_utils import json_default


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
        assert user.subscriptionMessages[0].popOverIcon == subscription_models.PopOverIcon.ERROR
        assert (
            user.subscriptionMessages[0].userMessage
            == "Ton dossier déposé sur le site Démarches-Simplifiées a été rejeté. Tu n’es malheureusement pas éligible au pass culture."
        )

    @patch.object(DMSGraphQLClient, "execute_query")
    @patch.object(DMSGraphQLClient, "send_user_message")
    def test_dms_double_parsing_error(self, send_user_message, execute_query, client):
        user = users_factories.UserFactory()
        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.draft.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        execute_query.return_value = make_single_application(
            12,
            state=GraphQLApplicationStates.draft.value,
            email=user.email,
            postal_code="error_postal_code",
            id_piece_number="error_identity_piece_number",
        )
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1
        assert send_user_message.call_count == 1
        assert send_user_message.call_args[0][2] == subscription_messages.DMS_ERROR_MESSAGE_DOUBLE_ERROR

    @patch.object(DMSGraphQLClient, "execute_query")
    @patch.object(DMSGraphQLClient, "send_user_message")
    def test_dms_request_with_unexisting_user(self, send_user_message, execute_query, client):

        execute_query.return_value = make_single_application(
            12, state=GraphQLApplicationStates.draft.value, email="user@example.com"
        )
        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.draft.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1
        assert send_user_message.call_count == 1
        assert send_user_message.call_args[0][2] == subscription_messages.DMS_ERROR_MESSAGE_USER_NOT_FOUND

    @patch.object(DMSGraphQLClient, "execute_query")
    @patch.object(DMSGraphQLClient, "send_user_message")
    def test_dms_id_piece_number_error(self, send_user_message, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            12,
            state=GraphQLApplicationStates.draft.value,
            email=user.email,
            id_piece_number="error_identity_piece_number",
        )
        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.draft.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1
        assert send_user_message.call_count == 1
        assert send_user_message.call_args[0][2] == subscription_messages.DMS_ERROR_MESSAGE_ERROR_ID_PIECE

    @patch.object(DMSGraphQLClient, "execute_query")
    @patch.object(DMSGraphQLClient, "send_user_message")
    def test_dms_postal_code_error(self, send_user_message, execute_query, client):
        user = users_factories.UserFactory()
        execute_query.return_value = make_single_application(
            12, state=GraphQLApplicationStates.draft.value, email=user.email, postal_code="error_postal_code"
        )
        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.draft.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1
        assert send_user_message.call_count == 1
        assert send_user_message.call_args[0][2] == subscription_messages.DMS_ERROR_MESSAGE_ERROR_POSTAL_CODE

    @patch.object(DMSGraphQLClient, "execute_query")
    @patch.object(DMSGraphQLClient, "send_user_message")
    @freezegun.freeze_time("2021-12-20 09:00:00")
    @pytest.mark.parametrize("birthday_date", [datetime.date(2012, 5, 12), datetime.date(1999, 6, 12)])
    def test_dms_birth_date_error(self, send_user_message, execute_query, client, birthday_date):
        user = users_factories.UserFactory()
        return_value = make_single_application(
            12, state=GraphQLApplicationStates.draft.value, email=user.email, birth_date=birthday_date
        )

        execute_query.return_value = return_value

        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.draft.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }
        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 204
        assert execute_query.call_count == 1
        assert send_user_message.call_count == 1
        assert send_user_message.call_args[0][2] == subscription_messages.DMS_ERROR_MESSSAGE_BIRTH_DATE

    @patch.object(DMSGraphQLClient, "execute_query")
    @pytest.mark.parametrize(
        "subscription_state",
        [
            users_models.SubscriptionState.user_profiling_validated,
            users_models.SubscriptionState.phone_validated,
        ],
    )
    def test_dms_accepted_application_by_operator(self, execute_query, client, subscription_state):
        user = users_factories.UserFactory(subscriptionState=subscription_state)
        execute_query.return_value = make_single_application(
            12, state=GraphQLApplicationStates.accepted.value, email=user.email
        )

        form_data = {
            "procedure_id": "48860",
            "dossier_id": "6044787",
            "state": GraphQLApplicationStates.accepted.value,
            "updated_at": "2021-09-30 17:55:58 +0200",
        }

        response = client.post(
            f"/webhooks/dms/application_status?token={settings.DMS_WEBHOOK_TOKEN}",
            form=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 204

        assert user.subscriptionState == users_models.SubscriptionState.identity_check_pending
        assert user.beneficiaryFraudChecks[0].status == fraud_models.FraudCheckStatus.PENDING
        assert user.beneficiaryFraudChecks[0].type == fraud_models.FraudCheckType.DMS
        assert user.beneficiaryFraudChecks[0].eligibilityType == users_models.EligibilityType.AGE18


@pytest.mark.usefixtures("db_session")
class UbbleWebhookTest:
    def _get_request_body(self, fraud_check, status):
        return ubble_routes.WebhookRequest(
            identification_id=fraud_check.thirdPartyId,
            status=status,
            configuration=ubble_routes.Configuration(
                id=fraud_check.user.id,
                name="Pass Culture",
            ),
        )

    def _get_signature(self, payload):
        timestamp = str(int(time.time()))
        token = ubble_routes.compute_signature(timestamp.encode("utf-8"), payload.encode("utf-8"))
        return f"ts={timestamp},v1={token}"

    def _init_test(self, current_identification_state, notified_identification_state):
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            resultContent=fraud_factories.UbbleContentFactory(
                status=test_factories.STATE_STATUS_MAPPING[current_identification_state].value,
            ),
            user=user,
        )
        request_data = self._get_request_body(
            fraud_check, test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        )
        payload = json.dumps(request_data.dict(by_alias=True), default=json_default)
        signature = self._get_signature(payload)
        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=notified_identification_state,
            data__attributes__identification_id=str(request_data.identification_id),
        )
        return payload, request_data, signature, ubble_identification_response

    def test_webhook_signature_ok(self, client, ubble_mocker):
        current_identification_state = test_factories.IdentificationState.INITIATED
        notified_identification_state = test_factories.IdentificationState.PROCESSING
        payload, request_data, signature, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            response = client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": signature},
                raw_json=payload,
            )

        assert response.status_code == 200
        assert response.json == {"status": "ok"}

    def test_webhook_signature_bad(self, client, ubble_mocker):
        current_identification_state = test_factories.IdentificationState.INITIATED
        notified_identification_state = test_factories.IdentificationState.PROCESSING
        payload, request_data, _, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            response = client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": "bad_signature"},
                raw_json=payload,
            )

        assert response.status_code == 403
        assert response.json == {"signature": ["Invalid signature"]}

    def test_webhook_signature_missing(self, client, ubble_mocker):
        current_identification_state = test_factories.IdentificationState.INITIATED
        notified_identification_state = test_factories.IdentificationState.PROCESSING
        payload, request_data, _, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            response = client.post(
                "/webhooks/ubble/application_status",
                raw_json=payload,
            )

        assert response.status_code == 403
        assert response.json == {"signature": ["Invalid signature"]}

    def test_fraud_check_intiated(self, client, ubble_mocker):
        current_identification_state = test_factories.IdentificationState.NEW
        notified_identification_state = test_factories.IdentificationState.INITIATED
        payload, request_data, signature, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": signature},
                raw_json=payload,
            )

        fraud_check = fraud_api.ubble.get_ubble_fraud_check(
            ubble_identification_response.data.attributes.identification_id
        )
        assert fraud_check.reason is None
        assert fraud_check.reasonCodes is None
        assert fraud_check.status is fraud_models.FraudCheckStatus.PENDING
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id
        content = fraud_models.ubble.UbbleContent(**fraud_check.resultContent)
        assert content.score is None
        assert content.status == test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        assert content.comment is None
        assert content.last_name is None
        assert content.first_name is None
        assert content.birth_date is None
        assert content.supported is None
        assert content.document_type is None
        assert content.expiry_date_score is None
        assert content.id_document_number is None
        assert str(content.identification_id) == ubble_identification_response.data.attributes.identification_id
        assert (
            content.identification_url == f"{settings.UBBLE_API_URL}/identifications/{str(content.identification_id)}"
        )

    def test_fraud_check_aborted(self, client, ubble_mocker):
        current_identification_state = test_factories.IdentificationState.INITIATED
        notified_identification_state = test_factories.IdentificationState.ABORTED
        payload, request_data, signature, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": signature},
                raw_json=payload,
            )

        fraud_check = fraud_api.ubble.get_ubble_fraud_check(
            ubble_identification_response.data.attributes.identification_id
        )
        assert fraud_check.reason is None
        assert fraud_check.reasonCodes is None
        assert fraud_check.status is fraud_models.FraudCheckStatus.CANCELED
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id
        content = fraud_models.ubble.UbbleContent(**fraud_check.resultContent)
        assert content.score is None
        assert content.status == test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        assert content.comment is None
        assert content.last_name is None
        assert content.first_name is None
        assert content.birth_date is None
        assert content.supported is None
        assert content.document_type is None
        assert content.expiry_date_score is None
        assert str(content.identification_id) == ubble_identification_response.data.attributes.identification_id
        assert content.id_document_number is None
        assert (
            content.identification_url == f"{settings.UBBLE_API_URL}/identifications/{str(content.identification_id)}"
        )

    def test_fraud_check_processing(self, client, ubble_mocker):
        current_identification_state = test_factories.IdentificationState.INITIATED
        notified_identification_state = test_factories.IdentificationState.PROCESSING
        payload, request_data, signature, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": signature},
                raw_json=payload,
            )

        fraud_check = fraud_api.ubble.get_ubble_fraud_check(
            ubble_identification_response.data.attributes.identification_id
        )
        assert fraud_check.reason is None
        assert fraud_check.reasonCodes is None
        assert fraud_check.status is fraud_models.FraudCheckStatus.PENDING
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id
        assert fraud_check.user.hasCompletedIdCheck is True
        content = fraud_models.ubble.UbbleContent(**fraud_check.resultContent)
        document = list(filter(lambda included: included.type == "documents", ubble_identification_response.included))[
            0
        ].attributes
        assert content.score is None
        assert content.status == test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        assert content.comment == ubble_identification_response.data.attributes.comment
        assert content.last_name == document.last_name
        assert content.first_name == document.first_name
        assert str(content.birth_date) == document.birth_date
        assert content.supported is None
        assert content.document_type == document.document_type
        assert content.expiry_date_score is None
        assert str(content.identification_id) == ubble_identification_response.data.attributes.identification_id
        assert content.id_document_number == document.document_number
        assert (
            content.identification_url == f"{settings.UBBLE_API_URL}/identifications/{str(content.identification_id)}"
        )

    def test_fraud_check_valid(self, client, ubble_mocker, mocker):
        current_identification_state = test_factories.IdentificationState.PROCESSING
        notified_identification_state = test_factories.IdentificationState.VALID
        payload, request_data, signature, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": signature},
                raw_json=payload,
            )

        fraud_check = fraud_api.ubble.get_ubble_fraud_check(
            ubble_identification_response.data.attributes.identification_id
        )
        assert fraud_check.reason == ""
        assert fraud_check.reasonCodes == []
        assert fraud_check.status is fraud_models.FraudCheckStatus.OK
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id

        assert fraud_check.user.has_beneficiary_role
        assert len(fraud_check.user.deposits) == 1
        assert len(fraud_check.user.beneficiaryImports) == 1
        assert fraud_check.user.beneficiaryImports[0].source == BeneficiaryImportSources.ubble.value

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["To"] == fraud_check.user.email

        content = fraud_models.ubble.UbbleContent(**fraud_check.resultContent)
        document = list(filter(lambda included: included.type == "documents", ubble_identification_response.included))[
            0
        ].attributes
        assert content.score == fraud_models.ubble.UbbleScore.VALID.value
        assert content.status == test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        assert content.comment == ubble_identification_response.data.attributes.comment
        assert content.last_name == document.last_name
        assert content.first_name == document.first_name
        assert str(content.birth_date) == document.birth_date
        assert content.supported == fraud_models.ubble.UbbleScore.VALID.value
        assert content.document_type == document.document_type
        assert content.expiry_date_score == fraud_models.ubble.UbbleScore.VALID.value
        assert str(content.identification_id) == ubble_identification_response.data.attributes.identification_id
        assert content.id_document_number == document.document_number
        assert (
            content.identification_url == f"{settings.UBBLE_API_URL}/identifications/{str(content.identification_id)}"
        )

    def test_fraud_check_invalid(self, client, ubble_mocker, mocker):
        current_identification_state = test_factories.IdentificationState.PROCESSING
        notified_identification_state = test_factories.IdentificationState.INVALID
        payload, request_data, signature, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": signature},
                raw_json=payload,
            )

        fraud_check = fraud_api.ubble.get_ubble_fraud_check(
            ubble_identification_response.data.attributes.identification_id
        )
        assert fraud_check.reason is not None
        assert fraud_check.reasonCodes is not None
        assert fraud_check.status is fraud_models.FraudCheckStatus.KO
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id

        assert not fraud_check.user.has_beneficiary_role
        assert len(fraud_check.user.deposits) == 0

        assert len(mails_testing.outbox) == 0

        content = fraud_models.ubble.UbbleContent(**fraud_check.resultContent)
        document = list(filter(lambda included: included.type == "documents", ubble_identification_response.included))[
            0
        ].attributes
        document_check = list(
            filter(lambda included: included.type == "document-checks", ubble_identification_response.included)
        )[0].attributes
        assert content.score == fraud_models.ubble.UbbleScore.INVALID.value
        assert content.status == test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        assert content.comment == ubble_identification_response.data.attributes.comment
        assert content.last_name == document.last_name
        assert content.first_name == document.first_name
        assert str(content.birth_date) == document.birth_date
        assert content.supported == document_check.supported
        assert content.document_type == document.document_type
        assert content.expiry_date_score == document_check.expiry_date_score
        assert str(content.identification_id) == ubble_identification_response.data.attributes.identification_id
        assert content.id_document_number == document.document_number
        assert (
            content.identification_url == f"{settings.UBBLE_API_URL}/identifications/{str(content.identification_id)}"
        )

    def test_fraud_check_unprocessable(self, client, ubble_mocker, mocker):
        current_identification_state = test_factories.IdentificationState.PROCESSING
        notified_identification_state = test_factories.IdentificationState.UNPROCESSABLE
        payload, request_data, signature, ubble_identification_response = self._init_test(
            current_identification_state, notified_identification_state
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": signature},
                raw_json=payload,
            )

        fraud_check = fraud_api.ubble.get_ubble_fraud_check(
            ubble_identification_response.data.attributes.identification_id
        )
        assert fraud_check.reason == "Ubble score -1.0: None"
        assert fraud_check.reasonCodes == [fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE]
        assert fraud_check.status is fraud_models.FraudCheckStatus.KO
        assert fraud_check.type == fraud_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id

        assert not fraud_check.user.has_beneficiary_role
        assert len(fraud_check.user.deposits) == 0

        assert len(mails_testing.outbox) == 0

        content = fraud_models.ubble.UbbleContent(**fraud_check.resultContent)
        document = list(filter(lambda included: included.type == "documents", ubble_identification_response.included))[
            0
        ].attributes
        document_check = list(
            filter(lambda included: included.type == "document-checks", ubble_identification_response.included)
        )[0].attributes
        assert content.score == fraud_models.ubble.UbbleScore.UNDECIDABLE.value
        assert content.status == test_factories.STATE_STATUS_MAPPING[notified_identification_state]
        assert content.comment == ubble_identification_response.data.attributes.comment
        assert content.last_name == document.last_name
        assert content.first_name == document.first_name
        assert str(content.birth_date == document.birth_date)
        assert content.supported == document_check.supported
        assert content.document_type == document.document_type
        assert content.expiry_date_score == document_check.expiry_date_score
        assert str(content.identification_id) == ubble_identification_response.data.attributes.identification_id
        assert content.id_document_number == document.document_number
        assert (
            content.identification_url == f"{settings.UBBLE_API_URL}/identifications/{str(content.identification_id)}"
        )

    def test_birth_date_not_updated_with_ubble_test_emails(self, client, ubble_mocker, mocker):
        email = "whatever+ubble_test@example.com"
        subscription_birth_date = datetime.datetime.combine(datetime.date(1980, 1, 1), datetime.time(0, 0))
        document_birth_date = datetime.datetime.combine(datetime.date(2004, 6, 16), datetime.time(0, 0))
        user = users_factories.UserFactory(email=email, dateOfBirth=subscription_birth_date)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            resultContent=fraud_factories.UbbleContentFactory(
                status=test_factories.STATE_STATUS_MAPPING[test_factories.IdentificationState.PROCESSING].value,
            ),
            user=user,
        )
        request_data = self._get_request_body(fraud_check, fraud_models.ubble.UbbleIdentificationStatus.PROCESSED)
        payload = json.dumps(request_data.dict(by_alias=True), default=json_default)
        signature = self._get_signature(payload)
        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.VALID,
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=document_birth_date.date().isoformat()
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(),
            ],
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": signature},
                raw_json=payload,
            )

        db.session.refresh(user)
        assert user.dateOfBirth != document_birth_date
        assert user.dateOfBirth == subscription_birth_date
        assert fraud_check.source_data().birth_date == user.dateOfBirth.date()

    def test_birth_date_updated_non_with_ubble_test_emails(self, client, ubble_mocker, mocker):
        email = "whatever@example.com"
        subscription_birth_date = datetime.datetime.combine(datetime.date(1980, 1, 1), datetime.time(0, 0))
        document_birth_date = datetime.datetime.combine(datetime.date(2004, 6, 16), datetime.time(0, 0))
        user = users_factories.UserFactory(email=email, dateOfBirth=subscription_birth_date)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            resultContent=fraud_factories.UbbleContentFactory(
                status=test_factories.STATE_STATUS_MAPPING[test_factories.IdentificationState.PROCESSING].value,
            ),
            user=user,
        )
        request_data = self._get_request_body(fraud_check, fraud_models.ubble.UbbleIdentificationStatus.PROCESSED)
        payload = json.dumps(request_data.dict(by_alias=True), default=json_default)
        signature = self._get_signature(payload)
        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.VALID,
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=document_birth_date.date().isoformat()
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(),
            ],
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": signature},
                raw_json=payload,
            )

        db.session.refresh(user)
        assert user.dateOfBirth == document_birth_date
        assert user.dateOfBirth != subscription_birth_date

    @testing.override_settings(IS_PROD=True)
    def test_ubble_test_emails_not_actives_on_production(self, client, ubble_mocker, mocker):
        email = "whatever+ubble_test@example.com"
        subscription_birth_date = datetime.datetime.combine(datetime.date(1980, 1, 1), datetime.time(0, 0))
        document_birth_date = datetime.datetime.combine(datetime.date(2004, 6, 16), datetime.time(0, 0))
        user = users_factories.UserFactory(email=email, dateOfBirth=subscription_birth_date)
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            resultContent=fraud_factories.UbbleContentFactory(
                status=test_factories.STATE_STATUS_MAPPING[test_factories.IdentificationState.PROCESSING].value,
            ),
            user=user,
        )
        request_data = self._get_request_body(fraud_check, fraud_models.ubble.UbbleIdentificationStatus.PROCESSED)
        payload = json.dumps(request_data.dict(by_alias=True), default=json_default)
        signature = self._get_signature(payload)
        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.VALID,
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=document_birth_date.date().isoformat()
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(),
            ],
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": signature},
                raw_json=payload,
            )

        db.session.refresh(user)
        assert user.dateOfBirth == document_birth_date
        assert user.dateOfBirth != subscription_birth_date

    def test_older_than_18_cannot_become_beneficiary(self, client, ubble_mocker):
        fraudulous_birth_date = datetime.datetime.now() - relativedelta.relativedelta(years=18, months=6)
        document_birth_date = datetime.datetime.now() - relativedelta.relativedelta(years=28)
        user = users_factories.UserFactory(
            dateOfBirth=fraudulous_birth_date,
        )
        profiling_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent={},
            status=fraud_models.FraudCheckStatus.OK,
            reason=None,
            reasonCodes=None,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        repository.save(profiling_fraud_check)
        identification_id = str(uuid.uuid4())
        ubble_fraud_check = fraud_models.BeneficiaryFraudCheck(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            thirdPartyId=identification_id,
            resultContent={
                "birth_date": document_birth_date.date().isoformat(),
                "comment": "",
                "document_type": "CI",
                "expiry_date_score": None,
                "first_name": user.firstName,
                "id_document_number": "012345678910",
                "identification_id": identification_id,
                "identification_url": f"https://id.ubble.ai/{identification_id}",
                "last_name": user.lastName,
                "registration_datetime": datetime.datetime.now().isoformat(),
                "score": None,
                "status": fraud_models.ubble.UbbleIdentificationStatus.PROCESSING.value,
                "supported": None,
            },
            status=fraud_models.FraudCheckStatus.PENDING,
            reason=None,
            reasonCodes=None,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        repository.save(ubble_fraud_check)
        honor_fraud_check = fraud_models.BeneficiaryFraudCheck(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            thirdPartyId="internal_check_4483",
            resultContent=None,
            status=fraud_models.FraudCheckStatus.OK,
            reason=None,
            reasonCodes=None,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        repository.save(honor_fraud_check)

        request_data = self._get_request_body(ubble_fraud_check, fraud_models.ubble.UbbleIdentificationStatus.PROCESSED)
        payload = json.dumps(request_data.dict(by_alias=True), default=json_default)
        signature = self._get_signature(payload)
        ubble_identification_response = test_factories.UbbleIdentificationResponseFactory(
            identification_state=test_factories.IdentificationState.VALID,
            data__attributes__identification_id=str(request_data.identification_id),
            included=[
                test_factories.UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=ubble_fraud_check.resultContent["birth_date"],
                    attributes__document_number=ubble_fraud_check.resultContent["id_document_number"],
                    attributes__document_type=ubble_fraud_check.resultContent["document_type"],
                    attributes__first_name=ubble_fraud_check.resultContent["first_name"],
                    attributes__last_name=ubble_fraud_check.resultContent["last_name"],
                ),
                test_factories.UbbleIdentificationIncludedDocumentChecksFactory(
                    attributes__data_extracted_score=fraud_models.ubble.UbbleScore.VALID.value,
                    attributes__expiry_date_score=fraud_models.ubble.UbbleScore.VALID.value,
                    attributes__issue_date_score=fraud_models.ubble.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=fraud_models.ubble.UbbleScore.VALID.value,
                    attributes__mrz_validity_score=fraud_models.ubble.UbbleScore.VALID.value,
                    attributes__mrz_viz_score=fraud_models.ubble.UbbleScore.VALID.value,
                    attributes__ove_back_score=fraud_models.ubble.UbbleScore.VALID.value,
                    attributes__ove_front_score=fraud_models.ubble.UbbleScore.VALID.value,
                    attributes__ove_score=fraud_models.ubble.UbbleScore.VALID.value,
                    attributes__quality_score=fraud_models.ubble.UbbleScore.VALID.value,
                    attributes__visual_back_score=fraud_models.ubble.UbbleScore.VALID.value,
                    attributes__visual_front_score=fraud_models.ubble.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedFaceChecksFactory(
                    attributes__active_liveness_score=fraud_models.ubble.UbbleScore.VALID.value,
                    attributes__live_video_capture_score=fraud_models.ubble.UbbleScore.VALID.value,
                    attributes__quality_score=fraud_models.ubble.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedDocFaceMatchesFactory(
                    attributes__score=fraud_models.ubble.UbbleScore.VALID.value,
                ),
                test_factories.UbbleIdentificationIncludedReferenceDataChecksFactory(
                    attributes__score=fraud_models.ubble.UbbleScore.VALID.value,
                ),
            ],
        )

        with ubble_mocker(
            request_data.identification_id,
            json.dumps(ubble_identification_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            client.post(
                "/webhooks/ubble/application_status",
                headers={"Ubble-Signature": signature},
                raw_json=payload,
            )

        db.session.refresh(user)
        assert not user.has_beneficiary_role
        db.session.refresh(ubble_fraud_check)
        assert ubble_fraud_check.reason == "L'utilisateur n'est pas éligible"
