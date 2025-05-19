import datetime

import pytest
import time_machine
from dateutil.relativedelta import relativedelta

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.notifications.push import testing as push_testing
from pcapi.utils.postal_code import INELIGIBLE_POSTAL_CODES


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

        user = db.session.query(users_models.User).get(user.id)
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

        user = db.session.query(users_models.User).get(user.id)
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
