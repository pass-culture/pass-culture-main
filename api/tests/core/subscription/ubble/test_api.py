import datetime
import json
import pathlib
from io import BytesIO
from unittest.mock import call
from unittest.mock import patch

import pytest
import time_machine
from dateutil.relativedelta import relativedelta

import pcapi.notifications.push.testing as push_testing
from pcapi import settings
from pcapi.core.fraud.exceptions import IncompatibleFraudCheckStatus
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.exceptions import BeneficiaryFraudCheckMissingException
from pcapi.core.subscription.factories import BeneficiaryFraudCheckFactory
from pcapi.core.subscription.factories import ProfileCompletionFraudCheckFactory
from pcapi.core.subscription.factories import UbbleContentFactory
from pcapi.core.subscription.models import FraudCheckStatus
from pcapi.core.subscription.models import FraudCheckType
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.subscription.ubble import constants as ubble_constants
from pcapi.core.subscription.ubble import errors as ubble_errors
from pcapi.core.subscription.ubble import exceptions as ubble_exceptions
from pcapi.core.subscription.ubble import schemas as ubble_schemas
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.notifications.push import trigger_events
from pcapi.utils import date as date_utils
from pcapi.utils import requests as requests_utils
from pcapi.utils.date import DATE_ISO_FORMAT
from pcapi.utils.string import u_nbsp
from pcapi.utils.transaction_manager import atomic

import tests
from tests.connectors.beneficiaries.ubble_fixtures import UBBLE_IDENTIFICATION_V2_RESPONSE
from tests.connectors.beneficiaries.ubble_fixtures import build_ubble_identification_v2_response
from tests.core.subscription.test_factories import IdentificationState
from tests.core.subscription.test_factories import UbbleIdentificationIncludedDocumentsFactory
from tests.core.subscription.test_factories import UbbleIdentificationResponseFactory
from tests.test_utils import json_default


IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class UbbleWorkflowV2Test:
    def test_start_ubble_workflow(self, requests_mock):
        user = users_factories.UserFactory()
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/create-and-start-idv",
            json=build_ubble_identification_v2_response(status="pending", response_codes=[], documents=[]),
        )

        redirect_url = ubble_subscription_api.start_ubble_workflow(
            user, "Oriane", "Bertone", redirect_url="https://redirect.example.com"
        )

        assert redirect_url == "https://verification.ubble.example.com/"

        fraud_check = user.beneficiaryFraudChecks[0]
        assert fraud_check.type == subscription_models.FraudCheckType.UBBLE
        assert fraud_check.thirdPartyId is not None
        assert fraud_check.resultContent is not None
        assert fraud_check.status == subscription_models.FraudCheckStatus.STARTED

        ubble_request = requests_mock.last_request.json()
        assert ubble_request["webhook_url"] == "http://localhost/webhooks/ubble/v2/application_status"

        assert push_testing.requests[0] == {
            "can_be_asynchronously_retried": True,
            "event_name": "user_identity_check_started",
            "event_payload": {"type": "ubble"},
            "user_id": user.id,
        }

    def test_applicant_creation_flow(self, requests_mock):
        user = users_factories.UserFactory()
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
            thirdPartyId="",
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=UbbleContentFactory(
                status=ubble_schemas.UbbleIdentificationStatus.PENDING,
                external_applicant_id="eaplt_61301A10000000000000000000",
            ),
        )
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/applicants",
            json={
                "id": "aplt_qwerty123",
                "created_on": "2023-07-21T17:32:28Z",
                "modified_on": "2023-07-21T17:40:32Z",
                "external_applicant_id": "eaplt_61301A10000000000000000000",
                "email": user.email,
                "_links": {"self": {"href": "https://api.ubble.example.com/v2/applicants/aplt_qwerty123"}},
            },
        )
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications",
            json=build_ubble_identification_v2_response(status="pending", response_codes=[], documents=[]),
        )
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{UBBLE_IDENTIFICATION_V2_RESPONSE['id']}/attempts",
            json=build_ubble_identification_v2_response(status="pending", response_codes=[], documents=[]),
        )

        ubble_subscription_api.start_ubble_workflow(
            user, user.firstName, user.lastName, redirect_url="https://redirect.example.com"
        )

        create_applicant_request, create_identification_request, attempt_identification_request = (
            requests_mock.request_history[-3:]
        )
        assert create_applicant_request.url == f"{settings.UBBLE_API_URL}/v2/applicants"
        assert create_applicant_request.json() == {
            "external_applicant_id": "eaplt_61301A10000000000000000000",
            "email": fraud_check.user.email,
        }
        assert create_identification_request.url == f"{settings.UBBLE_API_URL}/v2/identity-verifications"
        assert create_identification_request.json()["applicant_id"] == "aplt_qwerty123"
        assert (
            create_identification_request.json()["webhook_url"]
            == "http://localhost/webhooks/ubble/v2/application_status"
        )
        assert (
            attempt_identification_request.url
            == f"{settings.UBBLE_API_URL}/v2/identity-verifications/{UBBLE_IDENTIFICATION_V2_RESPONSE['id']}/attempts"
        )
        assert attempt_identification_request.json()["redirect_url"] == "https://redirect.example.com"

    def test_applicant_creation_flow_updates_fraud_check(self, requests_mock):
        user = users_factories.UserFactory()
        BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
            thirdPartyId="",
            status=subscription_models.FraudCheckStatus.STARTED,
            resultContent=UbbleContentFactory(
                status=ubble_schemas.UbbleIdentificationStatus.PENDING,
                external_applicant_id="eaplt_61301A10000000000000000000",
            ),
        )
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/applicants",
            json={
                "id": UBBLE_IDENTIFICATION_V2_RESPONSE["applicant_id"],
                "created_on": "2023-07-21T17:32:28Z",
                "modified_on": "2023-07-21T17:40:32Z",
                "external_applicant_id": "eaplt_61301A10000000000000000000",
                "email": user.email,
                "_links": {
                    "self": {
                        "href": f"https://api.ubble.example.com/v2/applicants/{UBBLE_IDENTIFICATION_V2_RESPONSE['applicant_id']}"
                    }
                },
            },
        )
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications",
            json=build_ubble_identification_v2_response(status="pending", response_codes=[], documents=[]),
        )
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{UBBLE_IDENTIFICATION_V2_RESPONSE['id']}/attempts",
            json=build_ubble_identification_v2_response(status="pending", response_codes=[], documents=[]),
        )

        ubble_subscription_api.start_ubble_workflow(
            user, user.firstName, user.lastName, redirect_url="https://redirect.example.com"
        )

        (ubble_fraud_check,) = user.beneficiaryFraudChecks
        ubble_content = ubble_fraud_check.resultContent
        assert ubble_content["applicant_id"] == UBBLE_IDENTIFICATION_V2_RESPONSE["applicant_id"]
        assert ubble_content["external_applicant_id"] == "eaplt_61301A10000000000000000000"
        assert ubble_content["identification_id"] == UBBLE_IDENTIFICATION_V2_RESPONSE["id"]

    def test_ubble_checks_in_progress(self, requests_mock):
        user = users_factories.UserFactory()
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
            thirdPartyId="idv_qwerty1234",
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(
                status=ubble_schemas.UbbleIdentificationStatus.CHECKS_IN_PROGRESS.value,
                response_codes=[],
                documents=[],
            ),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        assert fraud_check.status == subscription_models.FraudCheckStatus.PENDING

    @patch("pcapi.core.subscription.ubble.tasks.store_id_pictures_task.delay")
    def test_ubble_identification_approved(self, store_id_pictures_task_mock, requests_mock):
        user = users_factories.UserFactory(age=17)
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
            thirdPartyId="idv_qwerty1234",
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(
                birth_date=datetime.date.today() - relativedelta(years=18), created_on=datetime.datetime.today()
            ),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        assert fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert fraud_check.resultContent.get("birth_place") is not None
        store_id_pictures_task_mock.assert_called_once()

    @patch("pcapi.core.subscription.ubble.tasks.store_id_pictures_task.delay")
    def test_ubble_identification_approved_with_test_email(self, store_id_pictures_task_mock, requests_mock):
        user = users_factories.UserFactory(email="hello+ubble_test@example.com", age=17)
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
            thirdPartyId="idv_qwerty1234",
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        ignored_birth_date = datetime.date.today() - relativedelta(years=999)
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(
                birth_date=ignored_birth_date, created_on=datetime.datetime.today()
            ),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        assert fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert user.validatedBirthDate == user.dateOfBirth.date()

    def test_ubble_identification_approved_but_user_too_young(self, requests_mock):
        user = users_factories.UserFactory()
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
            thirdPartyId="idv_qwerty1234",
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        fourteen_years_ago = datetime.date.today() - relativedelta(years=14, months=1)
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(birth_date=fourteen_years_ago),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        assert fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.AGE_TOO_YOUNG]

    @pytest.mark.time_machine("2025-02-02")
    def test_ubble_identification_approved_but_user_too_old(self, requests_mock):
        user = users_factories.UserFactory(age=40)
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
            thirdPartyId="idv_qwerty1234",
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        twenty_years_ago = datetime.date.today() - relativedelta(years=20, months=1)
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(birth_date=twenty_years_ago),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        assert fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.AGE_TOO_OLD]

    def test_ubble_retry_required(self, requests_mock):
        user = users_factories.UserFactory()
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE, user=user, thirdPartyId="idv_qwerty1234"
        )
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(
                status="retry_required",
                response_codes=[{"code": 61302, "summary": "document_video_lighting_issue"}],
            ),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        ubble_content = fraud_check.resultContent
        assert ubble_content["status"] == ubble_schemas.UbbleIdentificationStatus.RETRY_REQUIRED.value
        assert fraud_check.status == subscription_models.FraudCheckStatus.SUSPICIOUS
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.LACK_OF_LUMINOSITY]
        assert "Ubble RETRY_REQUIRED" in fraud_check.reason

    def test_ubble_identification_declined(self, requests_mock):
        user = users_factories.UserFactory()
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE, user=user, thirdPartyId="idv_qwerty1234"
        )
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(
                status="declined",
                response_codes=[{"code": 62401, "summary": "declared_identity_mismatch"}],
                declared_data={"name": "Ai Mori"},
            ),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        ubble_content = fraud_check.resultContent
        assert ubble_content["status"] == ubble_schemas.UbbleIdentificationStatus.DECLINED.value
        assert fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.ID_CHECK_DATA_MATCH]
        assert "Ubble DECLINED" in fraud_check.reason

    @pytest.mark.parametrize(
        "status",
        [
            ubble_schemas.UbbleIdentificationStatus.INCONCLUSIVE,
            ubble_schemas.UbbleIdentificationStatus.REFUSED,
        ],
    )
    def test_ubble_update_cancelled(self, requests_mock, status):
        user = users_factories.UserFactory()
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
            thirdPartyId="idv_qwerty1234",
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(status=status.value, response_codes=[], documents=[]),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        assert fraud_check.status == subscription_models.FraudCheckStatus.CANCELED

    @patch("pcapi.core.subscription.ubble.tasks.store_id_pictures_task.delay")
    def test_concurrent_requests_leave_fraud_check_ok(self, store_id_pictures_task_mock, requests_mock):
        user = users_factories.UserFactory(
            age=18,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        ProfileCompletionFraudCheckFactory(user=user)
        BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            user=user,
            status=subscription_models.FraudCheckStatus.OK,
        )
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
            thirdPartyId=UBBLE_IDENTIFICATION_V2_RESPONSE["id"],
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(
                age_at_registration=18, created_on=date_utils.get_naive_utc_now()
            ),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)
        ubble_subscription_api.update_ubble_workflow(fraud_check)

        assert fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert user.has_beneficiary_role is True

    @patch("pcapi.core.subscription.ubble.tasks.store_id_pictures_task.delay")
    def test_ubble_workflow_updates_birth_date(self, store_id_pictures_task_mock, requests_mock):
        sixteen_years_ago = date_utils.get_naive_utc_now() - relativedelta(years=16, months=1)
        user = users_factories.UserFactory(dateOfBirth=sixteen_years_ago)
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            user=user,
            thirdPartyId="idv_qwerty1234",
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        seventeen_years_ago = datetime.date.today() - relativedelta(years=17, months=1)
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(birth_date=seventeen_years_ago),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        assert user.dateOfBirth == sixteen_years_ago
        assert user.validatedBirthDate == seventeen_years_ago

    @patch("pcapi.core.subscription.ubble.tasks.store_id_pictures_task.delay")
    @pytest.mark.features(ENABLE_PHONE_VALIDATION=False)
    def test_ubble_workflow_updates_birth_date_on_eligibility_upgrade(self, store_id_pictures_task_mock, requests_mock):
        last_year = date_utils.get_naive_utc_now() - relativedelta(years=1)
        with time_machine.travel(last_year):
            user = users_factories.BeneficiaryFactory(
                age=17,
                beneficiaryFraudChecks__type=subscription_models.FraudCheckType.EDUCONNECT,
                phoneNumber="0123456789",
            )
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            user=user,
            thirdPartyId="idv_qwerty1234",
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        registration_date = datetime.datetime.strptime(UBBLE_IDENTIFICATION_V2_RESPONSE["created_on"], DATE_ISO_FORMAT)
        eighteen_years_and_a_month_ago = registration_date - relativedelta(years=18, months=1)
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(birth_date=eighteen_years_and_a_month_ago.date()),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        assert user.validatedBirthDate == eighteen_years_and_a_month_ago.date()
        assert user.has_beneficiary_role

    @patch("pcapi.core.subscription.ubble.tasks.store_id_pictures_task.delay")
    def test_ubble_workflow_with_eligibility_change_17_18(self, store_id_pictures_task_mock, requests_mock):
        seventeen_years_ago = date_utils.get_naive_utc_now() - relativedelta(years=17, months=1)
        user = users_factories.UserFactory(dateOfBirth=seventeen_years_ago)
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            user=user,
            thirdPartyId=UBBLE_IDENTIFICATION_V2_RESPONSE["id"],
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        original_third_party_id = fraud_check.thirdPartyId

        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(age_at_registration=18),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        canceled_fraud_check, ok_fraud_check = sorted(user.beneficiaryFraudChecks, key=lambda fc: fc.id)
        assert canceled_fraud_check.type == subscription_models.FraudCheckType.UBBLE
        assert canceled_fraud_check.status == subscription_models.FraudCheckStatus.CANCELED
        assert canceled_fraud_check.eligibilityType == users_models.EligibilityType.UNDERAGE
        assert canceled_fraud_check.thirdPartyId != original_third_party_id
        assert subscription_models.FraudReasonCode.ELIGIBILITY_CHANGED in canceled_fraud_check.reasonCodes

        assert ok_fraud_check.type == subscription_models.FraudCheckType.UBBLE
        assert ok_fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert ok_fraud_check.eligibilityType == users_models.EligibilityType.AGE18
        assert ok_fraud_check.thirdPartyId == original_third_party_id

    def test_ubble_workflow_with_eligibility_change_18_19(self, requests_mock):
        eighteen_years_ago = date_utils.get_naive_utc_now() - relativedelta(years=18, months=1)
        user = users_factories.UserFactory(dateOfBirth=eighteen_years_ago)
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            user=user,
            thirdPartyId="idv_qwerty1234",
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        nineteen_years_ago = datetime.date.today() - relativedelta(years=19, months=1)
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(
                birth_date=nineteen_years_ago, created_on=date_utils.get_naive_utc_now()
            ),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        (ko_fraud_check,) = user.beneficiaryFraudChecks
        assert ko_fraud_check.type == subscription_models.FraudCheckType.UBBLE
        assert ko_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert ko_fraud_check.eligibilityType == users_models.EligibilityType.AGE18
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.AGE_TOO_OLD]

    @patch("pcapi.core.subscription.ubble.tasks.store_id_pictures_task.delay")
    def test_ubble_workflow_with_eligibility_change_with_first_attempt_at_18(
        self, store_id_pictures_task_mock, requests_mock
    ):
        nineteen_years_ago = datetime.date.today() - relativedelta(years=19, months=1)
        user = users_factories.UserFactory(dateOfBirth=nineteen_years_ago)
        year_when_user_was_eighteen = date_utils.get_naive_utc_now() - relativedelta(years=1)
        BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.KO,
            user=user,
            thirdPartyId="idv_qwerty1234",
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=year_when_user_was_eighteen,
        )
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            user=user,
            thirdPartyId="idv_qwerty1234",
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=date_utils.get_naive_utc_now(),
        )
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(
                age_at_registration=19, created_on=date_utils.get_naive_utc_now() - relativedelta(months=2)
            ),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        (_ko_fraud_check, ok_fraud_check) = sorted(user.beneficiaryFraudChecks, key=lambda fc: fc.id)
        assert ok_fraud_check.type == subscription_models.FraudCheckType.UBBLE
        assert ok_fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert ok_fraud_check.eligibilityType == users_models.EligibilityType.AGE18

    def test_ubble_workflow_with_eligibility_change_at_21_with_first_attempt_at_18(self, requests_mock):
        twenty_one_years_ago = datetime.date.today() - relativedelta(years=21, months=1)
        user = users_factories.UserFactory(dateOfBirth=twenty_one_years_ago)
        year_when_user_was_eighteen = date_utils.get_naive_utc_now() - relativedelta(years=3)
        BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.KO,
            user=user,
            thirdPartyId="idv_qwerty1234",
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=year_when_user_was_eighteen,
        )
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            user=user,
            thirdPartyId="idv_qwerty1234",
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=date_utils.get_naive_utc_now(),
        )
        requests_mock.get(
            f"{settings.UBBLE_API_URL}/v2/identity-verifications/{fraud_check.thirdPartyId}",
            json=build_ubble_identification_v2_response(age_at_registration=21),
        )

        ubble_subscription_api.update_ubble_workflow(fraud_check)

        (_first_ko_fraud_check, ko_fraud_check) = sorted(user.beneficiaryFraudChecks, key=lambda fc: fc.id)
        assert ko_fraud_check.type == subscription_models.FraudCheckType.UBBLE
        assert ko_fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert ko_fraud_check.eligibilityType == users_models.EligibilityType.AGE18
        assert ko_fraud_check.reason == "L'utilisateur a dépassé l'âge maximum (21 ans)"
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.AGE_TOO_OLD]


