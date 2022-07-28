import dataclasses
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
from pcapi.core.testing import override_features
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import PhoneValidationStatusType
from pcapi.models import api_errors
import pcapi.notifications.push.testing as push_testing


@pytest.mark.usefixtures("db_session")
class EduconnectFlowTest:
    @freeze_time("2021-10-10")
    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_saml_client")
    @override_features(ENABLE_EDUCONNECT_AUTHENTICATION=True)
    def test_educonnect_subscription(self, mock_get_educonnect_saml_client, client, app):
        ine_hash = "5ba682c0fc6a05edf07cd8ed0219258f"
        user = users_factories.UserFactory(dateOfBirth=datetime(2004, 1, 1))
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
        assert not subscription_api.should_complete_profile(user, user.eligibility)
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
        }
        mock_saml_response.in_response_to = request_id

        response = client.post("/saml/acs", form={"SAMLResponse": "encrypted_data"})

        assert response.status_code == 302
        assert (
            response.location
            == "https://webapp-v2.example.com/educonnect/validation?firstName=Max&lastName=SENS&dateOfBirth=2006-08-18&logoutUrl=https%3A%2F%2Feduconnect.education.gouv.fr%2FLogout"
        )

        assert user.firstName == "Max"
        assert user.lastName == "SENS"
        assert user.dateOfBirth == datetime(2006, 8, 18, 0, 0)
        assert user.ineHash == ine_hash

        assert not user.is_beneficiary
        assert subscription_api.get_next_subscription_step(user) == subscription_models.SubscriptionStep.HONOR_STATEMENT

        response = client.post("/native/v1/subscription/honor_statement")

        assert response.status_code == 204
        assert user.roles == [users_models.UserRole.UNDERAGE_BENEFICIARY]
        assert user.deposit.amount == 20


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
                {"ENABLE_PHONE_VALIDATION": True, "ENABLE_PHONE_VALIDATION_IN_STEPPER": True},
                18,
                True,
            ),
            (
                {"ENABLE_PHONE_VALIDATION": True, "ENABLE_PHONE_VALIDATION_IN_STEPPER": False},
                18,
                False,
            ),
            (
                {"ENABLE_PHONE_VALIDATION": False, "ENABLE_PHONE_VALIDATION_IN_STEPPER": True},
                18,
                False,
            ),
            # User 15 - 17
            (
                {"ENABLE_PHONE_VALIDATION": True, "ENABLE_PHONE_VALIDATION_IN_STEPPER": True},
                15,
                False,
            ),
            (
                {"ENABLE_PHONE_VALIDATION": True, "ENABLE_PHONE_VALIDATION_IN_STEPPER": True},
                16,
                False,
            ),
            (
                {"ENABLE_PHONE_VALIDATION": True, "ENABLE_PHONE_VALIDATION_IN_STEPPER": True},
                17,
                False,
            ),
        ],
    )
    def test_is_phone_validation_in_stepper(self, feature_flags, user_age, expected_result):
        dateOfBirth = datetime.today() - relativedelta(years=user_age, months=1)
        user = users_factories.UserFactory(dateOfBirth=dateOfBirth)
        with override_features(**feature_flags):
            assert subscription_api.is_phone_validation_in_stepper(user) == expected_result

    def test_should_complete_profile_not_completed(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.eighteen_years_ago,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            address="3 rue du quai",
            activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
        )
        assert subscription_api.should_complete_profile(user, user.eligibility)

    def test_should_complete_profile_completed_dms(self):
        user = users_factories.UserFactory(dateOfBirth=self.eighteen_years_ago)
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        assert not subscription_api.should_complete_profile(user, user.eligibility)

    def test_should_complete_profile_completed(self):
        user = users_factories.UserFactory(dateOfBirth=self.eighteen_years_ago)
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)
        assert subscription_api.should_complete_profile(user, users_models.EligibilityType.UNDERAGE)
        assert not subscription_api.should_complete_profile(user, user.eligibility)

    def test_should_complete_profile_completed_underage(self):
        user = users_factories.UserFactory(dateOfBirth=self.eighteen_years_ago)
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )
        assert not subscription_api.should_complete_profile(user, users_models.EligibilityType.UNDERAGE)
        assert subscription_api.should_complete_profile(user, user.eligibility)

    def test_should_complete_profile_completed_both(self):
        user = users_factories.UserFactory(dateOfBirth=self.eighteen_years_ago)
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.AGE18
        )
        assert not subscription_api.should_complete_profile(user, users_models.EligibilityType.UNDERAGE)
        assert not subscription_api.should_complete_profile(user, user.eligibility)

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
class OnSuccessfulDMSApplicationTest:
    def test_new_beneficiaries_requires_userprofiling(self):
        # given
        information = fraud_models.DMSContent(
            department="93",
            last_name="Doe",
            first_name="Jane",
            birth_date=datetime.utcnow() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18),
            email="jane.doe@example.com",
            phone="0612345678",
            postal_code="93130",
            address="11 Rue du Test",
            application_number=123,
            procedure_number=123456,
            civility=users_models.GenderEnum.F,
            activity="Étudiant",
            registration_datetime=datetime.today(),
        )
        applicant = users_factories.UserFactory(email=information.email)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=applicant, type=fraud_models.FraudCheckType.USER_PROFILING, status=fraud_models.FraudCheckStatus.OK
        )

        # when
        subscription_api.on_successful_application(user=applicant, source_data=information)

        # then
        first = users_models.User.query.first()
        assert first.email == "jane.doe@example.com"
        assert first.civility == users_models.GenderEnum.F.value
        assert first.activity == "Étudiant"
        assert not first.has_beneficiary_role
        assert (
            subscription_api.get_next_subscription_step(first) == subscription_models.SubscriptionStep.PHONE_VALIDATION
        )

    def test_new_beneficiaries_are_recorded_with_deposit(self):
        # given
        information = fraud_models.DMSContent(
            department="93",
            last_name="Doe",
            first_name="Jane",
            birth_date=datetime.utcnow() - relativedelta(years=users_constants.ELIGIBILITY_AGE_18),
            email="jane.doe@example.com",
            phone="0612345678",
            postal_code="93130",
            address="11 Rue du Test",
            application_number=123,
            procedure_number=123456,
            civility=users_models.GenderEnum.F,
            activity="Étudiant",
            registration_datetime=datetime.today(),
        )
        applicant = users_factories.UserFactory(
            email=information.email, phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=applicant)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=applicant, type=fraud_models.FraudCheckType.USER_PROFILING, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=applicant, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=applicant, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.OK
        )

        # when
        subscription_api.on_successful_application(user=applicant, source_data=information)

        # then
        first = users_models.User.query.first()
        assert first.email == "jane.doe@example.com"
        assert first.wallet_balance == 300
        assert first.civility == users_models.GenderEnum.F.value
        assert first.activity == "Étudiant"
        assert first.has_beneficiary_role
        assert len(push_testing.requests) == 2
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.ACCEPTED_AS_BENEFICIARY.value
        )

    @patch("pcapi.repository.repository")
    def test_error_is_collected_if_beneficiary_could_not_be_saved(self, mock_repository):
        # given
        information = fraud_factories.DMSContentFactory(application_number=123)
        applicant = users_factories.UserFactory(email=information.email)

        mock_repository.save.side_effect = [api_errors.ApiErrors({"postalCode": ["baaaaad value"]})]

        # when
        with pytest.raises(api_errors.ApiErrors):
            subscription_api.on_successful_application(user=applicant, source_data=information)

        # then
        assert len(push_testing.requests) == 0

    def test_activate_beneficiary_when_confirmation_happens_after_18_birthday(self):
        with freeze_time("2020-01-01"):
            applicant = users_factories.UserFactory(
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
            )
            eighteen_years_and_one_month_ago = datetime.today() - relativedelta(years=18, months=1)

            # the user deposited their DMS application before turning 18
            information = fraud_factories.DMSContentFactory(
                birth_date=eighteen_years_and_one_month_ago,
                registration_datetime=datetime.today(),
            )
            fraud_factories.ProfileCompletionFraudCheckFactory(user=applicant)
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=applicant,
                type=fraud_models.FraudCheckType.USER_PROFILING,
                status=fraud_models.FraudCheckStatus.OK,
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=applicant,
                type=fraud_models.FraudCheckType.DMS,
                status=fraud_models.FraudCheckStatus.OK,
            )
            fraud_factories.BeneficiaryFraudCheckFactory(
                user=applicant,
                type=fraud_models.FraudCheckType.HONOR_STATEMENT,
                status=fraud_models.FraudCheckStatus.OK,
            )

        assert applicant.has_beneficiary_role is False

        with freeze_time("2020-03-01"):
            # the DMS application is confirmed after the user turns 18
            subscription_api.on_successful_application(user=applicant, source_data=information)
        assert applicant.has_beneficiary_role

    @freeze_time("2020-03-01")
    def test_activate_beneficiary_when_confirmation_happens_after_18_birthday_requires_phone_validation(self):
        with freeze_time("2020-01-01"):
            applicant = users_factories.UserFactory()
            eighteen_years_and_one_month_ago = datetime.today() - relativedelta(years=18, months=1)

            # the user deposited their DMS application before turning 18
            information = fraud_models.DMSContent(
                department="93",
                last_name="Doe",
                first_name="Jane",
                birth_date=eighteen_years_and_one_month_ago,
                email="jane.doe@example.com",
                phone="0612345678",
                postal_code="93130",
                address="11 Rue du Test",
                application_number=123,
                procedure_number=123456,
                civility="Mme",
                activity="Étudiant",
                registration_datetime=datetime.today(),
            )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=applicant,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=applicant,
            type=fraud_models.FraudCheckType.HONOR_STATEMENT,
            status=fraud_models.FraudCheckStatus.OK,
        )

        # the DMS application is confirmed after the user turns 18
        subscription_api.on_successful_application(user=applicant, source_data=information)

        assert applicant.has_beneficiary_role is False
        assert (
            subscription_api.get_next_subscription_step(applicant)
            == subscription_models.SubscriptionStep.PHONE_VALIDATION
        )


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
class GetActivableFraudCheckTest:
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=18, months=4)

    def eligible_user(
        self,
        validate_phone: bool,
        city: typing.Optional[str] = "Quito",
        activity: typing.Optional[users_models.ActivityEnum] = "Étudiant",
    ):
        phone_validation_status = users_models.PhoneValidationStatusType.VALIDATED if validate_phone else None
        return users_factories.UserFactory(
            dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE,
            phoneValidationStatus=phone_validation_status,
            city=city,
            activity=activity,
        )

    def test_no_missing_step(self):
        user = self.eligible_user(validate_phone=True)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.USER_PROFILING, status=fraud_models.FraudCheckStatus.OK
        )
        identity_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        assert subscription_api._get_activable_identity_fraud_check(user) == identity_fraud_check

    @override_features(ENABLE_USER_PROFILING=False)
    def test_no_missing_step_with_user_profiling_disabled(self):
        user = self.eligible_user(validate_phone=True)

        identity_fraud_check = fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.ProfileCompletionFraudCheckFactory(user=user)

        assert subscription_api._get_activable_identity_fraud_check(user) == identity_fraud_check

    @override_features(ENABLE_USER_PROFILING=False)
    def test_missing_step_with_user_profiling_disabled_but_profiling_ko(self):
        user = self.eligible_user(validate_phone=True)

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.USER_PROFILING, status=fraud_models.FraudCheckStatus.KO
        )

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )

        assert subscription_api._get_activable_identity_fraud_check(user) is None

    @override_features(ENABLE_PHONE_VALIDATION=True)
    def test_missing_step(self):
        user = self.eligible_user(validate_phone=False)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )

        assert subscription_api._get_activable_identity_fraud_check(user) is None

    @override_features(ENABLE_PHONE_VALIDATION=True)
    def test_rejected_import(self):
        user = self.eligible_user(validate_phone=False)

        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.UBBLE, status=fraud_models.FraudCheckStatus.KO
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )

        assert subscription_api._get_activable_identity_fraud_check(user) is None

    @override_features(ENABLE_PHONE_VALIDATION=True)
    def test_missing_all(self):
        user = self.eligible_user(validate_phone=False)

        assert subscription_api._get_activable_identity_fraud_check(user) is None

    def test_missing_userprofiling_after_dms_application(self):
        user = self.eligible_user(validate_phone=True)
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.OK
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user, type=fraud_models.FraudCheckType.HONOR_STATEMENT, status=fraud_models.FraudCheckStatus.OK
        )
        assert not subscription_api._get_activable_identity_fraud_check(user)

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

        assert not subscription_api._get_activable_identity_fraud_check(user)


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
            type=fraud_models.FraudCheckType.UBBLE,
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


