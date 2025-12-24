import datetime
import json
import pathlib
import re
import time
from unittest.mock import patch

import pytest
import requests_mock
import sqlalchemy as sa
import time_machine
from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.routes.external.authentication import compute_signature
from pcapi.utils import date as date_utils
from pcapi.utils.date import DATE_ISO_FORMAT

import tests
from tests.conftest import TestClient
from tests.test_utils import json_default

from . import fixtures


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class UbbleV2EndToEndTest:
    @pytest.mark.time_machine("2025-02-02")
    def test_beneficiary_activation_with_ubble_mocked_response(self, client, ubble_client):
        seventeen_years_ago = date_utils.get_naive_utc_now() - relativedelta(years=17, months=1)
        user = users_factories.UserFactory(
            dateOfBirth=seventeen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName="Catherine",
            lastName="Destivelle",
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(
            user=user, resultContent__first_name="Catherine", resultContent__last_name="Destivelle"
        )
        registration_date = datetime.datetime.strptime(
            fixtures.ID_VERIFICATION_APPROVED_RESPONSE["created_on"], DATE_ISO_FORMAT
        )
        eighteen_years_before_registration = registration_date - relativedelta(years=18, months=1)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.STARTED,
            thirdPartyId="",
            resultContent=ubble_schemas.UbbleContent(
                birth_date=eighteen_years_before_registration.date(),
                external_applicant_id="eaplt_61313A10000000000000000000",
                id_document_number=f"{user.id:012}",
            ).dict(exclude_none=True),
        )

        user_id = user.id  # keep access to the id even after the user is expunged from the session
        with requests_mock.Mocker() as requests_mocker:
            self._start_ubble_workflow(user, client, requests_mocker)
            self._receive_and_ignore_verification_pending_webhook_notification(user, ubble_client)
            self._receive_and_ignore_capture_in_progress_webhook_notification(user, ubble_client)
            self._receive_and_handle_verification_refused_webhook_notification(
                user, client, ubble_client, requests_mocker
            )

            user = _refresh_user(user_id)
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

            user = _refresh_user(user_id)
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

        response = client.with_token(user).post(
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

        user_id = user.id
        response = ubble_client.post(
            "/webhooks/ubble/v2/application_status", json=fixtures.ID_VERIFICATION_REFUSED_WEBHOOK_BODY
        )
        assert response.status_code == 200, response.json

        user = _refresh_user(user_id)
        (ubble_fraud_check,) = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == subscription_models.FraudCheckType.UBBLE
        ]
        assert ubble_fraud_check.status == subscription_models.FraudCheckStatus.SUSPICIOUS

    def _retry_ubble_workflow(self, user, client, requests_mocker) -> None:
        requests_mocker.post(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fixtures.ID_VERIFICATION_CREATION_RESPONSE['id']}/attempts",
            json=fixtures.ID_VERIFICATION_ATTEMPT_RESPONSE,
        )

        response = client.with_token(user).post(
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

        user_id = user.id
        response = ubble_client.post(
            "/webhooks/ubble/v2/application_status", json=fixtures.ID_CHECKS_IN_PROGRESS_WEBHOOK_BODY
        )
        assert response.status_code == 200, response.json

        user = _refresh_user(user_id)
        (ubble_fraud_check,) = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == subscription_models.FraudCheckType.UBBLE
        ]
        assert ubble_fraud_check.status == subscription_models.FraudCheckStatus.PENDING

    def _receive_and_handle_verification_approved_webhook_notification(
        self, user, client, ubble_client, requests_mocker
    ) -> None:
        requests_mocker.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fixtures.ID_VERIFICATION_CREATION_RESPONSE['id']}",
            json=fixtures.ID_VERIFICATION_APPROVED_RESPONSE,
        )

        user_id = user.id
        response = ubble_client.post(
            "/webhooks/ubble/v2/application_status", json=fixtures.ID_VERIFICATION_APPROVED_WEBHOOK_BODY
        )
        assert response.status_code == 200, response.json

        user = _refresh_user(user_id)
        ubble_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == subscription_models.FraudCheckType.UBBLE
        ]
        (deprecated_ubble_fraud_check, ok_ubble_fraud_check) = sorted(
            ubble_fraud_checks, key=lambda check: check.thirdPartyId
        )
        assert "deprecated" in deprecated_ubble_fraud_check.thirdPartyId, [c.thirdPartyId for c in ubble_fraud_checks]
        assert ok_ubble_fraud_check.status == subscription_models.FraudCheckStatus.OK

    def _create_honor_statement_fraud_check(self, user, client) -> None:
        response = client.with_token(user).post("/native/v1/subscription/honor_statement")

        assert response.status_code == 204, response.json


