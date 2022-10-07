import dataclasses
from datetime import date
from datetime import datetime
import typing
from unittest.mock import MagicMock
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from flask_jwt_extended.utils import create_access_token
from freezegun import freeze_time
import pytest

from pcapi import settings
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import repository as subscription_repository
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import PhoneValidationStatusType


@pytest.mark.usefixtures("db_session")
class EduconnectFlowTest:
    @freeze_time("2021-10-10")
    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_saml_client")
    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=True)
    def test_educonnect_subscription(self, mock_get_educonnect_saml_client, client, app):
        ine_hash = "5ba682c0fc6a05edf07cd8ed0219258f"
        user = users_factories.UserFactory(dateOfBirth=datetime(2004, 1, 1), firstName=None, lastName=None)
        access_token = create_access_token(identity=user.email)
        client.auth_header = {"Authorization": f"Bearer {access_token}"}
        mock_saml_client = MagicMock()
        mock_get_educonnect_saml_client.return_value = mock_saml_client
        mock_saml_client.prepare_for_authenticate.return_value = (
            "request_id_123",
            {"headers": [("Location", "https://pr4.educonnect.phm.education.gouv.fr/idp")]},
        )

        profile_data = {
            "activityId": "HIGH_SCHOOL_STUDENT",
            "schoolTypeId": "PUBLIC_HIGH_SCHOOL",
            "address": "1 rue des rues",
            "city": "Uneville",
            "firstName": "WrongFirstName",
            "lastName": "Wrong Lastname",
            "postalCode": "77000",
        }

        response = client.post("/native/v1/subscription/profile", profile_data)

        assert response.status_code == 204

        assert user.city == "Uneville"
        assert user.activity == "Lycéen"
        assert subscription_api.has_completed_profile_for_given_eligibility(user, user.eligibility)
        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.IDENTITY_CHECK

        # Get educonnect login form with saml protocol
        response = client.get("/saml/educonnect/login")
        assert response.status_code == 302
        assert response.location.startswith("https://pr4.educonnect.phm.education.gouv.fr/idp")

        prefixed_request_id = app.redis_client.keys("educonnect-saml-request-*")[0]
        request_id = prefixed_request_id[len("educonnect-saml-request-") :]

        mock_saml_response = MagicMock()
        mock_saml_client.parse_authn_request_response.return_value = mock_saml_response
        mock_saml_response.get_identity.return_value = {
            "givenName": ["Max"],
            "sn": ["SENS"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.57": [
                "e6759833fb379e0340322889f2a367a5a5150f1533f80dfe963d21e43e33f7164b76cc802766cdd33c6645e1abfd1875"
            ],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.5": ["https://educonnect.education.gouv.fr/Logout"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.67": ["2006-08-18"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.73": ["2212"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.6": ["2021-10-08 11:51:33.437"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.64": [ine_hash],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.7": ["eleve1d"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.72": ["school_uai"],
            "urn:oid:1.3.6.1.4.1.20326.10.999.1.76": ["Mme"],
        }
        mock_saml_response.in_response_to = request_id

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert (
            response.location
            == "https://webapp-v2.example.com/educonnect/validation?firstName=Max&lastName=SENS&dateOfBirth=2006-08-18&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )

        assert user.firstName == "WrongFirstName"
        assert user.lastName == "Wrong Lastname"
        assert user.validatedBirthDate == date(2006, 8, 18)
        assert user.ineHash is None
        assert user.civility is None

        assert not user.is_beneficiary
        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.HONOR_STATEMENT

        response = client.post("/native/v1/subscription/honor_statement")

        assert response.status_code == 204
        assert user.roles == [users_models.UserRole.UNDERAGE_BENEFICIARY]
        assert user.deposit.amount == 20

        assert user.firstName == "Max"
        assert user.lastName == "SENS"
        assert user.ineHash == ine_hash
        assert user.validatedBirthDate == date(2006, 8, 18)
        assert user.civility == "Mme"


@pytest.mark.usefixtures("db_session")
class NextSubscriptionStepTest:
    eighteen_years_ago = datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=18, months=1)
    fifteen_years_ago = datetime.combine(datetime.today(), datetime.min.time()) - relativedelta(years=15, months=1)

    def test_next_subscription_step_beneficiary(self):
        user = users_factories.BeneficiaryGrant18Factory()
        assert subscription_api.get_next_subscription_step(user) is None

    def test_next_subscription_step_phone_validation(self):
        user = users_factories.UserFactory(dateOfBirth=self.eighteen_years_ago)
        assert (
            subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.PHONE_VALIDATION
        )

    def test_no_step_after_ko_admin_review(self):
        user = users_factories.UserFactory(dateOfBirth=self.eighteen_years_ago)
        fraud_factories.BeneficiaryFraudReviewFactory(user=user, review=fraud_models.FraudReviewStatus.KO)

        assert subscription_api.get_next_subscription_step(user) is None

    def test_next_subscription_step_phone_validation_skipped(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago, phoneValidationStatus=PhoneValidationStatusType.SKIPPED_BY_SUPPORT
        )
        assert subscription_api.get_next_subscription_step(user) in (
            subscription_models.SubscriptionStep.USER_PROFILING,
            subscription_models.SubscriptionStep.PROFILE_COMPLETION,
            subscription_models.SubscriptionStep.IDENTITY_CHECK,
            subscription_models.SubscriptionStep.HONOR_STATEMENT,
        )

    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=True)
    def test_next_subscription_step_underage_profile_completion(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.fifteen_years_ago,
            city=None,
        )
        assert (
            subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.PROFILE_COMPLETION
        )

    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=True)
    def test_next_subscription_step_underage_honor_statement(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.fifteen_years_ago,
            city="Zanzibar",
            activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.HONOR_STATEMENT

    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=True)
    def test_next_subscription_step_underage_finished(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.fifteen_years_ago,
            city="Zanzibar",
            activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            resultContent=None,
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        assert subscription_api.get_next_subscription_step(user) == None

    @override_features(ENABLE_USER_PROFILING=True)
    def test_next_subscription_step_user_profiling(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city=None,
        )
        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.USER_PROFILING

    @override_features(ENABLE_USER_PROFILING=False)
    def test_next_subscription_step_user_profiling_disabled(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city=None,
        )
        assert (
            subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.PROFILE_COMPLETION
        )

    def test_next_subscription_step_user_profiling_ko(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city=None,
        )
        content = fraud_factories.UserProfilingFraudDataFactory(risk_rating="high")
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=content,
            user=user,
            status=fraud_models.FraudCheckStatus.KO,
        )

        assert subscription_api.get_next_subscription_step(user) == None

    def test_next_subscription_step_profile_completion(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city=None,
        )
        content = fraud_factories.UserProfilingFraudDataFactory(risk_rating="trusted")
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=content,
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
        )

        assert (
            subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.PROFILE_COMPLETION
        )

    def test_next_subscription_step_profile_completion_if_user_profiling_suspicious(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city=None,
        )
        content = fraud_factories.UserProfilingFraudDataFactory(risk_rating="medium")
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=content,
            user=user,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
        )

        assert (
            subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.PROFILE_COMPLETION
        )

    def test_next_subscription_step_identity_check(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Zanzibar",
            activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        content = fraud_factories.UserProfilingFraudDataFactory(risk_rating="trusted")
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=content,
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.STARTED,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.IDENTITY_CHECK

    def test_underage_ubble_alread_performed(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Zanzibar",
            activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        content = fraud_factories.UserProfilingFraudDataFactory(risk_rating="trusted")
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=content,
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.HONOR_STATEMENT

    def test_underage_dms_alread_performed(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Zanzibar",
            activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        content = fraud_factories.UserProfilingFraudDataFactory(risk_rating="trusted")
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=content,
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.HONOR_STATEMENT

    def test_next_subscription_step_honor_statement(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            city="Zanzibar",
            activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        content = fraud_factories.UserProfilingFraudDataFactory(risk_rating="trusted")
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=content,
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.HONOR_STATEMENT

    def test_next_subscription_step_finished(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            address="3 rue du quai",
            activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        content = fraud_factories.UserProfilingFraudDataFactory(risk_rating="trusted")
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=content,
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            resultContent=None,
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
        )

        assert subscription_api.get_next_subscription_step(user) == None

    @pytest.mark.parametrize(
        "feature_flags,user_age,user_school_type,expected_result",
        [
            # User 18
            (
                {"ALLOW_IDCHECK_REGISTRATION": True, "ENABLE_UBBLE": True},
                18,
                None,
                [subscription_models.IdentityCheckMethod.UBBLE],
            ),
            (
                {"ALLOW_IDCHECK_REGISTRATION": False},
                18,
                None,
                [],
            ),
            # User 15 - 17
            # Public schools -> force EDUCONNECT when possible
            (
                {
                    "ENABLE_EDUCONNECT_AUTHENTICATION": True,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE": False,
                },
                15,
                users_models.SchoolTypeEnum.PUBLIC_HIGH_SCHOOL,
                [subscription_models.IdentityCheckMethod.EDUCONNECT],
            ),
            (
                {
                    "ENABLE_EDUCONNECT_AUTHENTICATION": True,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE": False,
                },
                15,
                users_models.SchoolTypeEnum.PUBLIC_SECONDARY_SCHOOL,
                [subscription_models.IdentityCheckMethod.EDUCONNECT],
            ),
            (
                {
                    "ENABLE_EDUCONNECT_AUTHENTICATION": False,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE": True,
                    "ENABLE_UBBLE": True,
                },
                15,
                users_models.SchoolTypeEnum.PUBLIC_SECONDARY_SCHOOL,
                [subscription_models.IdentityCheckMethod.UBBLE],
            ),
            (
                {
                    "ENABLE_EDUCONNECT_AUTHENTICATION": False,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ALLOW_IDCHECK_REGISTRATION_FOR_EDUCONNECT_ELIGIBLE": False,
                },
                15,
                users_models.SchoolTypeEnum.PUBLIC_SECONDARY_SCHOOL,
                [],
            ),
            # Other schools
            (
                {
                    "ENABLE_EDUCONNECT_AUTHENTICATION": True,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ENABLE_UBBLE": True,
                },
                15,
                None,
                [subscription_models.IdentityCheckMethod.EDUCONNECT, subscription_models.IdentityCheckMethod.UBBLE],
            ),
            (
                {
                    "ENABLE_EDUCONNECT_AUTHENTICATION": True,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": False,
                    "ENABLE_UBBLE": True,
                },
                15,
                None,
                [subscription_models.IdentityCheckMethod.EDUCONNECT],
            ),
            (
                {
                    "ENABLE_EDUCONNECT_AUTHENTICATION": False,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": True,
                    "ENABLE_UBBLE": True,
                },
                15,
                None,
                [subscription_models.IdentityCheckMethod.UBBLE],
            ),
            (
                {
                    "ENABLE_EDUCONNECT_AUTHENTICATION": True,
                    "ALLOW_IDCHECK_UNDERAGE_REGISTRATION": False,
                },
                15,
                None,
                [subscription_models.IdentityCheckMethod.EDUCONNECT],
            ),
        ],
    )
    def test_get_allowed_identity_check_methods(self, feature_flags, user_age, user_school_type, expected_result):
        dateOfBirth = datetime.today() - relativedelta(years=user_age, months=1)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth, schoolType=user_school_type)
        with override_features(**feature_flags):
            assert subscription_api.get_allowed_identity_check_methods(user) == expected_result

    @pytest.mark.parametrize(
        "feature_flags,user_age,expected_result",
        [
            # User 18
            (
                {"ENABLE_PHONE_VALIDATION": True},
                18,
                True,
            ),
            (
                {"ENABLE_PHONE_VALIDATION": False},
                18,
                False,
            ),
            # User 15 - 17
            (
                {"ENABLE_PHONE_VALIDATION": True},
                15,
                False,
            ),
            (
                {"ENABLE_PHONE_VALIDATION": False},
                16,
                False,
            ),
        ],
    )
    def test_is_phone_validation_in_stepper(self, feature_flags, user_age, expected_result):
        dateOfBirth = datetime.today() - relativedelta(years=user_age, months=1)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth)
        with override_features(**feature_flags):
            assert subscription_api.is_phone_validation_in_stepper(user) == expected_result

    @pytest.mark.parametrize(
        "feature_flags,user_age,expected_result",
        [
            (
                {"ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18": True},
                18,
                subscription_models.MaintenancePageType.WITH_DMS,
            ),
            (
                {"ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18": False},
                18,
                subscription_models.MaintenancePageType.WITHOUT_DMS,
            ),
            (
                {"ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE": True},
                15,
                subscription_models.MaintenancePageType.WITH_DMS,
            ),
            (
                {"ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE": False},
                15,
                subscription_models.MaintenancePageType.WITHOUT_DMS,
            ),
        ],
    )
    @patch("pcapi.core.subscription.api.get_allowed_identity_check_methods", return_value=[])
    def test_get_maintenance_page_type(self, _, feature_flags, user_age, expected_result):
        dateOfBirth = datetime.today() - relativedelta(years=user_age, months=1)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth)
        with override_features(**feature_flags):
            assert subscription_api.get_maintenance_page_type(user) == expected_result

    @freeze_time("2019-01-01")
    def test_next_step_phone_validation_after_dms_succeded_at_19(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 1))
        with freeze_time("2018-01-01"):
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.KO
            )
        assert (
            subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.PHONE_VALIDATION
        )

    def test_user_with_pending_dms_application_should_not_fill_profile(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        # User profiling
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.USER_PROFILING,
            resultContent=fraud_factories.UserProfilingFraudDataFactory(risk_rating="trusted"),
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
        )
        # Pending DMS application
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.PENDING,
            eligibilityType=users_models.EligibilityType.AGE18,
            resultContent=fraud_factories.DMSContentFactory(city="Brockton Bay"),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            resultContent=None,
            user=user,
            status=fraud_models.FraudCheckStatus.OK,
        )

        assert subscription_api.get_next_subscription_step(user) is None

    def test_underage_user_with_pending_dms_application_should_not_fill_profile(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.fifteen_years_ago,
        )
        # Pending DMS application
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.PENDING,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.DMSContentFactory(city="Brockton Bay"),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=None,
        )

        assert subscription_api.get_next_subscription_step(user) is None


