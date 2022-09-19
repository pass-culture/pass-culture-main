import datetime
import json
import pathlib
import re
import time

import flask
import freezegun
import pytest
import requests_mock

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble.models import UbbleIdentificationStatus
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.validation.routes import ubble as ubble_routes

import tests
from tests.conftest import TestClient
from tests.test_utils import json_default

from . import requests_data


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class UbbleEndToEndTest:
    def _get_ubble_webhook_signature(self, payload):
        timestamp = str(int(time.time()))
        token = ubble_routes.compute_signature(timestamp.encode("utf-8"), payload.encode("utf-8"))
        return f"ts={timestamp},v1={token}"

    @freezegun.freeze_time("2018-01-01")
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
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.USER_PROFILING, status=fraud_models.FraudCheckStatus.OK
        )

        ubble_client = TestClient(app.test_client())
        client.with_token(user.email)

        # Step 1:The user initializes a subscription with ubble
        next_step = subscription_api.get_next_subscription_step(user)
        assert next_step == subscription_models.SubscriptionStep.IDENTITY_CHECK

        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.post(
                "https://api.ubble.ai/identifications/", json=requests_data.START_IDENTIFICATION_RESPONSE
            )

            response = client.post(
                "/native/v1/ubble_identification",
                json={"redirectUrl": "https://passculture.app/verification-identite/fin"},
            )

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

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            userId=user.id, type=fraud_models.FraudCheckType.UBBLE
        ).one()

        assert fraud_check.thirdPartyId == requests_data.IDENTIFICATION_ID
        assert fraud_check.status == fraud_models.FraudCheckStatus.STARTED
        assert fraud_check.source_data().status == UbbleIdentificationStatus.UNINITIATED

        assert response.status_code == 200
        assert response.json == {"identificationUrl": f"https://id.ubble.ai/{requests_data.IDENTIFICATION_ID}"}

        # Step 2: Ubble calls the webhook to inform that the identification has been initiated by user
        webhook_request_payload = {
            "configuration": {"id": 5, "name": "MyConfig"},
            "identification_id": requests_data.IDENTIFICATION_ID,
            "status": "initiated",
        }

        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.get(
                f"https://api.ubble.ai/identifications/{requests_data.IDENTIFICATION_ID}/",
                json=requests_data.INITIATED_IDENTIFICATION_RESPONSE,
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
        assert response.json == {"identificationUrl": f"https://id.ubble.ai/{requests_data.IDENTIFICATION_ID}"}

        next_step = subscription_api.get_next_subscription_step(user)
        assert next_step == subscription_models.SubscriptionStep.IDENTITY_CHECK

        # Step 3: Ubble calls the webhook to inform that the identification has been completed by the user
        webhook_request_payload = {
            "configuration": {"id": 5, "name": "MyConfig"},
            "identification_id": requests_data.IDENTIFICATION_ID,
            "status": "processing",
        }

        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.get(
                f"https://api.ubble.ai/identifications/{requests_data.IDENTIFICATION_ID}/",
                json=requests_data.PROCESSING_IDENTIFICATION_RESPONSE,
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

        next_step = subscription_api.get_next_subscription_step(user)
        assert next_step == subscription_models.SubscriptionStep.HONOR_STATEMENT

        # Step 4: The user performs the HONOR_STATEMENT step
        response = client.post("/native/v1/subscription/honor_statement")
        assert (
            fraud_models.BeneficiaryFraudCheck.query.filter_by(
                user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT
            )
            .one()
            .status
            == fraud_models.FraudCheckStatus.OK
        )

        # Step 5: Ubble calls the webhook to inform that the identification has been manually processed
        webhook_request_payload = {
            "configuration": {"id": 5, "name": "MyConfig"},
            "identification_id": requests_data.IDENTIFICATION_ID,
            "status": "processed",
        }
        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.get(
                f"https://api.ubble.ai/identifications/{requests_data.IDENTIFICATION_ID}/",
                json=requests_data.PROCESSED_IDENTIFICATION_RESPONSE,
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

        assert user.is_beneficiary
        assert user.has_active_deposit
        assert user.deposit.amount == 300
        assert user.firstName == "RAOUL"
        assert user.lastName == "DE TOULON"
