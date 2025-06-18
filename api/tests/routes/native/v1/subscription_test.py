import datetime
from unittest.mock import patch

import pytest
import requests_mock
import time_machine
from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.connectors.serialization import ubble_serializers
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.notifications.push import testing as push_testing
from pcapi.utils import requests
from pcapi.utils.postal_code import INELIGIBLE_POSTAL_CODES

from tests.connectors.beneficiaries.ubble_fixtures import build_ubble_identification_v2_response


pytestmark = pytest.mark.usefixtures("db_session")


class GetProfileTest:
    expected_num_queries = 2  # user + beneficiary_fraud_check

    def test_get_profile(self, client):
        user = users_factories.BeneficiaryGrant18Factory()
        fraud_check = fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )

        client.with_token(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/native/v1/subscription/profile")
            assert response.status_code == 200

        content: fraud_models.ProfileCompletionContent = fraud_check.source_data()
        profile_content = response.json["profile"]

        assert profile_content["firstName"] == content.first_name
        assert profile_content["lastName"] == content.last_name
        assert profile_content["address"] == content.address
        assert profile_content["city"] == content.city
        assert profile_content["postalCode"] == content.postal_code
        assert profile_content["activity"] == content.activity
        assert profile_content["schoolType"] == content.school_type

    def test_get_profile_with_no_fraud_check(self, client):
        user = users_factories.BeneficiaryGrant18Factory()

        client.with_token(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/native/v1/subscription/profile")
            assert response.status_code == 404

    def test_get_profile_with_obsolete_profile_info(self, client):
        user = users_factories.BeneficiaryGrant18Factory()
        content = fraud_factories.ProfileCompletionContentFactory()
        fraud_check = fraud_factories.ProfileCompletionFraudCheckFactory(
            resultContent=content, user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )
        fraud_check.resultContent["activity"] = "NOT_AN_ACTIVITY"

        client.with_token(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/native/v1/subscription/profile")
            assert response.status_code == 200
        assert response.json["profile"] is None

    def test_get_profile_with_two_profile_completions(self, client):
        user = users_factories.BeneficiaryGrant18Factory()
        fraud_check_1 = fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            dateCreated=datetime.datetime.utcnow() - relativedelta(months=1),
        )
        fraud_check_1.resultContent["activity"] = "NOT_AN_ACTIVITY"
        fraud_check_2 = fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.AGE17_18
        )
        fraud_check_2.resultContent["activity"] = "Lycéen"

        client.with_token(user.email)
        with assert_num_queries(self.expected_num_queries):
            response = client.get("/native/v1/subscription/profile")
            assert response.status_code == 200

        profile_content = response.json["profile"]
        assert profile_content is not None
        assert profile_content["activity"] == "Lycéen"

    def test_post_profile_then_get(self, client):
        user = users_factories.EligibleGrant18Factory()
        profile_data = {
            "firstName": "Lucy",
            "lastName": "Ellingson",
            "address": "Chez ma maman",
            "city": "Kennet",
            "postalCode": "77000",
            "activityId": "HIGH_SCHOOL_STUDENT",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        with time_machine.travel(datetime.datetime.utcnow() - datetime.timedelta(days=365)):
            client.with_token(user.email)
            client.post("/native/v1/subscription/profile", profile_data)

        client.with_token(user.email)
        response = client.get("/native/v1/subscription/profile")

        assert response.status_code == 200
        assert response.json["profile"]["firstName"] == profile_data["firstName"]
        assert response.json["profile"]["lastName"] == profile_data["lastName"]
        assert response.json["profile"]["address"] == profile_data["address"]
        assert response.json["profile"]["city"] == profile_data["city"]
        assert response.json["profile"]["postalCode"] == profile_data["postalCode"]
        assert response.json["profile"]["activity"] == users_models.ActivityEnum.HIGH_SCHOOL_STUDENT.value
        assert response.json["profile"]["schoolType"] == users_models.SchoolTypeEnum.PUBLIC_HIGH_SCHOOL.value


class UpdateProfileTest:
    @pytest.mark.features(ENABLE_UBBLE=True)
    def test_fulfill_profile(self, client):
        """
        Test that valid request:
            * updates the user's profile information;
            * send a request to Batch to update the user's information
        """

        user = users_factories.UserFactory(
            address=None,
            city=None,
            postalCode=None,
            activity=None,
            firstName=None,
            lastName=None,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33609080706",
            dateOfBirth=datetime.date.today() - relativedelta(years=18, months=6),
        )

        profile_data = {
            "firstName": "John",
            "lastName": "Doe",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activityId": "HIGH_SCHOOL_STUDENT",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        client.with_token(user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 204

        user = db.session.get(users_models.User, user.id)
        assert not user.is_beneficiary
        assert user.firstName == "John"
        assert user.lastName == "Doe"
        assert user.address == "1 rue des rues"
        assert user.city == "Uneville"
        assert user.postalCode == "77000"
        assert user.activity == "Lycéen"
        assert user.schoolType == users_models.SchoolTypeEnum.PUBLIC_HIGH_SCHOOL
        assert user.phoneNumber == "+33609080706"

        assert len(push_testing.requests) == 2
        notification = push_testing.requests[0]

        assert notification["user_id"] == user.id
        assert not notification["attribute_values"]["u.is_beneficiary"]
        assert notification["attribute_values"]["u.postal_code"] == "77000"

        # Check that a PROFILE_COMPLETION fraud check is created
        profile_completion_fraud_checks = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.PROFILE_COMPLETION
        ]
        assert len(profile_completion_fraud_checks) == 1
        profile_completion_fraud_check = profile_completion_fraud_checks[0]
        assert profile_completion_fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert profile_completion_fraud_check.reason == "Completed in application step"

    @pytest.mark.features(ENABLE_UBBLE=True)
    def test_fulfill_profile_invalid_character(self, client):
        user = users_factories.UserFactory(
            address=None,
            city=None,
            postalCode=None,
            activity=None,
            firstName=None,
            lastName=None,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33609080706",
            dateOfBirth=datetime.date.today() - relativedelta(years=18, months=6),
        )

        profile_data = {
            "firstName": "ჯონ",
            "lastName": "Doe",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activityId": "HIGH_SCHOOL_STUDENT",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        client.with_token(user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 400

    @pytest.mark.features(ENABLE_UBBLE=True)
    def test_fulfill_profile_empty_field(self, client):
        user = users_factories.UserFactory(
            address=None,
            city=None,
            postalCode=None,
            activity=None,
            firstName=None,
            lastName=None,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33609080706",
            dateOfBirth=datetime.date.today() - relativedelta(years=18, months=6),
        )

        profile_data = {
            "firstName": " ",
            "lastName": "Doe",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activityId": "HIGH_SCHOOL_STUDENT",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        client.with_token(user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 400

    @pytest.mark.features(ENABLE_UBBLE=True)
    def test_fulfill_profile_missing_mandatory_field(self, client):
        user = users_factories.UserFactory(
            address=None,
            city=None,
            postalCode=None,
            activity=None,
            firstName=None,
            lastName=None,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33609080706",
            dateOfBirth=datetime.date.today() - relativedelta(years=18, months=6),
        )

        profile_data = {
            "firstName": " ",
            "lastName": "Doe",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        client.with_token(user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 400

    @pytest.mark.parametrize("postal_code", INELIGIBLE_POSTAL_CODES)
    @pytest.mark.features(ENABLE_UBBLE=True)
    def test_fulfill_profile_ineligible_postal_code(self, client, postal_code):
        user = users_factories.UserFactory()

        response = client.with_token(user.email).post(
            "/native/v1/subscription/profile",
            {
                "firstName": "John",
                "lastName": "Doe",
                "address": "1 rue des rues",
                "city": "Uneville",
                "postalCode": postal_code,
                "activityId": "HIGH_SCHOOL_STUDENT",
                "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
            },
        )

        assert response.status_code == 400
        assert response.json["code"] == "INELIGIBLE_POSTAL_CODE"

    @pytest.mark.features(ENABLE_UBBLE=True)
    def test_fulfill_profile_valid_character(self, client):
        user = users_factories.UserFactory(
            address=None,
            city=None,
            postalCode=None,
            activity=None,
            firstName=None,
            lastName=None,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33609080706",
            dateOfBirth=datetime.date.today() - relativedelta(years=18, months=6),
        )

        profile_data = {
            "firstName": "John",
            "lastName": "àâçéèêîôœùûÀÂÇÉÈÊÎÔŒÙÛ-' ",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activityId": "HIGH_SCHOOL_STUDENT",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        client.with_token(user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 204

    @pytest.mark.features(ENABLE_UBBLE=True)
    def test_fulfill_profile_activation(self, client):
        user = users_factories.UserFactory(
            address=None,
            city=None,
            postalCode=None,
            activity=None,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            phoneNumber="+33609080706",
            dateOfBirth=datetime.date.today() - relativedelta(years=18, months=6),
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.DMS,
            resultContent=fraud_factories.DMSContentFactory(
                first_name="Alexandra", last_name="Stan", postal_code="75008"
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        profile_data = {
            "firstName": "John",
            "lastName": "Doe",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activityId": "HIGH_SCHOOL_STUDENT",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
        }

        client.with_token(user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 204

        user = db.session.get(users_models.User, user.id)
        assert user.firstName == "Alexandra"
        assert user.lastName == "Stan"
        assert user.has_beneficiary_role

        assert len(push_testing.requests) == 3
        notification = push_testing.requests[0]
        assert notification["user_id"] == user.id
        assert notification["attribute_values"]["u.is_beneficiary"]
        assert notification["attribute_values"]["u.postal_code"] == "75008"


class ActivityTypesTest:
    @pytest.mark.parametrize("age", (17, 18))
    def test_get_activity_types(self, client, age):
        user = users_factories.BaseUserFactory(age=age)
        client.with_token(user.email)
        with assert_num_queries(2):  # user + free eligibility FF
            response = client.get("/native/v1/subscription/activity_types")
            assert response.status_code == 200

        expected_response = {
            "activities": [
                {
                    "id": "HIGH_SCHOOL_STUDENT",
                    "label": "Lycéen",
                    "description": None,
                },
                {"id": "STUDENT", "label": "Étudiant", "description": None},
                {"id": "EMPLOYEE", "label": "Employé", "description": None},
                {"id": "APPRENTICE", "label": "Apprenti", "description": None},
                {"id": "APPRENTICE_STUDENT", "label": "Alternant", "description": None},
                {
                    "id": "VOLUNTEER",
                    "label": "Volontaire",
                    "description": "En service civique",
                },
                {
                    "id": "INACTIVE",
                    "label": "Inactif",
                    "description": "En incapacité de travailler",
                },
                {
                    "id": "UNEMPLOYED",
                    "label": "Demandeur d'emploi",
                    "description": "En recherche d'emploi",
                },
            ],
        }
        if age < 18:
            expected_response["activities"].insert(
                0,
                {
                    "id": "MIDDLE_SCHOOL_STUDENT",
                    "label": "Collégien",
                    "description": None,
                },
            )
        assert response.json == expected_response


class IdentificationSessionTest:
    def test_request(self, client, requests_mock):
        user = users_factories.ProfileCompletedUserFactory(age=18)
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/create-and-start-idv",
            json=build_ubble_identification_v2_response(status="pending", response_codes=[], documents=[]),
        )

        client.with_token(user.email)
        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 200
        assert len(user.beneficiaryFraudChecks) == 3

        check = next(check for check in user.beneficiaryFraudChecks if check.type == fraud_models.FraudCheckType.UBBLE)
        assert check.type == fraud_models.FraudCheckType.UBBLE
        assert check.status == fraud_models.FraudCheckStatus.STARTED
        assert response.json["identificationUrl"] == "https://verification.ubble.example.com/"

    @pytest.mark.parametrize("age", [14, 19, 20])
    @patch("pcapi.core.subscription.ubble.api.start_ubble_workflow")
    def test_request_not_eligible(self, start_ubble_mock, client, age):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=age, days=5))

        client.with_token(user.email)
        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 400
        assert response.json["code"] == "IDCHECK_NOT_ELIGIBLE"
        start_ubble_mock.assert_not_called()
        assert len(user.beneficiaryFraudChecks) == 0

    def test_request_connection_error(self, client, requests_mock):
        user = users_factories.ProfileCompletedUserFactory(age=18)
        requests_mock.post(f"{settings.UBBLE_API_URL}/v2/create-and-start-idv", exc=requests.exceptions.ConnectionError)

        client.with_token(user.email)
        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 503
        assert response.json["code"] == "IDCHECK_SERVICE_UNAVAILABLE"
        assert (
            db.session.query(fraud_models.BeneficiaryFraudCheck)
            .filter_by(user=user, type=fraud_models.FraudCheckType.UBBLE)
            .count()
            == 0
        )

    def test_request_ubble_http_error_status(self, client, requests_mock):
        user = users_factories.ProfileCompletedUserFactory(age=18)
        requests_mock.post(f"{settings.UBBLE_API_URL}/v2/create-and-start-idv", status_code=404)

        client.with_token(user.email)
        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 500
        assert response.json["code"] == "IDCHECK_SERVICE_ERROR"
        assert (
            db.session.query(fraud_models.BeneficiaryFraudCheck)
            .filter_by(user=user, type=fraud_models.FraudCheckType.UBBLE)
            .count()
            == 0
        )

    @pytest.mark.parametrize(
        "fraud_check_status,ubble_status",
        [
            (fraud_models.FraudCheckStatus.PENDING, ubble_serializers.UbbleIdentificationStatus.PROCESSING),
            (fraud_models.FraudCheckStatus.OK, ubble_serializers.UbbleIdentificationStatus.PROCESSED),
            (fraud_models.FraudCheckStatus.KO, ubble_serializers.UbbleIdentificationStatus.PROCESSED),
        ],
    )
    def test_request_ubble_second_check_blocked(self, client, fraud_check_status, ubble_status):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=18, days=5))
        client.with_token(user.email)

        # Perform phone validation
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED

        # Perform first id check with Ubble
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_check_status,
            resultContent=fraud_factories.UbbleContentFactory(status=ubble_status),
        )

        # Initiate second id check with Ubble
        # It should be blocked - only one identification is allowed
        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 400
        assert response.json["code"] == "IDCHECK_ALREADY_PROCESSED"
        assert len(user.beneficiaryFraudChecks) == 1

    def test_request_ubble_second_check_after_first_aborted(self, client, requests_mock):
        user = users_factories.ProfileCompletedUserFactory(age=18)
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/create-and-start-idv",
            json=build_ubble_identification_v2_response(status="pending", response_codes=[], documents=[]),
        )

        # Perform first id check with Ubble
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.CANCELED,
            resultContent=fraud_factories.UbbleContentFactory(
                status=ubble_serializers.UbbleIdentificationStatus.ABORTED
            ),
        )

        # Initiate second id check with Ubble
        # Accepted because the first one was canceled
        client.with_token(user.email)
        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 200
        assert len(user.beneficiaryFraudChecks) == 4

        sorted_fraud_checks = sorted(user.beneficiaryFraudChecks, key=lambda x: x.id)
        check = sorted_fraud_checks[-1]
        assert check.type == fraud_models.FraudCheckType.UBBLE
        assert response.json["identificationUrl"] == "https://verification.ubble.example.com/"

    @pytest.mark.parametrize(
        "retry_number,expected_status",
        [(1, 200), (2, 200), (3, 400), (4, 400)],
    )
    @pytest.mark.parametrize(
        "reason",
        [
            fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
            fraud_models.FraudReasonCode.ID_CHECK_EXPIRED,
            fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE,
        ],
    )
    def test_request_ubble_retry(self, client, requests_mock, reason, retry_number, expected_status):
        user = users_factories.ProfileCompletedUserFactory(age=18)
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/create-and-start-idv",
            json=build_ubble_identification_v2_response(status="pending", response_codes=[], documents=[]),
        )

        # Perform previous Ubble identifications
        for _ in range(0, retry_number):
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.UBBLE,
                status=fraud_models.FraudCheckStatus.SUSPICIOUS,
                reasonCodes=[reason],
                resultContent=fraud_factories.UbbleContentFactory(
                    status=ubble_serializers.UbbleIdentificationStatus.PROCESSED
                ),
            )

        len_fraud_checks_before = len(user.beneficiaryFraudChecks)

        client.with_token(user.email)
        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == expected_status

        if response.status_code == 200:
            assert len(user.beneficiaryFraudChecks) == len_fraud_checks_before + 1

        if response.status_code == 400:
            assert len(user.beneficiaryFraudChecks) == len_fraud_checks_before

    @pytest.mark.parametrize(
        "reason",
        [
            fraud_models.FraudReasonCode.DUPLICATE_USER,
            fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH,
        ],
    )
    def test_request_ubble_retry_not_allowed(self, client, requests_mock, reason):
        user = users_factories.ProfileCompletedUserFactory(age=18)
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/create-and-start-idv",
            json=build_ubble_identification_v2_response(status="pending", response_codes=[], documents=[]),
        )

        # Perform previous Ubble identification
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[reason],
            resultContent=fraud_factories.UbbleContentFactory(
                status=ubble_serializers.UbbleIdentificationStatus.PROCESSED
            ),
        )

        client.with_token(user.email)
        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 400
        assert len(user.beneficiaryFraudChecks) == 3

    def test_allow_rerun_identification_from_started(self, client, requests_mock):
        user = users_factories.ProfileCompletedUserFactory(age=18)
        expected_url = "https://id.ubble.ai/ef055567-3794-4ca5-afad-dce60fe0f227"
        ubble_content = fraud_factories.UbbleContentFactory(
            status=ubble_serializers.UbbleIdentificationStatus.INITIATED,
            identification_url=expected_url,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.STARTED,
            user=user,
            resultContent=ubble_content,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )
        requests_mock.post(
            f"{settings.UBBLE_API_URL}/v2/create-and-start-idv",
            json=build_ubble_identification_v2_response(status="pending", response_codes=[], documents=[]),
        )

        client.with_token(user.email)
        response = client.post("/native/v1/ubble_identification", json={"redirectUrl": "http://example.com/deeplink"})

        assert response.status_code == 200
        assert len(user.beneficiaryFraudChecks) == 3

        check = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.UBBLE
        ][0]
        assert check
        assert response.json["identificationUrl"] == expected_url

    def test_conflict_error_tries_to_resync(self, client):
        user = users_factories.ProfileCompletedUserFactory(age=18)
        ubble_identification_id = "idv_qwerty1234"
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user,
            thirdPartyId=ubble_identification_id,
            status=fraud_models.FraudCheckStatus.STARTED,
            resultContent=fraud_factories.UbbleContentFactory(
                applicant_id="aplt_01je97fqhmtk2jmn6gcgyram3s",
                identification_id=ubble_identification_id,
                status=ubble_serializers.UbbleIdentificationStatus.PENDING,
            ),
        )
        with requests_mock.Mocker() as requests_mocker:
            # There is a state conflict between Ubble's user and ours
            requests_mocker.post(
                f"{settings.UBBLE_API_URL}/v2/identity-verifications/{ubble_identification_id}/attempts",
                status_code=409,
            )
            # We should try to resync
            requests_mocker.get(
                f"{settings.UBBLE_API_URL}/v2/identity-verifications/{ubble_identification_id}",
                json=build_ubble_identification_v2_response(
                    age_at_registration=18, created_on=datetime.datetime.utcnow()
                ),
            )

            response = client.with_token(user.email).post(
                "/native/v1/ubble_identification", json={"redirectUrl": "https://redirect.example.com"}
            )

        assert response.status_code == 500, response.json
        assert response.json["code"] == "IDCHECK_SERVICE_ERROR", response.json

        db.session.refresh(fraud_check)
        assert fraud_check.status == fraud_models.FraudCheckStatus.OK, fraud_check.reasonCodes


class HonorStatementTest:
    @pytest.mark.parametrize("age", [17, 18])
    def test_create_honor_statement_fraud_check(self, client, age):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=age, days=10))

        client.with_token(user.email)

        response = client.post("/native/v1/subscription/honor_statement")

        assert response.status_code == 204

        fraud_check = (
            db.session.query(fraud_models.BeneficiaryFraudCheck)
            .filter_by(user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT)
            .first()
        )

        assert fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert fraud_check.reason == "statement from /subscription/honor_statement endpoint"
        assert fraud_check.eligibilityType == users_models.EligibilityType.AGE17_18