@pytest.mark.usefixtures("db_session")
class OverflowSubscriptionLimitationTest:
    @override_features(ENABLE_UBBLE_SUBSCRIPTION_LIMITATION=True)
    @pytest.mark.parametrize("age", [15, 16, 17, 18])
    def test__is_ubble_allowed_if_subscription_overflow(self, age):
        # user birthday is in settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS days
        birth_date = datetime.utcnow() - relativedelta(years=age + 1)
        birth_date += relativedelta(days=settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS - 1)

        # the user has:
        # email v
        user_approching_birthday = users_factories.UserFactory(dateOfBirth=birth_date)

        users_utils.get_age_from_birth_date(user_approching_birthday.dateOfBirth)
        user_not_allowed = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow()
            - relativedelta(years=age, days=settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS + 10)
        )

        assert subscription_api._is_ubble_allowed_if_subscription_overflow(user_approching_birthday)
        assert not subscription_api._is_ubble_allowed_if_subscription_overflow(user_not_allowed)

    @override_features(ENABLE_UBBLE_SUBSCRIPTION_LIMITATION=False)
    def test_subscription_is_possible_if_flag_is_false(self):
        user = users_factories.UserFactory()
        assert subscription_api._is_ubble_allowed_if_subscription_overflow(user)


