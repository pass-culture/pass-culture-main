import json
import time
from unittest.mock import patch

import freezegun
import pytest

from pcapi import settings
from pcapi.connectors.api_demarches_simplifiees import DMSGraphQLClient
from pcapi.connectors.api_demarches_simplifiees import GraphQLApplicationStates
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.api import get_ubble_fraud_check
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.fraud.models import FraudCheckType
from pcapi.core.fraud.models import FraudReasonCode
from pcapi.core.fraud.models import UbbleContent
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import factories as users_factories
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.validation.routes.ubble import Configuration
from pcapi.validation.routes.ubble import WebhookRequest
from pcapi.validation.routes.ubble import compute_signature

from tests.core.subscription.test_factories import IdentificationState
from tests.core.subscription.test_factories import STATE_STATUS_MAPPING
from tests.core.subscription.test_factories import UbbleIdentificationResponseFactory
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


@pytest.mark.usefixtures("db_session")
class UbbleWebhookTest:
    def _get_request_body(self, fraud_check, status):
        return WebhookRequest(
            identification_id=fraud_check.thirdPartyId,
            status=status,
            configuration=Configuration(
                id=fraud_check.user.id,
                name="Pass Culture",
            ),
        )

    def _get_signature(self, payload):
        timestamp = str(int(time.time()))
        token = compute_signature(timestamp.encode("utf-8"), payload.encode("utf-8"))
        return f"ts={timestamp},v1={token}"

    def _init_test(self, current_identification_state, notified_identification_state):
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            resultContent=fraud_factories.UbbleContentFactory(
                status=STATE_STATUS_MAPPING[current_identification_state].value,
            ),
            user=user,
        )
        request_data = self._get_request_body(fraud_check, STATE_STATUS_MAPPING[notified_identification_state])
        payload = json.dumps(request_data.dict(by_alias=True), default=json_default)
        signature = self._get_signature(payload)
        ubble_identification_response = UbbleIdentificationResponseFactory(
            identification_state=notified_identification_state,
            data__attributes__identification_id=str(request_data.identification_id),
        )
        return payload, request_data, signature, ubble_identification_response

    def test_webhook_signature_ok(self, client, ubble_mocker):
        current_identification_state = IdentificationState.INITIATED
        notified_identification_state = IdentificationState.PROCESSING
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
        current_identification_state = IdentificationState.INITIATED
        notified_identification_state = IdentificationState.PROCESSING
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
        current_identification_state = IdentificationState.INITIATED
        notified_identification_state = IdentificationState.PROCESSING
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
        current_identification_state = IdentificationState.NEW
        notified_identification_state = IdentificationState.INITIATED
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

        fraud_check = get_ubble_fraud_check(ubble_identification_response.data.attributes.identification_id)
        assert fraud_check.reason is None
        assert fraud_check.reasonCodes is None
        assert fraud_check.status is FraudCheckStatus.PENDING
        assert fraud_check.type == FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id
        content = UbbleContent(**fraud_check.resultContent)
        assert content.score is None
        assert content.status == STATE_STATUS_MAPPING[notified_identification_state]
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
        current_identification_state = IdentificationState.INITIATED
        notified_identification_state = IdentificationState.ABORTED
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

        fraud_check = get_ubble_fraud_check(ubble_identification_response.data.attributes.identification_id)
        assert fraud_check.reason is None
        assert fraud_check.reasonCodes is None
        assert fraud_check.status is FraudCheckStatus.CANCELED
        assert fraud_check.type == FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id
        content = UbbleContent(**fraud_check.resultContent)
        assert content.score is None
        assert content.status == STATE_STATUS_MAPPING[notified_identification_state]
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
        current_identification_state = IdentificationState.INITIATED
        notified_identification_state = IdentificationState.PROCESSING
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

        fraud_check = get_ubble_fraud_check(ubble_identification_response.data.attributes.identification_id)
        assert fraud_check.reason is None
        assert fraud_check.reasonCodes is None
        assert fraud_check.status is FraudCheckStatus.PENDING
        assert fraud_check.type == FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id
        assert fraud_check.user.hasCompletedIdCheck is True
        content = UbbleContent(**fraud_check.resultContent)
        document = list(filter(lambda included: included.type == "documents", ubble_identification_response.included))[
            0
        ].attributes
        assert content.score is None
        assert content.status == STATE_STATUS_MAPPING[notified_identification_state]
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

    def test_fraud_check_valid(self, client, ubble_mocker):
        current_identification_state = IdentificationState.PROCESSING
        notified_identification_state = IdentificationState.VALID
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

        fraud_check = get_ubble_fraud_check(ubble_identification_response.data.attributes.identification_id)
        assert fraud_check.reason == ""
        assert fraud_check.reasonCodes == []
        assert fraud_check.status is FraudCheckStatus.OK
        assert fraud_check.type == FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id
        content = UbbleContent(**fraud_check.resultContent)
        document = list(filter(lambda included: included.type == "documents", ubble_identification_response.included))[
            0
        ].attributes
        assert content.score == fraud_models.UbbleScore.VALID.value
        assert content.status == STATE_STATUS_MAPPING[notified_identification_state]
        assert content.comment == ubble_identification_response.data.attributes.comment
        assert content.last_name == document.last_name
        assert content.first_name == document.first_name
        assert str(content.birth_date) == document.birth_date
        assert content.supported == fraud_models.UbbleScore.VALID.value
        assert content.document_type == document.document_type
        assert content.expiry_date_score == fraud_models.UbbleScore.VALID.value
        assert str(content.identification_id) == ubble_identification_response.data.attributes.identification_id
        assert content.id_document_number == document.document_number
        assert (
            content.identification_url == f"{settings.UBBLE_API_URL}/identifications/{str(content.identification_id)}"
        )

    def test_fraud_check_invalid(self, client, ubble_mocker):
        current_identification_state = IdentificationState.PROCESSING
        notified_identification_state = IdentificationState.INVALID
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

        fraud_check = get_ubble_fraud_check(ubble_identification_response.data.attributes.identification_id)
        assert fraud_check.reason is not None
        assert fraud_check.reasonCodes is not None
        assert fraud_check.status is FraudCheckStatus.KO
        assert fraud_check.type == FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id
        content = UbbleContent(**fraud_check.resultContent)
        document = list(filter(lambda included: included.type == "documents", ubble_identification_response.included))[
            0
        ].attributes
        document_check = list(
            filter(lambda included: included.type == "document-checks", ubble_identification_response.included)
        )[0].attributes
        assert content.score == fraud_models.UbbleScore.INVALID.value
        assert content.status == STATE_STATUS_MAPPING[notified_identification_state]
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

    def test_fraud_check_unprocessable(self, client, ubble_mocker):
        current_identification_state = IdentificationState.PROCESSING
        notified_identification_state = IdentificationState.UNPROCESSABLE
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

        fraud_check = get_ubble_fraud_check(ubble_identification_response.data.attributes.identification_id)
        assert fraud_check.reason == "Ubble score -1.0: None"
        assert fraud_check.reasonCodes == [FraudReasonCode.ID_CHECK_UNPROCESSABLE]
        assert fraud_check.status is FraudCheckStatus.KO
        assert fraud_check.type == FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId == ubble_identification_response.data.attributes.identification_id
        content = UbbleContent(**fraud_check.resultContent)
        document = list(filter(lambda included: included.type == "documents", ubble_identification_response.included))[
            0
        ].attributes
        document_check = list(
            filter(lambda included: included.type == "document-checks", ubble_identification_response.included)
        )[0].attributes
        assert content.score == fraud_models.UbbleScore.UNDECIDABLE.value
        assert content.status == STATE_STATUS_MAPPING[notified_identification_state]
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