@pytest.mark.usefixtures("db_session")
class NeedsToPerformeIdentityCheckTest:
    AGE16_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=16, months=4)
    AGE18_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=18, months=4)
    AGE20_ELIGIBLE_BIRTH_DATE = datetime.utcnow() - relativedelta(years=20, months=4)

    def test_not_eligible(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE20_ELIGIBLE_BIRTH_DATE)

        assert not subscription_api._needs_to_perform_identity_check(user)

    def test_ex_underage_eligible(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE, roles=[users_models.UserRole.UNDERAGE_BENEFICIARY]
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_models.FraudCheckType.UBBLE,
            status=fraud_models.FraudCheckStatus.OK,
        )

        assert subscription_api._needs_to_perform_identity_check(user)

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
        assert subscription_api.get_first_registration_date(user, users_models.EligibilityType.UNDERAGE) is None

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
        assert subscription_api.get_first_registration_date(user, users_models.EligibilityType.UNDERAGE) == d1

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
        assert subscription_api.get_first_registration_date(user, users_models.EligibilityType.AGE18) == d2

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

        assert subscription_api.get_first_registration_date(user, users_models.EligibilityType.UNDERAGE) == d2

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

        assert subscription_api.get_first_registration_date(user, users_models.EligibilityType.UNDERAGE) == d2

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

        assert subscription_api.get_first_registration_date(user, users_models.EligibilityType.UNDERAGE) == None


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

        assert subscription_api.has_completed_profile(user, EligibilityType.AGE18)
        assert (
            fraud_models.BeneficiaryFraudCheck.query.filter_by(
                userId=user.id,
                type=fraud_models.FraudCheckType.PROFILE_COMPLETION,
                status=fraud_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.AGE18,
            ).count()
            == 1
        )