@pytest.mark.usefixtures("db_session")
class CommonSubscritpionTest:
    def test_handle_eligibility_difference_between_declaration_and_identity_provider_no_difference(self):
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        assert (
            subscription_api.handle_eligibility_difference_between_declaration_and_identity_provider(user, fraud_check)
            == fraud_check
        )

    def test_handle_eligibility_difference_between_declaration_and_identity_provider_eligibility_diff(self):
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.UbbleContentFactory(),  # default age is 18
        )
        # Profile completion fraud check
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.ProfileCompletionContentFactory(),
        )
        assert (
            subscription_api.handle_eligibility_difference_between_declaration_and_identity_provider(user, fraud_check)
            != fraud_check
        )

        user_fraud_checks = sorted(
            fraud_models.BeneficiaryFraudCheck.query.filter_by(user=user).all(), key=lambda x: x.id
        )
        assert len(user_fraud_checks) == 4
        assert user_fraud_checks[0].eligibilityType == users_models.EligibilityType.UNDERAGE
        assert user_fraud_checks[0].type == fraud_models.FraudCheckType.UBBLE
        assert user_fraud_checks[0].reason == "Eligibility type changed by the identity provider"
        assert user_fraud_checks[0].status == fraud_models.FraudCheckStatus.CANCELED

        assert user_fraud_checks[1].eligibilityType == users_models.EligibilityType.UNDERAGE
        assert user_fraud_checks[1].type == fraud_models.FraudCheckType.PROFILE_COMPLETION
        assert user_fraud_checks[1].reason == "Eligibility type changed by the identity provider"
        assert user_fraud_checks[1].status == fraud_models.FraudCheckStatus.CANCELED

        assert user_fraud_checks[2].eligibilityType == users_models.EligibilityType.AGE18
        assert user_fraud_checks[2].type == fraud_models.FraudCheckType.UBBLE
        assert user_fraud_checks[2].status == fraud_models.FraudCheckStatus.PENDING

        assert user_fraud_checks[3].eligibilityType == users_models.EligibilityType.AGE18
        assert user_fraud_checks[3].type == fraud_models.FraudCheckType.PROFILE_COMPLETION
        assert user_fraud_checks[3].status == fraud_models.FraudCheckStatus.OK

    def test_handle_eligibility_difference_between_declaration_and_identity_provider_unreadable_document(self):
        user = users_factories.UserFactory()
        fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.PENDING,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.UbbleContentFactory(birth_date=None),  # default age is 18
        )
        assert (
            subscription_api.handle_eligibility_difference_between_declaration_and_identity_provider(user, fraud_check)
            == fraud_check
        )