IDENTIFICATION_STATE_PARAMETERS = [
    (
        IdentificationState.INITIATED,
        ubble_schemas.UbbleIdentificationStatus.INITIATED,
        subscription_models.FraudCheckStatus.PENDING,
    ),
    (
        IdentificationState.PROCESSING,
        ubble_schemas.UbbleIdentificationStatus.PROCESSING,
        subscription_models.FraudCheckStatus.PENDING,
    ),
    (
        IdentificationState.VALID,
        ubble_schemas.UbbleIdentificationStatus.PROCESSED,
        subscription_models.FraudCheckStatus.OK,
    ),
    (
        IdentificationState.INVALID,
        ubble_schemas.UbbleIdentificationStatus.PROCESSED,
        subscription_models.FraudCheckStatus.KO,
    ),
    (
        IdentificationState.UNPROCESSABLE,
        ubble_schemas.UbbleIdentificationStatus.PROCESSED,
        subscription_models.FraudCheckStatus.SUSPICIOUS,
    ),
    (
        IdentificationState.ABORTED,
        ubble_schemas.UbbleIdentificationStatus.ABORTED,
        subscription_models.FraudCheckStatus.CANCELED,
    ),
]


@pytest.mark.usefixtures("db_session")
class UbbleWorkflowV1Test:
    @pytest.mark.parametrize("state, status, fraud_check_status", IDENTIFICATION_STATE_PARAMETERS)
    @patch("pcapi.core.subscription.ubble.tasks.store_id_pictures_task.delay")
    def test_update_ubble_workflow(self, store_id_pictures_task_mock, ubble_mocker, state, status, fraud_check_status):
        user = users_factories.UserFactory()
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        ubble_response = UbbleIdentificationResponseFactory(identification_state=state)
        assert user.married_name is None

        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        ubble_content = fraud_check.resultContent
        assert ubble_content["status"] == status.value
        assert fraud_check.status == fraud_check_status

    @pytest.mark.parametrize("state, status, fraud_check_status", IDENTIFICATION_STATE_PARAMETERS)
    @patch("pcapi.core.subscription.ubble.tasks.store_id_pictures_task.delay")
    def test_update_ubble_workflow_with_v2_feature_flag(
        self, store_id_pictures_task_mock, ubble_mocker, state, status, fraud_check_status
    ):
        user = users_factories.UserFactory()
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        ubble_response = UbbleIdentificationResponseFactory(identification_state=state)
        assert user.married_name is None

        with ubble_mocker(
            fraud_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        ubble_content = fraud_check.resultContent
        assert ubble_content["status"] == status.value
        assert fraud_check.status == fraud_check_status

    @patch("pcapi.core.subscription.ubble.tasks.store_id_pictures_task.delay")
    def test_concurrent_requests_leave_fraud_check_ok(self, store_id_pictures_task_mock, ubble_mocker):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        ProfileCompletionFraudCheckFactory(user=user)
        BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            user=user,
            status=subscription_models.FraudCheckStatus.OK,
        )
        ubble_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID, data__attributes__identification_id=ubble_check.thirdPartyId
        )

        with ubble_mocker(
            ubble_check.thirdPartyId,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            with atomic():
                ubble_subscription_api.update_ubble_workflow(ubble_check)
            with atomic():
                ubble_subscription_api.update_ubble_workflow(ubble_check)

        assert ubble_check.status == subscription_models.FraudCheckStatus.OK
        assert user.has_beneficiary_role is True

    @time_machine.travel("2020-05-05")
    @patch("pcapi.core.subscription.ubble.tasks.store_id_pictures_task.delay")
    def test_ubble_workflow_with_eligibility_change_17_18(self, store_id_pictures_task_mock, ubble_mocker):
        signup_birth_date = datetime.datetime(year=2002, month=5, day=6)
        user = users_factories.UserFactory(dateOfBirth=signup_birth_date)
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        ubble_identification = fraud_check.thirdPartyId

        # Receiving a response from the UBBLE service, saying the user is 18 years old
        document_birth_date = datetime.datetime(year=2002, month=5, day=4)
        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID,
            data__attributes__identification_id=str(ubble_identification),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=document_birth_date.date().isoformat(),
                ),
            ],
        )
        with (
            ubble_mocker(
                ubble_identification,
                json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
            ),
            atomic(),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        fraud_checks = sorted(user.beneficiaryFraudChecks, key=lambda fc: fc.id)

        assert len(fraud_checks) == 2
        assert fraud_checks[0].type == subscription_models.FraudCheckType.UBBLE
        assert fraud_checks[0].status == subscription_models.FraudCheckStatus.CANCELED
        assert fraud_checks[0].eligibilityType == users_models.EligibilityType.UNDERAGE
        assert fraud_checks[0].thirdPartyId != ubble_identification
        assert subscription_models.FraudReasonCode.ELIGIBILITY_CHANGED in fraud_checks[0].reasonCodes

        assert fraud_checks[1].type == subscription_models.FraudCheckType.UBBLE
        assert fraud_checks[1].status == subscription_models.FraudCheckStatus.OK
        assert fraud_checks[1].eligibilityType == users_models.EligibilityType.AGE18
        assert fraud_checks[1].thirdPartyId == ubble_identification

        db.session.refresh(user)
        assert user.dateOfBirth == signup_birth_date
        assert user.validatedBirthDate == document_birth_date.date()

    @time_machine.travel("2020-05-05")
    def test_ubble_workflow_with_eligibility_change_18_19(self, ubble_mocker):
        signup_birth_date = datetime.datetime(year=2003, month=5, day=4)
        user = users_factories.UserFactory(dateOfBirth=signup_birth_date)
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        ubble_identification = fraud_check.thirdPartyId

        # Receiving a response from the UBBLE service, saying the user is 19 years old
        document_birth_date = datetime.datetime(year=2001, month=5, day=4)
        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID,
            data__attributes__identification_id=str(ubble_identification),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=document_birth_date.date().isoformat()
                ),
            ],
        )
        with ubble_mocker(
            ubble_identification,
            json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        fraud_checks = user.beneficiaryFraudChecks
        assert len(fraud_checks) == 1

        assert fraud_checks[0].type == subscription_models.FraudCheckType.UBBLE
        assert fraud_checks[0].status == subscription_models.FraudCheckStatus.KO
        assert fraud_checks[0].eligibilityType == users_models.EligibilityType.AGE18
        assert fraud_checks[0].thirdPartyId == ubble_identification
        assert subscription_models.FraudReasonCode.AGE_TOO_OLD in fraud_checks[0].reasonCodes

        assert user.dateOfBirth == signup_birth_date
        assert user.validatedBirthDate == document_birth_date.date()

    def test_ubble_workflow_updates_user_when_processed(self, ubble_mocker):
        signup_birth_date = datetime.datetime(year=2002, month=5, day=6)
        user = users_factories.UserFactory(dateOfBirth=signup_birth_date)
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        document_birth_date = datetime.datetime(year=2002, month=5, day=4)
        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.INVALID,
            data__attributes__identification_id=str(fraud_check.thirdPartyId),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=document_birth_date.date().isoformat()
                ),
            ],
        )

        with (
            ubble_mocker(
                fraud_check.thirdPartyId,
                json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
            ),
            atomic(),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        db.session.refresh(user)
        assert user.dateOfBirth == signup_birth_date
        assert user.validatedBirthDate == document_birth_date.date()

    def test_ubble_workflow_updates_user_birth_date_when_already_beneficiary(self, ubble_mocker):
        with time_machine.travel(date_utils.get_naive_utc_now() - relativedelta(years=1)):
            user = users_factories.BeneficiaryFactory(
                age=17,
                beneficiaryFraudChecks__type=subscription_models.FraudCheckType.EDUCONNECT,
            )
            assert user.validatedBirthDate
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        document_birth_date = user.dateOfBirth - relativedelta(days=5)
        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.INVALID,
            data__attributes__identification_id=str(fraud_check.thirdPartyId),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=document_birth_date.date().isoformat()
                ),
            ],
        )

        with (
            ubble_mocker(
                fraud_check.thirdPartyId,
                json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
            ),
            atomic(),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        db.session.refresh(user)
        assert user.validatedBirthDate == document_birth_date.date()

    def test_ubble_workflow_does_not_erase_user_data(self, ubble_mocker):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2002, month=5, day=6))
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.INVALID,
            data__attributes__identification_id=str(fraud_check.thirdPartyId),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(attributes__birth_date=None),
            ],
        )

        with (
            ubble_mocker(
                fraud_check.thirdPartyId,
                json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
            ),
            atomic(),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        db.session.refresh(user)
        assert user.dateOfBirth == datetime.datetime(year=2002, month=5, day=6)

    @time_machine.travel("2019-05-05")
    @patch("pcapi.core.subscription.ubble.tasks.store_id_pictures_task.delay")
    def test_ubble_workflow_started_at_19_with_previous_attempt_at_18(
        self, store_id_pictures_task_mock, ubble_mocker, db_session
    ):
        # Given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2000, month=5, day=1))
        # User started a ubble workflow at 18 years old and was rejected
        BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.KO,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=datetime.datetime(year=2018, month=5, day=4),
        )
        # User started a new ubble workflow at 19 years old
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=datetime.datetime(year=2019, month=5, day=4),
        )

        # When
        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID,
            data__attributes__identification_id=str(fraud_check.thirdPartyId),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=datetime.datetime(year=2000, month=5, day=1).date().isoformat()
                ),
            ],
        )

        with (
            ubble_mocker(
                fraud_check.thirdPartyId,
                json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
            ),
            atomic(),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        db.session.refresh(fraud_check)

        assert fraud_check.type == subscription_models.FraudCheckType.UBBLE
        assert fraud_check.status == subscription_models.FraudCheckStatus.OK
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18
        assert fraud_check.thirdPartyId == fraud_check.thirdPartyId

    @time_machine.travel("2020-05-05")
    def test_ubble_workflow_started_at_21_with_previous_attempt_at_18(self, ubble_mocker, db_session):
        # Given
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime(year=2000, month=5, day=1))
        # User started a ubble workflow at 18 years old and was rejected
        BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.KO,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=datetime.datetime(year=2018, month=5, day=4),
        )
        # User started a new ubble workflow at 21 years old
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            dateCreated=datetime.datetime(year=2021, month=5, day=4),
        )

        # When
        ubble_response = UbbleIdentificationResponseFactory(
            identification_state=IdentificationState.VALID,
            data__attributes__identification_id=str(fraud_check.thirdPartyId),
            included=[
                UbbleIdentificationIncludedDocumentsFactory(
                    attributes__birth_date=datetime.datetime(year=1999, month=5, day=1).date().isoformat()
                ),
            ],
        )

        with (
            ubble_mocker(
                fraud_check.thirdPartyId,
                json.dumps(ubble_response.dict(by_alias=True), sort_keys=True, default=json_default),
            ),
            atomic(),
        ):
            ubble_subscription_api.update_ubble_workflow(fraud_check)

        db.session.refresh(fraud_check)

        assert fraud_check.type == subscription_models.FraudCheckType.UBBLE
        assert fraud_check.status == subscription_models.FraudCheckStatus.KO
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE18
        assert fraud_check.thirdPartyId == fraud_check.thirdPartyId
        assert fraud_check.reason == "L'utilisateur a dépassé l'âge maximum (21 ans)"
        assert fraud_check.reasonCodes == [subscription_models.FraudReasonCode.AGE_TOO_OLD]


