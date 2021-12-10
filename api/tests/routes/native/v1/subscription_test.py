import datetime

from dateutil.relativedelta import relativedelta
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.notifications.push import testing as push_testing


pytestmark = pytest.mark.usefixtures("db_session")


class NextStepTest:
    def test_next_subscription_test(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
        )

        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "phone-validation",
            "allowedIdentityCheckMethods": ["jouve"],
            "maintenancePageType": None,
        }

    @override_features(
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
        ALLOW_IDCHECK_UNDERAGE_REGISTRATION=False,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE=True,
    )
    def test_next_subscription_maintenance_page_test(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=15, months=5),
        )

        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "maintenance",
            "allowedIdentityCheckMethods": [],
            "maintenancePageType": "with-dms",
        }

    @pytest.mark.parametrize(
        "fraud_check_status,ubble_status,next_step",
        [
            (
                fraud_models.FraudCheckStatus.PENDING,
                fraud_models.ubble.UbbleIdentificationStatus.INITIATED,
                "honor-statement",
            ),
            (
                fraud_models.FraudCheckStatus.PENDING,
                fraud_models.ubble.UbbleIdentificationStatus.PROCESSING,
                "honor-statement",
            ),
            (
                fraud_models.FraudCheckStatus.OK,
                fraud_models.ubble.UbbleIdentificationStatus.PROCESSED,
                "honor-statement",
            ),
            (
                fraud_models.FraudCheckStatus.KO,
                fraud_models.ubble.UbbleIdentificationStatus.PROCESSED,
                "honor-statement",
            ),
            (
                fraud_models.FraudCheckStatus.CANCELED,
                fraud_models.ubble.UbbleIdentificationStatus.ABORTED,
                "identity-check",
            ),
            (None, fraud_models.ubble.UbbleIdentificationStatus.INITIATED, "honor-statement"),
            (None, fraud_models.ubble.UbbleIdentificationStatus.PROCESSING, "honor-statement"),
            (None, fraud_models.ubble.UbbleIdentificationStatus.PROCESSED, "honor-statement"),
        ],
    )
    @override_features(ENABLE_UBBLE=True)
    def test_next_subscription_test_ubble(self, client, fraud_check_status, ubble_status, next_step):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
        )

        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "phone-validation",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
        }

        # Perform phone validation and user profiling
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(
                risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
            ),
        )

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "identity-check",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
        }

        # Perform first id check with Ubble
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_check_status,
            resultContent=fraud_factories.UbbleContentFactory(status=ubble_status),
        )

        # Check next step: only a single non-aborted Ubble identification is allowed
        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": next_step,
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
        }


class UpdateProfileTest:
    @override_features(ENABLE_UBBLE=True)
    def test_update_profile(self, client):
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

        user = users_models.User.query.get(user.id)
        assert user.firstName == "John"
        assert user.lastName == "Doe"
        assert user.address == "1 rue des rues"
        assert user.city == "Uneville"
        assert user.postalCode == "77000"
        assert user.activity == "Lycéen"
        assert user.schoolType == users_models.SchoolTypeEnum.PUBLIC_HIGH_SCHOOL
        assert user.phoneNumber == "+33609080706"
        assert not user.hasCompletedIdCheck

        assert len(push_testing.requests) == 2
        notification = push_testing.requests[0]

        assert notification["user_id"] == user.id
        assert not notification["attribute_values"]["u.is_beneficiary"]
        assert notification["attribute_values"]["u.postal_code"] == "77000"

    # TODO: CorentinN: Remove this when frontend only sends Enum Keys
    def test_update_profile_backward_compatibility(self, client):
        user = users_factories.UserFactory(
            address=None,
            city=None,
            postalCode=None,
            activity=None,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )

        profile_data = {
            "firstName": "John",
            "lastName": "Doe",
            "address": "1 rue des rues",
            "city": "Uneville",
            "postalCode": "77000",
            "activity": "Lycéen",
        }

        client.with_token(email=user.email)
        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 204

        user = users_models.User.query.get(user.id)
        assert user.firstName != "John"
        assert user.lastName != "Doe"
        assert user.address == "1 rue des rues"
        assert user.city == "Uneville"
        assert user.postalCode == "77000"
        assert user.activity == "Lycéen"

        assert len(push_testing.requests) == 2
        notification = push_testing.requests[0]

        assert notification["user_id"] == user.id
        assert not notification["attribute_values"]["u.is_beneficiary"]
        assert notification["attribute_values"]["u.postal_code"] == "77000"