@pytest.mark.usefixtures("db_session")
class SubscriptionItemTest:
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=18, months=4)

    def test_phone_validation_item(self):
        user = users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE,
        )
        assert (
            subscription_api.get_phone_validation_subscription_item(user, users_models.EligibilityType.AGE18).status
            == subscription_models.SubscriptionItemStatus.OK
        )

    def test_phone_validation_item_todo(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)
        assert (
            subscription_api.get_phone_validation_subscription_item(user, users_models.EligibilityType.AGE18).status
            == subscription_models.SubscriptionItemStatus.TODO
        )

    def test_phone_validation_item_ko(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, status=fraud_models.FraudCheckStatus.KO, type=fraud_models.FraudCheckType.PHONE_VALIDATION
        )

        assert (
            subscription_api.get_phone_validation_subscription_item(user, users_models.EligibilityType.AGE18).status
            == subscription_models.SubscriptionItemStatus.KO
        )


@pytest.mark.usefixtures("db_session")
class IdentityCheckSubscriptionStatusTest:
    AGE16_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=16, months=4)
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=18, months=4)
    AGE20_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=20, months=4)

    def test_not_eligible(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE20_ELIGIBLE_BIRTH_DATE)

        underage_status = subscription_api.get_identity_check_subscription_status(
            user, users_models.EligibilityType.UNDERAGE
        )
        age_18_status = subscription_api.get_identity_check_subscription_status(
            user, users_models.EligibilityType.AGE18
        )

        assert underage_status == subscription_models.SubscriptionItemStatus.VOID
        assert age_18_status == subscription_models.SubscriptionItemStatus.VOID

    def test_eligible_ex_underage(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE, roles=[users_models.UserRole.UNDERAGE_BENEFICIARY]
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
        )
        underage_status = subscription_api.get_identity_check_subscription_status(
            user, users_models.EligibilityType.UNDERAGE
        )
        age_18_status = subscription_api.get_identity_check_subscription_status(
            user, users_models.EligibilityType.AGE18
        )

        assert underage_status == subscription_models.SubscriptionItemStatus.OK
        assert age_18_status == subscription_models.SubscriptionItemStatus.TODO

    def test_dms_started_ubble_ko(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE20_ELIGIBLE_BIRTH_DATE)

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.STARTED,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.KO,
        )

        status = subscription_api.get_identity_check_subscription_status(user, users_models.EligibilityType.AGE18)

        assert status == subscription_models.SubscriptionItemStatus.PENDING

    def test_dms_error(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE16_ELIGIBLE_BIRTH_DATE)

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.KO,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.ERROR,
        )

        underage_status = subscription_api.get_identity_check_subscription_status(
            user, users_models.EligibilityType.UNDERAGE
        )
        age_18_status = subscription_api.get_identity_check_subscription_status(
            user, users_models.EligibilityType.AGE18
        )

        assert underage_status == subscription_models.SubscriptionItemStatus.TODO
        assert age_18_status == subscription_models.SubscriptionItemStatus.VOID

    def test_ubble_and_educo_ko(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE16_ELIGIBLE_BIRTH_DATE)

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.KO,
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.KO,
        )

        status = subscription_api.get_identity_check_subscription_status(user, users_models.EligibilityType.UNDERAGE)

        assert status == subscription_models.SubscriptionItemStatus.KO

    def test_ubble_underage_valid_for_18(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
        )

        age18_status = subscription_api.get_identity_check_subscription_status(user, users_models.EligibilityType.AGE18)

        assert age18_status == subscription_models.SubscriptionItemStatus.OK

    def test_dms_underage_valid_for_18(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )

        age18_status = subscription_api.get_identity_check_subscription_status(user, users_models.EligibilityType.AGE18)

        assert age18_status == subscription_models.SubscriptionItemStatus.OK

    def test_educonnect_underage_not_valid_for_18(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
        )

        age18_status = subscription_api.get_identity_check_subscription_status(user, users_models.EligibilityType.AGE18)

        assert age18_status == subscription_models.SubscriptionItemStatus.TODO