@pytest.mark.usefixtures("db_session")
class HandleValidationErrorsTest:
    @pytest.mark.parametrize("reason_code", ubble_constants.REASON_CODE_REQUIRING_IMMEDIATE_NOTIFICATION_REMINDER)
    def should_send_push_notification(self, reason_code):
        user: users_models.User = users_factories.ProfileCompletedUserFactory(age=18)
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            user=user,
            reasonCodes=[reason_code],
        )

        ubble_subscription_api.handle_validation_errors(user, fraud_check)

        assert push_testing.requests[0] == {
            "can_be_asynchronously_retried": True,
            "user_id": user.id,
            "event_name": trigger_events.BatchEvent.HAS_UBBLE_KO_STATUS.value,
            "event_payload": {"error_code": reason_code.value},
        }


class DownloadUbbleDocumentPictureTest:
    picture_path = "https://storage.ubble.ai/FRA-I4-Front-1640326309790.png"
    ubble_content = ubble_schemas.UbbleContent(signed_image_front_url=picture_path, signed_image_back_url=None)
    fraud_check = subscription_models.BeneficiaryFraudCheck(userId=123, thirdPartyId="abcd")

    def test_download_ubble_document_pictures_with_expired_request(self, requests_mock, caplog):
        # Given
        requests_mock.register_uri(
            "GET",
            self.picture_path,
            status_code=403,
            body="""<?xml version="1.0" encoding="UTF-8"?>
                <Error>
                    <Code>AccessDenied</Code>
                    <Message>Request has expired</Message>
                </Error>""",
        )

        # When
        with pytest.raises(requests_utils.ExternalAPIException) as exc_info:
            ubble_subscription_api._download_and_store_ubble_picture(self.fraud_check, self.picture_path, "front")

        # Then
        assert exc_info.value.is_retryable is False

        record = caplog.records[0]
        assert record.levelname == "ERROR"
        assert record.message == "Ubble picture-download: request has expired"
        assert self.picture_path in record.extra["url"]

    def test_download_ubble_document_pictures_with_empty_file(self, requests_mock, caplog):
        # Given
        empty_file = BytesIO()

        requests_mock.register_uri(
            "GET", self.picture_path, status_code=200, headers={"content-type": "image/png"}, body=empty_file
        )

        with pytest.raises(ubble_exceptions.UbbleDownloadedFileEmpty):
            ubble_subscription_api._download_and_store_ubble_picture(self.fraud_check, self.picture_path, "front")

        # Then
        record = caplog.records[0]
        assert "Ubble picture-download: downloaded file is empty" in record.message
        assert self.picture_path in record.extra["url"]

    def test_download_ubble_document_pictures_with_unknown_error(self, requests_mock, caplog):
        # Given
        requests_mock.register_uri("GET", self.picture_path, status_code=503)

        # When
        with pytest.raises(requests_utils.ExternalAPIException) as exc_info:
            ubble_subscription_api._download_and_store_ubble_picture(self.fraud_check, self.picture_path, "front")

        # Then
        assert exc_info.value.is_retryable is True

        record = caplog.records[0]
        assert "Ubble picture-download: external error" in record.message
        assert self.picture_path in record.extra["url"]
        assert record.extra["status_code"] == 503

    @patch("botocore.session.Session.create_client")
    def test_download_ubble_document_pictures_successfully(self, mocked_storage_client, requests_mock):
        # Given
        with open(f"{IMAGES_DIR}/carte_identite_front.png", "rb") as img:
            identity_file_picture = BytesIO(img.read())

        requests_mock.register_uri(
            "GET", self.picture_path, status_code=200, headers={"content-type": "image/png"}, body=identity_file_picture
        )

        # When
        ubble_subscription_api._download_and_store_ubble_picture(self.fraud_check, self.picture_path, "front")

        assert mocked_storage_client.return_value.upload_file.call_count == 1


