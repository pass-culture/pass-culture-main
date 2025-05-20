import datetime
import json
import pathlib
import re
import time
from unittest.mock import patch

import flask
import pytest
import requests_mock
import time_machine
from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.connectors.serialization.ubble_serializers import UbbleIdentificationStatus
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils.date import DATE_ISO_FORMAT
from pcapi.validation.routes import ubble as ubble_routes

import tests
from tests.conftest import TestClient
from tests.test_utils import json_default

from . import fixtures


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class UbbleV2EndToEndTest:
    @pytest.mark.features(WIP_UBBLE_V2=True)
    def test_beneficiary_activation_with_ubble_mocked_response(self, client, ubble_client):
        seventeen_years_ago = datetime.datetime.utcnow() - relativedelta(years=17, months=1)
        user = users_factories.UserFactory(
            dateOfBirth=seventeen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName="Catherine",
            lastName="Destivelle",
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, resultContent__first_name="Catherine", resultContent__last_name="Destivelle"
        )
        registration_date = datetime.datetime.strptime(
            fixtures.ID_VERIFICATION_APPROVED_RESPONSE["created_on"], DATE_ISO_FORMAT
        )
        eighteen_years_before_registration = registration_date - relativedelta(years=18, months=1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.STARTED,
            thirdPartyId="",
            resultContent=fraud_models.UbbleContent(
                birth_date=eighteen_years_before_registration.date(),
                external_applicant_id="eaplt_61313A10000000000000000000",
                id_document_number=f"{user.id:012}",
            ).dict(exclude_none=True),
        )

        with requests_mock.Mocker() as requests_mocker:
            self._start_ubble_workflow(user, client, requests_mocker)
            self._receive_and_ignore_verification_pending_webhook_notification(user, ubble_client)
            self._receive_and_ignore_capture_in_progress_webhook_notification(user, ubble_client)
            self._receive_and_handle_verification_refused_webhook_notification(
                user, client, ubble_client, requests_mocker
            )

            assert user.eligibility == users_models.EligibilityType.AGE17_18
            assert user.age < 18

            self._retry_ubble_workflow(user, client, requests_mocker)
            self._receive_and_ignore_capture_in_progress_webhook_notification(user, ubble_client)
            self._receive_and_handle_checks_in_progress_webhook_notification(
                user, client, ubble_client, requests_mocker
            )
            self._receive_and_handle_verification_approved_webhook_notification(
                user, client, ubble_client, requests_mocker
            )

            assert user.eligibility == users_models.EligibilityType.AGE17_18
            assert user.age >= 18

            self._create_honor_statement_fraud_check(user, client)

            assert user.is_beneficiary

    def _start_ubble_workflow(self, user, client, requests_mocker) -> None:
        requests_mocker.post(f"{settings.UBBLE_API_URL}/v2/applicants", json=fixtures.APPLICANT_CREATION_RESPONSE)
        requests_mocker.post(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications", json=fixtures.ID_VERIFICATION_CREATION_RESPONSE
        )
        requests_mocker.post(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fixtures.ID_VERIFICATION_CREATION_RESPONSE['id']}/attempts",
            json=fixtures.ID_VERIFICATION_ATTEMPT_RESPONSE,
        )

        response = client.with_token(user.email).post(
            "/native/v1/ubble_identification", json={"redirectUrl": "https://redirect.example.com"}
        )

        assert response.status_code == 200, response.json

    def _receive_and_ignore_verification_pending_webhook_notification(self, user, ubble_client) -> None:
        with patch(
            "pcapi.core.subscription.ubble.api.update_ubble_workflow",
        ) as mocked_update:
            response = ubble_client.post(
                "/webhooks/ubble/v2/application_status", json=fixtures.ID_VERIFICATION_PENDING_WEBHOOK_BODY
            )

            assert response.status_code == 200, response.json
            mocked_update.assert_not_called()

    def _receive_and_ignore_capture_in_progress_webhook_notification(self, user, ubble_client) -> None:
        with patch(
            "pcapi.core.subscription.ubble.api.update_ubble_workflow",
        ) as mocked_update:
            response = ubble_client.post(
                "/webhooks/ubble/v2/application_status", json=fixtures.ID_CAPTURE_IN_PROGRESS_WEBHOOK_BODY
            )

            assert response.status_code == 200, response.json
            mocked_update.assert_not_called()

    def _receive_and_handle_verification_refused_webhook_notification(
        self, user, client, ubble_client, requests_mocker
    ) -> None:
        requests_mocker.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fixtures.ID_VERIFICATION_CREATION_RESPONSE['id']}",
            json=fixtures.ID_VERIFICATION_REFUSED_RESPONSE,
        )

        response = ubble_client.post(
            "/webhooks/ubble/v2/application_status", json=fixtures.ID_VERIFICATION_REFUSED_WEBHOOK_BODY
        )
        assert response.status_code == 200, response.json

        (ubble_fraud_check,) = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.UBBLE
        ]
        assert ubble_fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS

    def _retry_ubble_workflow(self, user, client, requests_mocker) -> None:
        requests_mocker.post(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fixtures.ID_VERIFICATION_CREATION_RESPONSE['id']}/attempts",
            json=fixtures.ID_VERIFICATION_ATTEMPT_RESPONSE,
        )

        response = client.with_token(user.email).post(
            "/native/v1/ubble_identification", json={"redirectUrl": "https://redirect.example.com"}
        )

        assert response.status_code == 200, response.json

    def _receive_and_handle_checks_in_progress_webhook_notification(
        self, user, client, ubble_client, requests_mocker
    ) -> None:
        requests_mocker.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fixtures.ID_VERIFICATION_CREATION_RESPONSE['id']}",
            json=fixtures.ID_CHECKS_IN_PROGRESS_RESPONSE,
        )

        response = ubble_client.post(
            "/webhooks/ubble/v2/application_status", json=fixtures.ID_CHECKS_IN_PROGRESS_WEBHOOK_BODY
        )
        assert response.status_code == 200, response.json

        (ubble_fraud_check,) = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.UBBLE
        ]
        assert ubble_fraud_check.status == fraud_models.FraudCheckStatus.PENDING

    def _receive_and_handle_verification_approved_webhook_notification(
        self, user, client, ubble_client, requests_mocker
    ) -> None:
        requests_mocker.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fixtures.ID_VERIFICATION_CREATION_RESPONSE['id']}",
            json=fixtures.ID_VERIFICATION_APPROVED_RESPONSE,
        )

        response = ubble_client.post(
            "/webhooks/ubble/v2/application_status", json=fixtures.ID_VERIFICATION_APPROVED_WEBHOOK_BODY
        )
        assert response.status_code == 200, response.json

        ubble_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.UBBLE
        ]
        (deprecated_ubble_fraud_check, ok_ubble_fraud_check) = sorted(
            ubble_fraud_checks, key=lambda check: check.thirdPartyId
        )
        assert "deprecated" in deprecated_ubble_fraud_check.thirdPartyId, [c.thirdPartyId for c in ubble_fraud_checks]
        assert ok_ubble_fraud_check.status == fraud_models.FraudCheckStatus.OK

    def _create_honor_statement_fraud_check(self, user, client) -> None:
        response = client.with_token(user.email).post("/native/v1/subscription/honor_statement")

        assert response.status_code == 204, response.json