@pytest.mark.usefixtures("db_session")
class NeedsToPerformeIdentityCheckTest:
    AGE16_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=16, months=4)
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=18, months=4)
    AGE20_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=20, months=4)

    def test_not_eligible(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE20_ELIGIBLE_BIRTH_DATE)

        assert not subscription_api._needs_to_perform_identity_check(user)

    def test_ex_underage_eligible_18(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE, roles=[users_models.UserRole.UNDERAGE_BENEFICIARY]
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
        )

        assert subscription_api._needs_to_perform_identity_check(user)

    def test_ubble_underage_eligible_18_does_not_need_to_redo(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE, roles=[users_models.UserRole.UNDERAGE_BENEFICIARY]
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
        )

        assert not subscription_api._needs_to_perform_identity_check(user)

    def test_ubble_started(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.STARTED,
        )

        assert subscription_api._needs_to_perform_identity_check(user)

    def test_dms_started(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE16_ELIGIBLE_BIRTH_DATE)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.STARTED,
        )

        assert not subscription_api._needs_to_perform_identity_check(user)

    def test_educonnect_ok(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE16_ELIGIBLE_BIRTH_DATE)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
        )

        assert not subscription_api._needs_to_perform_identity_check(user)


@pytest.mark.usefixtures("db_session")
class GetFirstRegistrationDateTest:
    def test_get_first_registration_date_no_check(self):
        user = users_factories.UserFactory()
        assert (
            subscription_api.get_first_registration_date(user, user.dateOfBirth, users_models.EligibilityType.UNDERAGE)
            is None
        )

    def test_get_first_registration_date_underage(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(2002, 1, 15))
        d1 = datetime(2018, 1, 1)
        d2 = datetime(2018, 2, 1)
        d3 = datetime(2018, 3, 1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            dateCreated=d2,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            dateCreated=d2,
            resultContent=None,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            dateCreated=d3,
            resultContent=fraud_factories.DMSContentFactory(registration_datetime=d1),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        assert (
            subscription_api.get_first_registration_date(user, user.dateOfBirth, users_models.EligibilityType.UNDERAGE)
            == d1
        )

    def test_get_first_registration_date_age_18(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(2002, 1, 15))
        d1 = datetime(2018, 1, 1)
        d2 = datetime(2020, 2, 1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            dateCreated=d1,
            resultContent=fraud_factories.DMSContentFactory(registration_datetime=d1),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            dateCreated=d2,
            resultContent=fraud_factories.DMSContentFactory(registration_datetime=d2),
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        assert (
            subscription_api.get_first_registration_date(user, user.dateOfBirth, users_models.EligibilityType.AGE18)
            == d2
        )

    def test_with_uneligible_age_try(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(2005, 1, 15))
        d1 = datetime(2020, 1, 1)
        d2 = datetime(2020, 2, 1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            dateCreated=d1,
            status=fraud_models.FraudCheckStatus.KO,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            dateCreated=d2,
            resultContent=fraud_factories.DMSContentFactory(registration_datetime=d2),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        assert (
            subscription_api.get_first_registration_date(user, user.dateOfBirth, users_models.EligibilityType.UNDERAGE)
            == d2
        )

    def test_with_registration_before_opening_try(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(2005, 1, 15))
        d1 = datetime(2020, 1, 1)
        d2 = datetime(2020, 2, 1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.INTERNAL_REVIEW,  # this happened with jouve results saying when the age is <18
            dateCreated=d1,
            status=fraud_models.FraudCheckStatus.KO,
            eligibilityType=None,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            dateCreated=d2,
            resultContent=fraud_factories.DMSContentFactory(registration_datetime=d2),
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        assert (
            subscription_api.get_first_registration_date(user, user.dateOfBirth, users_models.EligibilityType.UNDERAGE)
            == d2
        )

    def test_without_eligible_try(self):
        user = users_factories.UserFactory(dateOfBirth=datetime(2005, 1, 15))
        d1 = datetime(2020, 1, 1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            dateCreated=d1,
            status=fraud_models.FraudCheckStatus.KO,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        assert (
            subscription_api.get_first_registration_date(user, user.dateOfBirth, users_models.EligibilityType.UNDERAGE)
            == None
        )


@pytest.mark.usefixtures("db_session")
class ShouldValidatePhoneTest:
    def test_eligible_15_17(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=17))
        assert not subscription_api._should_validate_phone(user, user.eligibility)

    def test_eligible_18(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18))
        assert subscription_api._should_validate_phone(user, user.eligibility)

    def test_already_validated(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        assert not subscription_api._should_validate_phone(user, user.eligibility)

    def test_when_has_failed(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18))
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.KO,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        assert subscription_api._should_validate_phone(user, user.eligibility)

    @override_features(ENABLE_PHONE_VALIDATION=False)
    def test_when_flag_off(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.KO,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        assert not subscription_api._should_validate_phone(user, user.eligibility)

    def test_when_skipped_by_support(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.SKIPPED_BY_SUPPORT,
        )

        assert not subscription_api._should_validate_phone(user, user.eligibility)


@pytest.mark.usefixtures("db_session")
class CompleteProfileTest:
    def test_when_profile_was_proviously_cancelled(self):
        """
        This was a bug when a user previously completed profile but the BeneficiaryCancelled
        was cancelled because of "eligibility_changed" scenaria
        """
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.CANCELED,
            eligibilityType=users_models.EligibilityType.AGE18,
            reasonCodes=[fraud_models.FraudReasonCode.ELIGIBILITY_CHANGED],
        )

        subscription_api.complete_profile(user, "address", "city", "12400", "étudiant", "harry", "cover")

        assert subscription_repository.get_completed_profile_check(user, EligibilityType.AGE18)
        assert (
            fraud_models.BeneficiaryFraudCheck.query.filter_by(
                userId=user.id,
                type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
                status=fraud_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.AGE18,
            ).count()
            == 1
        )


@pytest.mark.usefixtures("db_session")
class ActivateBeneficiaryIfNoMissingStepTest:
    def test_activation_success(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName="profile-firstname",
            lastName="profile-lastname",
        )
        identity_firstname = "Yolan"
        identity_lastname = "Mac Doumy"
        identity_birth_date = date.today() - relativedelta(years=18, months=3, days=1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
            resultContent=fraud_factories.UbbleContentFactory(
                first_name=identity_firstname,
                last_name=identity_lastname,
                birth_date=identity_birth_date.isoformat(),
            ),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        is_success = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_success
        assert user.is_beneficiary
        assert user.firstName == identity_firstname
        assert user.lastName == identity_lastname
        assert user.validatedBirthDate == identity_birth_date
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.ACCEPTED_AS_BENEFICIARY.value
        )

    def test_admin_review_ko(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName="profile-firstname",
            lastName="profile-lastname",
        )
        identity_firstname = "Yolan"
        identity_lastname = "Mac Doumy"
        identity_birth_date = date.today() - relativedelta(years=18, months=3, days=1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
            resultContent=fraud_factories.UbbleContentFactory(
                first_name=identity_firstname,
                last_name=identity_lastname,
                birth_date=identity_birth_date.isoformat(),
            ),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        fraud_factories.BeneficiaryFraudReviewFactory(user=user, review=fraud_models.FraudReviewStatus.KO)

        is_success = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert not is_success
        assert not user.is_beneficiary

    def test_missing_step(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName=None,
            lastName=None,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        is_success = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert not is_success
        assert not user.is_beneficiary
        assert user.firstName is None
        assert user.lastName is None

    def test_duplicate_detected(self):
        first_name = "Alain"
        last_name = "Milourd"
        birth_date = datetime.utcnow() - relativedelta(years=18)

        users_factories.BeneficiaryGrant18Factory(firstName=first_name, lastName=last_name, dateOfBirth=birth_date)

        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName=None,
            lastName=None,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        to_invalidate_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            resultContent=fraud_factories.UbbleContentFactory(
                first_name=first_name, last_name=last_name, birth_date=birth_date.date().isoformat()
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        resut = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert not resut
        assert not user.is_beneficiary
        assert to_invalidate_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS
        assert to_invalidate_check.reasonCodes == [fraud_models.FraudReasonCode.DUPLICATE_USER]
        assert user.firstName is None
        assert user.lastName is None

    AGE18_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=18, months=4)
    UNDERAGE_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=16, months=4)

    def eligible_user(
        self,
        validate_phone: bool,
        city: typing.Optional[str] = "Quito",
        activity: typing.Optional[users_models.ActivityEnum] = "Étudiant",
        is_underage: bool = False,
    ):
        phone_validation_status = users_models.PhoneValidationStatusType.VALIDATED if validate_phone else None
        return users_factories.UserFactory(
            dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE if not is_underage else self.UNDERAGE_ELIGIBLE_BIRTH_DATE,
            phoneValidationStatus=phone_validation_status,
            city=city,
            activity=activity,
        )

    def test_activation_success_underage(self):
        user = self.eligible_user(validate_phone=False, is_underage=True)
        identity_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.EduconnectContentFactory(
                first_name="Léo",
                last_name="Nard",
                birth_date=self.UNDERAGE_ELIGIBLE_BIRTH_DATE,
            ),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )

        is_success = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_success
        assert user.is_beneficiary
        assert user.firstName == "Léo"
        assert user.lastName == "Nard"
        assert user.dateOfBirth.date() == self.UNDERAGE_ELIGIBLE_BIRTH_DATE.date()
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.ACCEPTED_AS_EAC_BENEFICIARY.value
        )
        assert user.deposit.source == f"dossier FraudCheckType.EDUCONNECT [{identity_fraud_check.thirdPartyId}]"
        assert user.deposit.amount == 30

    @override_features(ENABLE_USER_PROFILING=False)
    def test_no_missing_step_with_user_profiling_disabled(self):
        user = self.eligible_user(validate_phone=True, is_underage=False)

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        assert subscription_api.activate_beneficiary_if_no_missing_step(user)
        assert user.is_beneficiary

    @override_features(ENABLE_USER_PROFILING=False)
    def test_missing_step_with_user_profiling_disabled_but_profiling_ko(self):
        user = self.eligible_user(validate_phone=True, is_underage=False)

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.USER_PROFILING, status=fraud_models.FraudCheckStatus.KO
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )

        assert not subscription_api.activate_beneficiary_if_no_missing_step(user)

    @override_features(ENABLE_PHONE_VALIDATION=False)
    def test_rejected_identity(self):
        user = self.eligible_user(validate_phone=False)

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.KO
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        assert not subscription_api.activate_beneficiary_if_no_missing_step(user)
        assert not user.is_beneficiary

    def test_missing_profile_after_dms_application(self):
        user = self.eligible_user(validate_phone=True, city=None)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.USER_PROFILING, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )

        assert not subscription_api.activate_beneficiary_if_no_missing_step(user)
        assert not user.is_beneficiary

    def test_underage_ubble_valid_for_18(self):
        identity_firstname = "Yolan"
        identity_lastname = "Mac Doumy"
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName=identity_firstname,
            lastName=identity_lastname,
        )
        identity_birth_date = date.today() - relativedelta(years=18, months=3, days=1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.UbbleContentFactory(
                first_name=identity_firstname,
                last_name=identity_lastname,
                birth_date=identity_birth_date.isoformat(),
            ),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        is_success = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_success
        assert user.is_beneficiary
        assert user.firstName == identity_firstname
        assert user.lastName == identity_lastname
        assert user.validatedBirthDate == identity_birth_date
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.ACCEPTED_AS_BENEFICIARY.value
        )

    def test_underage_dms_valid_for_18(self):
        identity_firstname = "Yolan"
        identity_lastname = "Mac Doumy"
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName=identity_firstname,
            lastName=identity_lastname,
        )
        identity_birth_date = date.today() - relativedelta(years=18, months=3, days=1)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=fraud_factories.DMSContentFactory(
                first_name=identity_firstname,
                last_name=identity_lastname,
                birth_date=identity_birth_date.isoformat(),
            ),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.PHONE_VALIDATION,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        is_success = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_success
        assert user.is_beneficiary
        assert user.firstName == identity_firstname
        assert user.lastName == identity_lastname
        assert user.validatedBirthDate == identity_birth_date
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.ACCEPTED_AS_BENEFICIARY.value
        )