@pytest.mark.usefixtures("db_session")
class ArchiveUbbleUserIdPicturesTest:
    front_picture_url = "https://storage.ubble.ai/front-picture.png?response-content-type=image%2Fpng"
    back_picture_url = "https://storage.ubble.ai/back-picture.png?response-content-type=image%2Fpng"

    def test_archive_ubble_user_id_pictures_with_unknown_fraud_check(self):
        # Given
        unknown_fraud_check_id = "unknown_fraud_check_id"

        # When
        with pytest.raises(BeneficiaryFraudCheckMissingException) as error:
            ubble_subscription_api.archive_ubble_user_id_pictures(unknown_fraud_check_id)

        # Then
        assert f"No validated Identity fraudCheck found with identification_id {unknown_fraud_check_id}" in str(
            error.value
        )

    def test_archive_ubble_user_id_pictures_fraud_check_is_not_ok(self, ubble_mocker, requests_mock):
        # Given
        fraud_check = BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.KO, type=subscription_models.FraudCheckType.UBBLE
        )

        # When
        with pytest.raises(IncompatibleFraudCheckStatus) as error:
            ubble_subscription_api.archive_ubble_user_id_pictures(fraud_check.thirdPartyId)

        # Then
        assert (
            f"Fraud check status FraudCheckStatus.KO is incompatible with pictures archives for identification_id {fraud_check.thirdPartyId}"
            in str(error.value)
        )

    @patch("pcapi.core.subscription.ubble.tasks.store_id_pictures_task.delay")
    def test_archive_ubble_user_id_pictures_no_file_saved(self, store_id_pictures_task_mock, requests_mock):
        # Given
        fraud_check = BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.UBBLE,
            resultContent=UbbleContentFactory(
                status=ubble_schemas.UbbleIdentificationStatus.PENDING,
                signed_image_front_url=self.front_picture_url,
                signed_image_back_url=self.back_picture_url,
            ),
            idPicturesStored=False,
        )

        requests_mock.register_uri("GET", self.front_picture_url, status_code=403)
        requests_mock.register_uri("GET", self.back_picture_url, status_code=403)

        # When
        with pytest.raises(requests_utils.ExternalAPIException) as exc_info:
            ubble_subscription_api.archive_ubble_user_id_pictures(fraud_check.thirdPartyId)

        # Then
        assert exc_info.value.is_retryable is False
        assert fraud_check.idPicturesStored is False

    @patch("botocore.session.Session.create_client")
    def test_archive_ubble_user_id_pictures_only_front_saved(self, mocked_storage_client, requests_mock):
        # Given
        fraud_check = BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.UBBLE,
            resultContent=UbbleContentFactory(
                status=ubble_schemas.UbbleIdentificationStatus.PENDING,
                signed_image_front_url=self.front_picture_url,
                signed_image_back_url=self.back_picture_url,
            ),
            idPicturesStored=False,
        )

        with open(f"{IMAGES_DIR}/carte_identite_front.png", "rb") as img:
            identity_file_picture_front = BytesIO(img.read())

        requests_mock.register_uri(
            "GET",
            self.front_picture_url,
            status_code=200,
            headers={"content-type": "image/png"},
            body=identity_file_picture_front,
        )
        requests_mock.register_uri("GET", self.back_picture_url, status_code=503)

        # When
        with pytest.raises(requests_utils.ExternalAPIException) as exc_info:
            ubble_subscription_api.archive_ubble_user_id_pictures(fraud_check.thirdPartyId)

        # Then
        assert exc_info.value.is_retryable is True
        assert fraud_check.idPicturesStored is False
        assert mocked_storage_client.return_value.upload_file.call_count == 1

    @patch("botocore.session.Session.create_client")
    def test_archive_ubble_user_id_pictures_both_files_saved(self, mocked_storage_client, requests_mock):
        # Given
        fraud_check = BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.UBBLE,
            resultContent=UbbleContentFactory(
                status=ubble_schemas.UbbleIdentificationStatus.PENDING,
                signed_image_front_url=self.front_picture_url,
                signed_image_back_url=self.back_picture_url,
            ),
        )

        with open(f"{IMAGES_DIR}/carte_identite_front.png", "rb") as img_front:
            identity_file_picture_front = BytesIO(img_front.read())
        with open(f"{IMAGES_DIR}/carte_identite_back.png", "rb") as img_back:
            identity_file_picture_back = BytesIO(img_back.read())

        requests_mock.register_uri(
            "GET",
            self.front_picture_url,
            status_code=200,
            headers={"content-type": "image/png"},
            body=identity_file_picture_front,
        )
        requests_mock.register_uri(
            "GET",
            self.back_picture_url,
            status_code=200,
            headers={"content-type": "image/png"},
            body=identity_file_picture_back,
        )

        # When
        ubble_subscription_api.archive_ubble_user_id_pictures(fraud_check.thirdPartyId)

        # Then
        assert fraud_check.idPicturesStored
        assert mocked_storage_client.return_value.upload_file.call_count == 2

    @patch("botocore.session.Session.create_client")
    def test_archive_ubble_user_id_pictures_all_expected_files_saved(self, mocked_storage_client, requests_mock):
        # Given
        fraud_check = BeneficiaryFraudCheckFactory(
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.UBBLE,
            resultContent=UbbleContentFactory(
                status=ubble_schemas.UbbleIdentificationStatus.PENDING,
                signed_image_front_url=self.front_picture_url,
            ),
        )

        with open(f"{IMAGES_DIR}/carte_identite_front.png", "rb") as img_front:
            identity_file_picture_front = BytesIO(img_front.read())

        requests_mock.register_uri(
            "GET",
            self.front_picture_url,
            status_code=200,
            headers={"content-type": "image/png"},
            body=identity_file_picture_front,
        )

        expected_id_pictures_stored = True

        # When
        ubble_subscription_api.archive_ubble_user_id_pictures(fraud_check.thirdPartyId)

        # Then
        assert fraud_check.idPicturesStored is expected_id_pictures_stored
        assert mocked_storage_client.return_value.upload_file.call_count == 1


