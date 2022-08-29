import datetime

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import pytest

from pcapi import settings
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.ubble import models as ubble_fraud_models
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.notifications.push import testing as push_testing
import pcapi.repository as pcapi_repository


pytestmark = pytest.mark.usefixtures("db_session")


class NextStepTest:
    @override_features(ENABLE_PHONE_VALIDATION_IN_STEPPER=False, ENABLE_EDUCONNECT_AUTHENTICATION=False)
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
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }

    @override_features(ENABLE_PHONE_VALIDATION_IN_STEPPER=False, ENABLE_EDUCONNECT_AUTHENTICATION=False)
    def test_next_subscription_test_profile_completion(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
        )

        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(
                risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
            status=fraud_models.FraudCheckStatus.OK,
        )

        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "profile-completion",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
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
            activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
        )
        # User completed profile
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )

        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "maintenance",
            "allowedIdentityCheckMethods": [],
            "maintenancePageType": "with-dms",
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }

    @override_features(ENABLE_PHONE_VALIDATION_IN_STEPPER=False, ENABLE_EDUCONNECT_AUTHENTICATION=False)
    @pytest.mark.parametrize(
        "fraud_check_status,reason_code,ubble_status,next_step,pending_idcheck",
        [
            (
                fraud_models.FraudCheckStatus.STARTED,
                None,
                ubble_fraud_models.UbbleIdentificationStatus.INITIATED,
                "identity-check",
                False,
            ),
            (
                fraud_models.FraudCheckStatus.PENDING,
                None,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSING,
                "honor-statement",
                True,
            ),
            (
                fraud_models.FraudCheckStatus.OK,
                None,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
                "honor-statement",
                False,
            ),
            (
                fraud_models.FraudCheckStatus.KO,
                fraud_models.FraudReasonCode.AGE_TOO_OLD,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
                "honor-statement",
                False,
            ),
            (
                fraud_models.FraudCheckStatus.CANCELED,
                None,
                ubble_fraud_models.UbbleIdentificationStatus.ABORTED,
                "identity-check",
                False,
            ),
            (
                fraud_models.FraudCheckStatus.SUSPICIOUS,
                fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED,
                ubble_fraud_models.UbbleIdentificationStatus.PROCESSED,
                "identity-check",  # User can retry
                False,
            ),
        ],
    )
    @override_features(ENABLE_UBBLE=True)
    def test_next_subscription_test_ubble(
        self, client, fraud_check_status, reason_code, ubble_status, next_step, pending_idcheck
    ):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
            activity="Étudiant",
        )

        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "phone-validation",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }

        # Perform phone validation and user profiling
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(
                risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
            status=fraud_models.FraudCheckStatus.OK,
        )

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "profile-completion",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }

        # Perform profile completion
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "identity-check",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }

        # Perform first id check with Ubble
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_check_status,
            reasonCodes=[reason_code],
            resultContent=fraud_factories.UbbleContentFactory(status=ubble_status),
        )

        # Check next step: only a single non-aborted Ubble identification is allowed
        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": next_step,
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": pending_idcheck,
            "stepperIncludesPhoneValidation": False,
        }

    @override_features(
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
        ENABLE_UBBLE=True,
        ENABLE_PHONE_VALIDATION_IN_STEPPER=False,
        ENABLE_USER_PROFILING=True,
    )
    @pytest.mark.parametrize(
        "underage_fraud_check_status",
        [
            fraud_models.FraudCheckStatus.PENDING,
            fraud_models.FraudCheckStatus.KO,
            fraud_models.FraudCheckStatus.SUSPICIOUS,
            fraud_models.FraudCheckStatus.CANCELED,
            None,
        ],
    )
    def test_underage_not_ok_turned_18(self, client, underage_fraud_check_status):
        # User has already performed id check with Ubble for underage credit (successfully or not), 2 years ago
        with freeze_time(datetime.datetime.utcnow() - relativedelta(years=2)):
            user = users_factories.UserFactory(
                dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
                - relativedelta(years=16, days=5),
                activity="Employé",
            )
            # 15-17: no phone validation, no user profiling

            # Perform profile completion
            fraud_factories.ProfileCompletionFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            # Perform first id check with Ubble
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.UBBLE,
                status=underage_fraud_check_status,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.HONOR_STATEMENT,
                status=fraud_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

        # Now user turned 18, phone and user profiling, profile completion are requested and Ubble identification is requested again
        # Process should not depend on Ubble result performed when underage
        client.with_token(user.email)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "phone-validation",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }

        # Perform phone validation
        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "user-profiling",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }

        # Perform user profiling
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(
                risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
            status=fraud_models.FraudCheckStatus.OK,
        )

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "profile-completion",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }

        # Perform profile completion
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "identity-check",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }

        # Perform id check with Ubble
        ubble_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            resultContent=fraud_factories.UbbleContentFactory(
                status=ubble_fraud_models.UbbleIdentificationStatus.PROCESSING
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "honor-statement",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": True,
            "stepperIncludesPhoneValidation": False,
        }

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": None,
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": True,
            "stepperIncludesPhoneValidation": False,
        }

        # ubble now confirms the status
        ubble_fraud_check.status = fraud_models.FraudCheckStatus.OK
        ubble_fraud_check.resultContent = fraud_factories.UbbleContentFactory(
            status=ubble_fraud_models.UbbleIdentificationStatus.PROCESSED
        )
        pcapi_repository.repository.save(ubble_fraud_check)
        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": None,
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }

    @override_features(
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
        ENABLE_UBBLE=True,
        ENABLE_PHONE_VALIDATION_IN_STEPPER=False,
        ENABLE_USER_PROFILING=True,
    )
    def test_underage_ubble_ok_turned_18(self, client):
        # User has already performed id check with Ubble for underage credit, 2 years ago
        with freeze_time(datetime.datetime.utcnow() - relativedelta(years=2)):
            user = users_factories.UserFactory(
                dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
                - relativedelta(years=16, days=5),
                activity="Employé",
            )
            # 15-17: no phone validation, no user profiling

            # Perform profile completion
            fraud_factories.ProfileCompletionFraudCheckFactory(
                user=user,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            # Perform first id check with Ubble
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.UBBLE,
                status=fraud_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=fraud_models.FraudCheckType.HONOR_STATEMENT,
                status=fraud_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

        user.phoneValidationStatus = users_models.PhoneValidationStatusType.VALIDATED
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(
                risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        client.with_token(user.email)
        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "honor-statement",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }

    @override_features(
        ENABLE_UBBLE_SUBSCRIPTION_LIMITATION=True,
        ALLOW_IDCHECK_UNDERAGE_REGISTRATION=True,
        ENABLE_UBBLE=True,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18=False,
        ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE=False,
        ENABLE_PHONE_VALIDATION_IN_STEPPER=False,
        ENABLE_EDUCONNECT_AUTHENTICATION=False,
    )
    @pytest.mark.parametrize("age", [15, 16, 17, 18])
    def test_ubble_subcription_limited(self, client, age):
        birth_date = datetime.datetime.utcnow() - relativedelta(years=age + 1)
        birth_date += relativedelta(days=settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS - 1)
        # the user has:
        # 1. Email Validated
        # 2. Phone Validated
        # 3. Profile Completed
        # 4. UserProfiling Valid
        user_approching_birthday = users_factories.UserFactory(
            dateOfBirth=birth_date,
            isEmailValidated=True,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Paris",
            firstName="Jean",
            lastName="Neige",
            address="1 rue des prés",
            postalCode="75001",
            activity="Lycéen",
            phoneNumber="+33609080706",
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user_approching_birthday, eligibilityType=user_approching_birthday.eligibility
        )
        user_profiling = fraud_factories.UserProfilingFraudDataFactory(
            risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user_approching_birthday,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            status=fraud_models.FraudCheckStatus.OK,
            resultContent=user_profiling,
        )

        client.with_token(user_approching_birthday.email)
        response = client.get("/native/v1/subscription/next_step")

        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "identity-check",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }

        user_not_eligible_for_ubble = users_factories.UserFactory(
            dateOfBirth=birth_date + relativedelta(days=10),
            isEmailValidated=True,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Paris",
            firstName="Jean",
            lastName="Neige",
            address="1 rue des prés",
            postalCode="75001",
            activity="Lycéen",
            phoneNumber="+33609080706",
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user_not_eligible_for_ubble,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            status=fraud_models.FraudCheckStatus.OK,
            resultContent=user_profiling,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user_not_eligible_for_ubble, eligibilityType=user_not_eligible_for_ubble.eligibility
        )

        client.with_token(user_not_eligible_for_ubble.email)
        response = client.get("/native/v1/subscription/next_step")
        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "maintenance",
            "allowedIdentityCheckMethods": [],
            "maintenancePageType": "without-dms",
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }

    @override_features(ENABLE_UBBLE=True)
    @override_features(ENABLE_PHONE_VALIDATION_IN_STEPPER=False, ENABLE_EDUCONNECT_AUTHENTICATION=False)
    def test_ubble_restart_workflow(self, client):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.datetime.combine(datetime.date.today(), datetime.time(0, 0))
            - relativedelta(years=18, months=5),
            isEmailValidated=True,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Paris",
            firstName="Jean",
            lastName="Neige",
            address="1 rue des prés",
            postalCode="75001",
            activity="Lycéen",
            phoneNumber="+33609080706",
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        user_profiling = fraud_factories.UserProfilingFraudDataFactory(
            risk_rating=fraud_models.UserProfilingRiskRating.TRUSTED
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
            status=fraud_models.FraudCheckStatus.OK,
            resultContent=user_profiling,
        )

        ubble_content = fraud_factories.UbbleContentFactory(
            status=ubble_fraud_models.UbbleIdentificationStatus.INITIATED
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user,
            resultContent=ubble_content,
            status=fraud_models.FraudCheckStatus.STARTED,
        )

        client.with_token(user.email)
        response = client.get("/native/v1/subscription/next_step")
        assert response.status_code == 200
        assert response.json == {
            "nextSubscriptionStep": "identity-check",
            "allowedIdentityCheckMethods": ["ubble"],
            "maintenancePageType": None,
            "hasIdentityCheckPending": False,
            "stepperIncludesPhoneValidation": False,
        }