@pytest.mark.usefixtures("db_session")
class SubscriptionMessageTest:
    def test_not_eligible(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=20))

        assert subscription_api.get_subscription_message(user) is None

    def test_already_beneficiary(self):
        user = users_factories.BeneficiaryGrant18Factory()

        assert subscription_api.get_subscription_message(user) is None

    def test_other_next_step(self):
        user_needing_honor_statement = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=17)
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            eligibilityType=EligibilityType.UNDERAGE,
            user=user_needing_honor_statement,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.DMS,
            eligibilityType=EligibilityType.UNDERAGE,
            user=user_needing_honor_statement,
            status=fraud_models.FraudCheckStatus.PENDING,
        )

        assert subscription_api.get_subscription_message(user_needing_honor_statement) is None

    @override_features(ENABLE_UBBLE=False)
    def test_maintenance(self):
        user_needing_identity_check = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            user=user_needing_identity_check,
            status=fraud_models.FraudCheckStatus.OK,
        )

        message = subscription_api.get_subscription_message(user_needing_identity_check)

        assert (
            message.user_message
            == "La vérification d'identité est momentanément indisponible. L'équipe du pass Culture met tout en oeuvre pour la rétablir au plus vite."
        )
        assert message.pop_over_icon == subscription_models.PopOverIcon.CLOCK

    @patch("pcapi.core.subscription.dms.api.get_dms_subscription_message")
    def test_dms_message_is_returned(self, mocked_dms_message):
        dms_returned_message = subscription_models.SubscriptionMessage(
            user_message="Ferme ton application. Attends 10 secondes. Ouvre la, referme. Mange un steak. Reviens. C'est bon.",
            pop_over_icon=subscription_models.PopOverIcon.MAGNIFYING_GLASS,
        )
        mocked_dms_message.return_value = dms_returned_message

        user_with_dms_pending = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            user=user_with_dms_pending,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            user=user_with_dms_pending,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.DMS,
            user=user_with_dms_pending,
            status=fraud_models.FraudCheckStatus.ERROR,
        )
        last_dms_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.DMS,
            user=user_with_dms_pending,
            status=fraud_models.FraudCheckStatus.PENDING,
        )

        message = subscription_api.get_subscription_message(user_with_dms_pending)

        mocked_dms_message.assert_called_once_with(last_dms_check)
        assert message == dms_returned_message

    @patch("pcapi.core.subscription.ubble.api.get_ubble_subscription_message")
    def test_ubble_pending_message_is_returned(self, mocked_ubble_message):
        ubble_returned_message = subscription_models.SubscriptionMessage(
            user_message="Prends un miroir, recoiffe-toi, entraine-toi à sourire et reviens.",
            pop_over_icon=subscription_models.PopOverIcon.MAGNIFYING_GLASS,
        )
        mocked_ubble_message.return_value = ubble_returned_message

        user_with_ubble_pending = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            user=user_with_ubble_pending,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            user=user_with_ubble_pending,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user_with_ubble_pending,
            status=fraud_models.FraudCheckStatus.ERROR,
        )
        last_ubble_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user_with_ubble_pending,
            status=fraud_models.FraudCheckStatus.PENDING,
        )

        message = subscription_api.get_subscription_message(user_with_ubble_pending)

        mocked_ubble_message.assert_called_once_with(last_ubble_check, is_retryable=False)
        assert message == ubble_returned_message

    @patch("pcapi.core.subscription.ubble.api.get_ubble_subscription_message")
    def test_ubble_retryable_message_is_returned(self, mocked_ubble_message):
        ubble_returned_message = subscription_models.SubscriptionMessage(
            user_message="Prends un miroir, recoiffe-toi, entraine-toi à sourire et reviens.",
            pop_over_icon=subscription_models.PopOverIcon.MAGNIFYING_GLASS,
        )
        mocked_ubble_message.return_value = ubble_returned_message

        user_with_ubble_pending = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            phoneValidationStatus=PhoneValidationStatusType.VALIDATED,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            user=user_with_ubble_pending,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            user=user_with_ubble_pending,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user_with_ubble_pending,
            status=fraud_models.FraudCheckStatus.ERROR,
        )
        last_ubble_check = fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.UBBLE,
            user=user_with_ubble_pending,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.ID_CHECK_EXPIRED],
        )

        message = subscription_api.get_subscription_message(user_with_ubble_pending)

        mocked_ubble_message.assert_called_once_with(last_ubble_check, is_retryable=True)
        assert message == ubble_returned_message

    @patch("pcapi.core.subscription.educonnect.api.get_educonnect_subscription_message")
    def test_educonnect_message_is_returned(self, mocked_educonnect_message):
        educonnect_returned_message = subscription_models.SubscriptionMessage(
            user_message="Pour une vie édulcorée.",
            pop_over_icon=subscription_models.PopOverIcon.MAGNIFYING_GLASS,
        )
        mocked_educonnect_message.return_value = educonnect_returned_message

        user_with_educonnect = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=16),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
            user=user_with_educonnect,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            user=user_with_educonnect,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            user=user_with_educonnect,
            status=fraud_models.FraudCheckStatus.KO,
        )
        last_educocheck = fraud_factories.BeneficiaryFraudCheckFactory(
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.EDUCONNECT,
            user=user_with_educonnect,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[fraud_models.FraudReasonCode.DUPLICATE_USER],
        )

        message = subscription_api.get_subscription_message(user_with_educonnect)

        mocked_educonnect_message.assert_called_once_with(last_educocheck)
        assert message == educonnect_returned_message