class UbbleDummyWebhookTest:
    def test_dummy_webhook_with_data(self, ubble_client):
        response = ubble_client.post("/webhooks/ubble/dummy", json=fixtures.ID_VERIFICATION_APPROVED_WEBHOOK_BODY)
        assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
@pytest.mark.features(WIP_UBBLE_V2=False)
class UbbleEndToEndTest:
    def _get_ubble_webhook_signature(self, payload):
        timestamp = str(int(time.time()))
        token = ubble_routes.compute_signature(timestamp.encode("utf-8"), payload.encode("utf-8"))
        return f"ts={timestamp},v1={token}"

    @time_machine.travel("2018-01-01")
    def test_beneficiary_activation(self, client, app):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime(2000, 1, 1),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName="Raoul",
            lastName="de Toul",
            address="23 rue du Collège",
            city="Toul",
            postalCode="54200",
            activity=users_models.ActivityEnum.HIGH_SCHOOL_STUDENT.value,
            schoolType=users_models.SchoolTypeEnum.PUBLIC_HIGH_SCHOOL,
            phoneNumber="+33612345678",
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user,
            resultContent=fraud_factories.ProfileCompletionContentFactory(first_name="Raoul", last_name="de Toulouz"),
        )

        ubble_client = TestClient(app.test_client())
        client.with_token(user.email)

        # Step 1:The user initializes a subscription with ubble
        next_step = subscription_api.get_user_subscription_state(user).next_step
        assert next_step == subscription_models.SubscriptionStep.IDENTITY_CHECK

        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.post(
                f"{settings.UBBLE_API_URL}/identifications/", json=fixtures.START_IDENTIFICATION_RESPONSE
            )

            response = client.post(
                "/native/v1/ubble_identification",
                json={"redirectUrl": "https://passculture.app/verification-identite/fin"},
            )
            assert response.status_code == 200, response.json

            assert requests_mocker.last_request.json() == {
                "data": {
                    "attributes": {
                        "identification-form": {"external-user-id": user.id, "phone-number": None},
                        "redirect_url": "https://passculture.app/verification-identite/fin",
                        "reference-data": {"first-name": "Raoul", "last-name": "de Toulouz"},
                        "webhook": flask.url_for("Public API.ubble_webhook_update_application_status", _external=True),
                    },
                    "type": "identifications",
                }
            }

        fraud_check = (
            db.session.query(fraud_models.BeneficiaryFraudCheck)
            .filter_by(userId=user.id, type=fraud_models.FraudCheckType.UBBLE)
            .one()
        )

        assert fraud_check.thirdPartyId == fixtures.IDENTIFICATION_ID
        assert fraud_check.status == fraud_models.FraudCheckStatus.STARTED
        assert fraud_check.source_data().status == UbbleIdentificationStatus.UNINITIATED

        assert response.status_code == 200
        assert response.json == {"identificationUrl": f"https://id.ubble.ai/{fixtures.IDENTIFICATION_ID}"}

        # Step 2: Ubble calls the webhook to inform that the identification has been initiated by user
        webhook_request_payload = {
            "configuration": {"id": 5, "name": "MyConfig"},
            "identification_id": fixtures.IDENTIFICATION_ID,
            "status": "initiated",
        }

        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.get(
                f"{settings.UBBLE_API_URL}/identifications/{fixtures.IDENTIFICATION_ID}/",
                json=fixtures.INITIATED_IDENTIFICATION_RESPONSE,
            )

            response = ubble_client.post(
                "/webhooks/ubble/application_status",
                headers={
                    "Ubble-Signature": self._get_ubble_webhook_signature(
                        json.dumps(webhook_request_payload, default=json_default)
                    )
                },
                json=webhook_request_payload,
            )

        assert response.status_code == 200
        assert fraud_check.status == fraud_models.FraudCheckStatus.STARTED
        assert fraud_check.source_data().status == UbbleIdentificationStatus.INITIATED

        # in case the user wants to continue the identification, we should return the same identification_id
        response = client.post(
            "/native/v1/ubble_identification",
            json={"redirectUrl": "https://passculture.app/verification-identite/fin"},
        )
        assert response.status_code == 200
        assert response.json == {"identificationUrl": f"https://id.ubble.ai/{fixtures.IDENTIFICATION_ID}"}

        next_step = subscription_api.get_user_subscription_state(user).next_step
        assert next_step == subscription_models.SubscriptionStep.IDENTITY_CHECK

        # Step 3: Ubble calls the webhook to inform that the identification has been completed by the user
        webhook_request_payload = {
            "configuration": {"id": 5, "name": "MyConfig"},
            "identification_id": fixtures.IDENTIFICATION_ID,
            "status": "processing",
        }

        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.get(
                f"{settings.UBBLE_API_URL}/identifications/{fixtures.IDENTIFICATION_ID}/",
                json=fixtures.PROCESSING_IDENTIFICATION_RESPONSE,
            )

            response = ubble_client.post(
                "/webhooks/ubble/application_status",
                headers={
                    "Ubble-Signature": self._get_ubble_webhook_signature(
                        json.dumps(webhook_request_payload, default=json_default)
                    )
                },
                json=webhook_request_payload,
            )

        assert response.status_code == 200
        assert fraud_check.status == fraud_models.FraudCheckStatus.PENDING
        assert fraud_check.source_data().status == UbbleIdentificationStatus.PROCESSING

        next_step = subscription_api.get_user_subscription_state(user).next_step
        assert next_step == subscription_models.SubscriptionStep.HONOR_STATEMENT

        # Step 4: The user performs the HONOR_STATEMENT step
        response = client.post("/native/v1/subscription/honor_statement")
        assert (
            db.session.query(fraud_models.BeneficiaryFraudCheck)
            .filter_by(user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT)
            .one()
            .status
            == fraud_models.FraudCheckStatus.OK
        )

        # Step 5: Ubble calls the webhook to inform that the identification has been manually processed
        webhook_request_payload = {
            "configuration": {"id": 5, "name": "MyConfig"},
            "identification_id": fixtures.IDENTIFICATION_ID,
            "status": "processed",
        }
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.get(
                f"{settings.UBBLE_API_URL}/identifications/{fixtures.IDENTIFICATION_ID}/",
                json=fixtures.PROCESSED_IDENTIFICATION_RESPONSE,
            )
            storage_path_matcher = re.compile("https://storage.ubble.ai/*")
            requests_mocker.get(storage_path_matcher)

            response = ubble_client.post(
                "/webhooks/ubble/application_status",
                headers={
                    "Ubble-Signature": self._get_ubble_webhook_signature(
                        json.dumps(webhook_request_payload, default=json_default)
                    )
                },
                json=webhook_request_payload,
            )

        assert response.status_code == 200
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert fraud_check.source_data().status == UbbleIdentificationStatus.PROCESSED
        assert fraud_check.source_data().processed_datetime == datetime.datetime(
            2018, 1, 1, 8, 41, 2, 504663, tzinfo=datetime.timezone.utc
        )
        assert fraud_check.source_data().status_updated_at == datetime.datetime(
            2018, 1, 1, 8, 41, 2, 504682, tzinfo=datetime.timezone.utc
        )

        assert user.is_beneficiary
        assert user.has_active_deposit
        assert user.deposit.amount == 300
        assert user.firstName == "RAOUL"
        assert user.lastName == "DE TOULON"