class UpdateProfileTest:
    @override_features(ENABLE_UBBLE=True)
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

        user = users_models.User.query.get(user.id)
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

    @override_features(ENABLE_UBBLE=True)
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

    @override_features(ENABLE_UBBLE=True)
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

    @override_features(ENABLE_UBBLE=True)
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

    @override_features(ENABLE_UBBLE=True)
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

    @override_features(ENABLE_UBBLE=True)
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
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.USER_PROFILING,
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

        user = users_models.User.query.get(user.id)
        assert user.firstName == "Alexandra"
        assert user.lastName == "Stan"
        assert user.has_beneficiary_role

        assert len(push_testing.requests) == 2
        notification = push_testing.requests[0]
        assert notification["user_id"] == user.id
        assert notification["attribute_values"]["u.is_beneficiary"]
        assert notification["attribute_values"]["u.postal_code"] == "75008"


class ProfileOptionsTypeTest:
    def test_get_profile_options(self, client):
        response = client.get("/native/v1/subscription/profile_options")

        assert response.status_code == 200
        assert response.json == {
            "activities": [
                {
                    "id": "MIDDLE_SCHOOL_STUDENT",
                    "label": "Collégien",
                    "description": None,
                    "associatedSchoolTypesIds": [
                        "PUBLIC_SECONDARY_SCHOOL",
                        "PRIVATE_SECONDARY_SCHOOL",
                        "HOME_OR_REMOTE_SCHOOLING",
                    ],
                },
                {
                    "id": "HIGH_SCHOOL_STUDENT",
                    "label": "Lycéen",
                    "description": None,
                    "associatedSchoolTypesIds": [
                        "PUBLIC_HIGH_SCHOOL",
                        "PRIVATE_HIGH_SCHOOL",
                        "AGRICULTURAL_HIGH_SCHOOL",
                        "MILITARY_HIGH_SCHOOL",
                        "NAVAL_HIGH_SCHOOL",
                        "APPRENTICE_FORMATION_CENTER",
                        "HOME_OR_REMOTE_SCHOOLING",
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
                {"id": "AGRICULTURAL_HIGH_SCHOOL", "description": None, "label": "Lycée agricole"},
                {
                    "id": "APPRENTICE_FORMATION_CENTER",
                    "description": None,
                    "label": "Centre de formation d'apprentis",
                },
                {"id": "MILITARY_HIGH_SCHOOL", "description": None, "label": "Lycée militaire"},
                {
                    "id": "HOME_OR_REMOTE_SCHOOLING",
                    "description": "À domicile, CNED, institut de santé, etc.",
                    "label": "Accompagnement spécialisé",
                },
                {"id": "NAVAL_HIGH_SCHOOL", "description": None, "label": "Lycée maritime"},
                {"id": "PRIVATE_HIGH_SCHOOL", "description": None, "label": "Lycée privé"},
                {"id": "PRIVATE_SECONDARY_SCHOOL", "description": None, "label": "Collège privé"},
                {"id": "PUBLIC_HIGH_SCHOOL", "description": None, "label": "Lycée public"},
                {"id": "PUBLIC_SECONDARY_SCHOOL", "description": None, "label": "Collège public"},
            ],
        }


class HonorStatementTest:
    @pytest.mark.parametrize(
        "age,eligibility_type",
        [
            (15, users_models.EligibilityType.UNDERAGE),
            (16, users_models.EligibilityType.UNDERAGE),
            (17, users_models.EligibilityType.UNDERAGE),
            (18, users_models.EligibilityType.AGE18),
        ],
    )
    def test_create_honor_statement_fraud_check(self, client, age, eligibility_type):
        user = users_factories.UserFactory(dateOfBirth=datetime.datetime.utcnow() - relativedelta(years=age, days=10))

        client.with_token(user.email)

        response = client.post("/native/v1/subscription/honor_statement")

        assert response.status_code == 204

        fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter_by(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT
        ).first()

        assert fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert fraud_check.reason == "statement from /subscription/honor_statement endpoint"
        assert fraud_check.eligibilityType == eligibility_type