class UbbleDummyWebhookTest:
    def test_dummy_webhook_with_data(self, ubble_client):
        response = ubble_client.post("/webhooks/ubble/dummy", json=fixtures.ID_VERIFICATION_APPROVED_WEBHOOK_BODY)
        assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
class UbbleEndToEndTest:
    def _get_ubble_webhook_signature(self, payload):
        timestamp = str(int(time.time()))
        token = compute_signature(timestamp.encode("utf-8"), payload.encode("utf-8"))
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
        user_id = user.id
        subscription_factories.ProfileCompletionFraudCheckFactory(
            user=user,
            resultContent=subscription_factories.ProfileCompletionContentFactory(
                first_name="Raoul", last_name="de Toulouz"
            ),
        )

        ubble_client = TestClient(app.test_client())
        client.with_token(user)

        # Step 1: The user initializes a subscription with ubble
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            thirdPartyId=fixtures.IDENTIFICATION_ID,
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=subscription_factories.UbbleContentFactory(
                status=ubble_schemas.UbbleIdentificationStatus.UNINITIATED
            ),
        )

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

        fraud_check = (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(userId=user.id, type=subscription_models.FraudCheckType.UBBLE)
            .one()
        )
        fraud_check_id = fraud_check.id
        assert fraud_check.status == subscription_models.FraudCheckStatus.STARTED
        assert fraud_check.source_data().status == ubble_schemas.UbbleIdentificationStatus.INITIATED

        # in case the user wants to continue the identification, we should return the same identification_id
        response = client.post(
            "/native/v1/ubble_identification",
            json={"redirectUrl": "https://passculture.app/verification-identite/fin"},
        )
        assert response.status_code == 200
        assert response.json == {"identificationUrl": f"https://id.ubble.ai/{fixtures.IDENTIFICATION_ID}"}

        next_step = subscription_api.get_user_subscription_state(user).next_step
        assert next_step == subscription_schemas.SubscriptionStep.IDENTITY_CHECK

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
        assert fraud_check.status == subscription_models.FraudCheckStatus.PENDING
        assert fraud_check.source_data().status == ubble_schemas.UbbleIdentificationStatus.PROCESSING

        next_step = subscription_api.get_user_subscription_state(user).next_step
        assert next_step == subscription_schemas.SubscriptionStep.HONOR_STATEMENT

        # Step 4: The user performs the HONOR_STATEMENT step
        response = client.post("/native/v1/subscription/honor_statement")
        assert (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(user=user, type=subscription_models.FraudCheckType.HONOR_STATEMENT)
            .one()
            .status
            == subscription_models.FraudCheckStatus.OK
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

        fraud_check = _refresh_fraud_check(fraud_check_id)
        assert fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert fraud_check.source_data().status == ubble_schemas.UbbleIdentificationStatus.PROCESSED
        assert fraud_check.source_data().processed_datetime == datetime.datetime(
            2018, 1, 1, 8, 41, 2, 504663, tzinfo=datetime.timezone.utc
        )
        assert fraud_check.source_data().status_updated_at == datetime.datetime(
            2018, 1, 1, 8, 41, 2, 504682, tzinfo=datetime.timezone.utc
        )

        user = _refresh_user(user_id)
        assert user.is_beneficiary
        assert user.has_active_deposit
        assert user.deposit.amount == 300
        assert user.firstName == "RAOUL"
        assert user.lastName == "DE TOULON"


def _refresh_user(user_id: int) -> users_models.User:
    """
    Celery task transactions expunge the current user, so we must refetch them after each task
    """
    return db.session.scalar(sa.select(users_models.User).where(users_models.User.id == user_id))


def _refresh_fraud_check(fraud_check_id: int) -> subscription_models.BeneficiaryFraudCheck:
    """
    Celery task transactions expunge the current fraud check, so we must refetch them after each task
    """
    return db.session.scalar(
        sa.select(subscription_models.BeneficiaryFraudCheck).where(
            subscription_models.BeneficiaryFraudCheck.id == fraud_check_id
        )
    )