class SchoolTypeTest:
    def test_get_all_school_types(self, client):
        response = client.get("/native/v1/subscription/school_types")

        assert response.status_code == 200
        assert response.json == {
            "activities": [
                {
                    "id": "MIDDLE_SCHOOL_STUDENT",
                    "label": "Collégien",
                    "description": None,
                    "associatedSchoolTypesIds": [
                        "PRIVATE_SECONDARY_SCHOOL",
                        "PUBLIC_SECONDARY_SCHOOL",
                        "HOME_OR_REMOTE_SCHOOLING",
                    ],
                },
                {
                    "id": "HIGH_SCHOOL_STUDENT",
                    "label": "Lycéen",
                    "description": None,
                    "associatedSchoolTypesIds": [
                        "AGRICULTURAL_HIGH_SCHOOL",
                        "MILITARY_HIGH_SCHOOL",
                        "NAVAL_HIGH_SCHOOL",
                        "PRIVATE_HIGH_SCHOOL",
                        "PUBLIC_HIGH_SCHOOL",
                        "HOME_OR_REMOTE_SCHOOLING",
                        "APPRENTICE_FORMATION_CENTER",
                    ],
                },
                {"id": "STUDENT", "label": "Étudiant", "description": None, "associatedSchoolTypesIds": []},
                {"id": "EMPLOYEE", "label": "Employé", "description": None, "associatedSchoolTypesIds": []},
                {"id": "APPRENTICE", "label": "Apprenti", "description": None, "associatedSchoolTypesIds": []},
                {"id": "APPRENTICE_STUDENT", "label": "Alternant", "description": None, "associatedSchoolTypesIds": []},
                {
                    "id": "VOLUNTEER",
                    "label": "Volontaire",
                    "description": "En service civique",
                    "associatedSchoolTypesIds": [],
                },
                {
                    "id": "INACTIVE",
                    "label": "Inactif",
                    "description": "En incapacité de travailler",
                    "associatedSchoolTypesIds": [],
                },
                {
                    "id": "UNEMPLOYED",
                    "label": "Chômeur",
                    "description": "En recherche d'emploi",
                    "associatedSchoolTypesIds": [],
                },
            ],
            "school_types": [
                {"id": "AGRICULTURAL_HIGH_SCHOOL", "label": "Lycée agricole"},
                {
                    "id": "APPRENTICE_FORMATION_CENTER",
                    "label": "Centre de formation d'apprentis",
                },
                {"id": "MILITARY_HIGH_SCHOOL", "label": "Lycée militaire"},
                {"id": "HOME_OR_REMOTE_SCHOOLING", "label": "À domicile ou au CNED"},
                {"id": "NAVAL_HIGH_SCHOOL", "label": "Lycée maritime"},
                {"id": "PRIVATE_HIGH_SCHOOL", "label": "Lycée privé"},
                {"id": "PRIVATE_SECONDARY_SCHOOL", "label": "Collège privé"},
                {"id": "PUBLIC_HIGH_SCHOOL", "label": "Lycée public"},
                {"id": "PUBLIC_SECONDARY_SCHOOL", "label": "Collège public"},
            ],
        }


class HonorStatementTest:
    def test_create_honor_statement_fraud_check(self, client):
        user = users_factories.UserFactory()

        client.with_token(user.email)

        response = client.post("/native/v1/subscription/honor_statement")

        assert response.status_code == 204

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT
        ).first()

        assert fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert fraud_check.reason == "statement from /subscription/honor_statement endpoint"
        # TODO(viconnex) add eligibility type -- assert fraud_check.eligibilityType == eligibilityType