@pytest.mark.usefixtures("db_session")
class SubscriptionMessageTest:
    def test_started(self):
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE, status=subscription_models.FraudCheckStatus.STARTED
        )
        assert ubble_subscription_api.get_ubble_subscription_message(fraud_check) is None

    def test_pending(self):
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            updatedAt=datetime.datetime(2021, 1, 1),
        )
        assert ubble_subscription_api.get_ubble_subscription_message(
            fraud_check
        ) == subscription_schemas.SubscriptionMessage(
            user_message="Ton document d'identité est en cours de vérification.",
            call_to_action=None,
            pop_over_icon=subscription_schemas.PopOverIcon.CLOCK,
            updated_at=datetime.datetime(2021, 1, 1),
        )

    def test_ok(self):
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE, status=subscription_models.FraudCheckStatus.OK
        )
        assert ubble_subscription_api.get_ubble_subscription_message(fraud_check) is None

    @pytest.mark.parametrize(
        "reason_code",
        [
            subscription_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER,
            subscription_models.FraudReasonCode.ID_CHECK_EXPIRED,
            subscription_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
            subscription_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
            subscription_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
            subscription_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
            subscription_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,
            subscription_models.FraudReasonCode.LACK_OF_LUMINOSITY,
            subscription_models.FraudReasonCode.MISSING_REQUIRED_DATA,
            subscription_models.FraudReasonCode.DOCUMENT_DAMAGED,
            subscription_models.FraudReasonCode.NOT_DOCUMENT_OWNER,
            subscription_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,
        ],
    )
    def test_retryable(self, reason_code):
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[reason_code],
        )

        assert ubble_subscription_api.get_ubble_subscription_message(
            fraud_check
        ) == subscription_schemas.SubscriptionMessage(
            user_message=ubble_errors.UBBLE_CODE_ERROR_MAPPING[reason_code].retryable_user_message,
            message_summary=ubble_errors.UBBLE_CODE_ERROR_MAPPING[reason_code].retryable_message_summary,
            action_hint=ubble_errors.UBBLE_CODE_ERROR_MAPPING[reason_code].retryable_action_hint,
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Réessayer la vérification de mon identité",
                link=f"{settings.WEBAPP_V2_URL}/verification-identite",
                icon=subscription_schemas.CallToActionIcon.RETRY,
            ),
            pop_over_icon=None,
            updated_at=fraud_check.updatedAt,
        )

    def test_duplicate_beneficiary_ask_support(self):
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.DUPLICATE_USER],
        )
        assert ubble_subscription_api.get_ubble_subscription_message(
            fraud_check
        ) == subscription_schemas.SubscriptionMessage(
            user_message=(
                "Ton dossier a été refusé car il y a déjà un compte bénéficiaire à ton nom. "
                "Contacte le support si tu penses qu’il s’agit d’une erreur. "
                "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."
            ),
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Contacter le support",
                link=f"mailto:support@example.com?subject=%23{fraud_check.user.id}+-+Mon+inscription+sur+le+pass+Culture+est+bloqu%C3%A9e",
                icon=subscription_schemas.CallToActionIcon.EMAIL,
            ),
            pop_over_icon=None,
            updated_at=fraud_check.updatedAt,
        )

    def test_not_retryable_ask_support(self):
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.ID_CHECK_DATA_MATCH],
        )
        assert ubble_subscription_api.get_ubble_subscription_message(
            fraud_check
        ) == subscription_schemas.SubscriptionMessage(
            user_message=ubble_errors.UBBLE_CODE_ERROR_MAPPING[
                subscription_models.FraudReasonCode.ID_CHECK_DATA_MATCH
            ].not_retryable_user_message,
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Contacter le support",
                link=f"mailto:support@example.com?subject=%23{fraud_check.user.id}+-+Mon+inscription+sur+le+pass+Culture+est+bloqu%C3%A9e",
                icon=subscription_schemas.CallToActionIcon.EMAIL,
            ),
            pop_over_icon=None,
            updated_at=fraud_check.updatedAt,
        )

    def test_not_retryable_go_dms(self):
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=None,
        )
        assert ubble_subscription_api.get_ubble_subscription_message(
            fraud_check
        ) == subscription_schemas.SubscriptionMessage(
            user_message=ubble_errors.UBBLE_DEFAULT.not_retryable_user_message,
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Accéder au site Démarche Numérique",
                link=f"{settings.WEBAPP_V2_URL}/verification-identite/demarches-simplifiees",
                icon=subscription_schemas.CallToActionIcon.EXTERNAL,
            ),
            pop_over_icon=None,
            updated_at=fraud_check.updatedAt,
        )

    @pytest.mark.parametrize(
        "reason_code",
        [
            subscription_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER,
            subscription_models.FraudReasonCode.ID_CHECK_EXPIRED,
            subscription_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC,
            subscription_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
            subscription_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
            subscription_models.FraudReasonCode.BLURRY_DOCUMENT_VIDEO,
            subscription_models.FraudReasonCode.NETWORK_CONNECTION_ISSUE,
            subscription_models.FraudReasonCode.LACK_OF_LUMINOSITY,
            subscription_models.FraudReasonCode.DOCUMENT_DAMAGED,
            subscription_models.FraudReasonCode.NOT_DOCUMENT_OWNER,
            subscription_models.FraudReasonCode.UBBLE_INTERNAL_ERROR,
        ],
    )
    def test_not_retryable_third_time_go_dms(self, reason_code):
        user = users_factories.UserFactory()
        BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[reason_code],
        )
        BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[reason_code],
        )
        fraud_check = BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[reason_code],
        )

        assert ubble_subscription_api.get_ubble_subscription_message(
            fraud_check
        ) == subscription_schemas.SubscriptionMessage(
            user_message=ubble_errors.UBBLE_CODE_ERROR_MAPPING[reason_code].not_retryable_user_message,
            call_to_action=subscription_schemas.CallToActionMessage(
                title="Accéder au site Démarche Numérique",
                link=f"{settings.WEBAPP_V2_URL}/verification-identite/demarches-simplifiees",
                icon=subscription_schemas.CallToActionIcon.EXTERNAL,
            ),
            pop_over_icon=None,
            updated_at=fraud_check.updatedAt,
        )

    def test_not_eligible(self):
        fraud_check = BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.AGE_TOO_OLD],
            updatedAt=datetime.datetime(2022, 10, 3),
        )
        assert ubble_subscription_api.get_ubble_subscription_message(
            fraud_check
        ) == subscription_schemas.SubscriptionMessage(
            user_message=f"Ton dossier a été refusé{u_nbsp}: tu ne peux pas bénéficier du pass Culture. Il est réservé aux jeunes de 15 à 18 ans.",
            call_to_action=None,
            pop_over_icon=subscription_schemas.PopOverIcon.ERROR,
            updated_at=datetime.datetime(2022, 10, 3),
        )


@pytest.mark.usefixtures("db_session")
@patch("pcapi.core.subscription.ubble.tasks.update_ubble_workflow_task.delay")
def test_pending_and_created_fraud_checks_are_updated(update_ubble_workflow_mock):
    yesterday = datetime.date.today() - relativedelta(hours=13)
    created_fraud_check = BeneficiaryFraudCheckFactory(
        type=FraudCheckType.UBBLE,
        status=FraudCheckStatus.STARTED,
        dateCreated=yesterday,
        updatedAt=yesterday,
    )
    pending_fraud_check = BeneficiaryFraudCheckFactory(
        type=FraudCheckType.UBBLE,
        status=FraudCheckStatus.PENDING,
        dateCreated=yesterday,
        updatedAt=yesterday,
    )

    ubble_subscription_api.recover_pending_ubble_applications()

    update_ubble_workflow_mock.assert_has_calls(
        [
            call(payload={"beneficiary_fraud_check_id": created_fraud_check.id}),
            call(payload={"beneficiary_fraud_check_id": pending_fraud_check.id}),
        ],
        any_order=True,
    )