@pytest.mark.usefixtures("db_session")
class HasCompletedProfileTest:
    def test_has_completed(self):
        user = users_factories.UserFactory(
            dateOfBirth=datetime.utcnow() - relativedelta(years=18),
            activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )
        assert (
            subscription_api.has_completed_profile_for_given_eligibility(user, users_models.EligibilityType.UNDERAGE)
            is True
        )
        assert subscription_api.has_completed_profile_for_given_eligibility(user, user.eligibility) is False

    def test_has_completed_with_profile_completion_ok(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18))
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user, status=fraud_models.FraudCheckStatus.OK)
        assert subscription_api.has_completed_profile_for_given_eligibility(user, user.eligibility) is True

    def test_has_not_completed_with_profile_completion_cancelled(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18))
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user, status=fraud_models.FraudCheckStatus.CANCELED)
        assert subscription_api.has_completed_profile_for_given_eligibility(user, user.eligibility) is False

    def test_has_completed_with_dms_form_filled(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18))
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.DMS, user=user, status=fraud_models.FraudCheckStatus.PENDING
        )
        assert subscription_api.has_completed_profile_for_given_eligibility(user, user.eligibility) is True

    def test_has_not_completed_with_dms_form_filled_for_underage(self):
        user = users_factories.UserFactory(dateOfBirth=datetime.utcnow() - relativedelta(years=18))
        fraud_factories.BeneficiaryFraudCheckFactory(
            type=fraud_models.FraudCheckType.DMS,
            user=user,
            status=fraud_models.FraudCheckStatus.PENDING,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )
        assert subscription_api.has_completed_profile_for_given_eligibility(user, user.eligibility) is False
