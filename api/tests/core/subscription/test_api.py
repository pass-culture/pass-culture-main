import dataclasses
from datetime import date
from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import psycopg2
import pytest
import time_machine
from dateutil.relativedelta import relativedelta
from flask_jwt_extended.utils import create_access_token
from sqlalchemy.orm import joinedload

import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.api as users_api
from pcapi import settings
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import factories as subscription_factories
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import repository as subscription_repository
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users import young_status
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.string import u_nbsp
from pcapi.utils.transaction_manager import atomic


@pytest.mark.usefixtures("db_session")
class RequiresIdCheckTest:
    def test_requires_identity_check_step_with_no_underage_beneficiary_role(self):
        user = users_factories.UserFactory()

        assert subscription_api.requires_identity_check_step(user) is True

    def test_requires_identity_check_step_with_fraud_check_not_present(self):
        user = users_factories.ExUnderageBeneficiaryFactory()

        assert subscription_api.requires_identity_check_step(user) is True

    def test_does_not_requires_id_check_for_free_eligibility(self):
        user = users_factories.UserFactory(age=15)

        assert not subscription_api.requires_identity_check_step(user)

    @pytest.mark.parametrize(
        "fraud_check_type,expected_result",
        [
            (subscription_models.FraudCheckType.JOUVE, True),
            (subscription_models.FraudCheckType.DMS, False),
            (subscription_models.FraudCheckType.UBBLE, False),
            (subscription_models.FraudCheckType.EDUCONNECT, True),
        ],
    )
    def test_requires_identity_check_step_with_valid_identity_fraud_check(self, fraud_check_type, expected_result):
        user = users_factories.ExUnderageBeneficiaryFactory()

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=fraud_check_type,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        assert subscription_api.requires_identity_check_step(user) is expected_result

    @pytest.mark.parametrize(
        "fraud_check_type",
        [
            subscription_models.FraudCheckType.JOUVE,
            subscription_models.FraudCheckType.DMS,
            subscription_models.FraudCheckType.UBBLE,
            subscription_models.FraudCheckType.EDUCONNECT,
        ],
    )
    def test_requires_identity_check_step_with_invalid_identity_check(self, fraud_check_type):
        user = users_factories.ExUnderageBeneficiaryFactory()

        subscription_factories.BeneficiaryFraudCheckFactory(
            userId=user.id,
            type=fraud_check_type,
            status=subscription_models.FraudCheckStatus.KO,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
        )

        assert subscription_api.requires_identity_check_step(user) is True


@pytest.mark.usefixtures("db_session")
class EduconnectFlowTest:
    @time_machine.travel("2021-10-10")
    @patch("pcapi.connectors.beneficiaries.educonnect.educonnect_connector.get_saml_client")
    @pytest.mark.features(ENABLE_EDUCONNECT_AUTHENTICATION=True)
    def test_educonnect_subscription(self, mock_get_educonnect_saml_client, client, app):
        ine_hash = "5ba682c0fc6a05edf07cd8ed0219258f"
        user = users_factories.UserFactory(dateOfBirth=datetime(2004, 1, 1), firstName=None, lastName=None)
        access_token = create_access_token(identity=user.email, additional_claims={"user_claims": {"user_id": user.id}})
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
        assert (
            subscription_api.get_user_subscription_state(user).next_step
            == subscription_schemas.SubscriptionStep.IDENTITY_CHECK
        )

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
        assert (
            subscription_api.get_user_subscription_state(user).next_step
            == subscription_schemas.SubscriptionStep.HONOR_STATEMENT
        )

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
    class NoNextStepTest:
        @pytest.mark.parametrize("age", [14, 19, 20, 21])
        def test_ineligible_user(self, age):
            user = users_factories.UserFactory(age=age)
            assert subscription_api.get_user_subscription_state(user).next_step is None

        def test_next_subscription_step_beneficiary(self):
            user = users_factories.BeneficiaryGrant18Factory()
            assert subscription_api.get_user_subscription_state(user).next_step is None

        @pytest.mark.parametrize("age", [15, 16, 17, 18])
        def test_no_step_after_ko_admin_review(self, age):
            user = users_factories.UserFactory(age=age)
            subscription_factories.BeneficiaryFraudReviewFactory(
                user=user, review=subscription_models.FraudReviewStatus.KO
            )

            next_step = subscription_api.get_user_subscription_state(user).next_step

            assert next_step is None

        @pytest.mark.features(ENABLE_EDUCONNECT_AUTHENTICATION=True)
        def test_next_subscription_step_underage_finished(self):
            user = users_factories.UserFactory(
                age=17,
                city="Zanzibar",
                activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            )
            subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
            subscription_factories.BeneficiaryFraudCheckFactory(
                type=subscription_models.FraudCheckType.HONOR_STATEMENT,
                resultContent=None,
                user=user,
                status=subscription_models.FraudCheckStatus.OK,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.UBBLE,
                status=subscription_models.FraudCheckStatus.PENDING,
            )

            next_step = subscription_api.get_user_subscription_state(user).next_step

            assert next_step is None

        def test_eighteen_year_old_subscription_finished(self):
            user = users_factories.UserFactory(
                age=18,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
                address="3 rue du quai",
                activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
            )
            subscription_factories.ProfileCompletionFraudCheckFactory(
                user=user, eligibilityType=users_models.EligibilityType.AGE17_18
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.UBBLE,
                status=subscription_models.FraudCheckStatus.PENDING,
                eligibilityType=users_models.EligibilityType.AGE17_18,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                type=subscription_models.FraudCheckType.HONOR_STATEMENT,
                resultContent=None,
                user=user,
                status=subscription_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.AGE17_18,
            )

            next_step = subscription_api.get_user_subscription_state(user).next_step

            assert next_step is None

        def test_free_subscription_finished(self):
            user = users_factories.UserFactory(
                age=15,
                address="3 rue du quai",
                activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
            )
            subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
            subscription_factories.HonorStatementFraudCheckFactory(user=user)

            next_step = subscription_api.get_user_subscription_state(user).next_step

            assert next_step is None

        @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=1))
        def test_17_18_transition_after_decree(self):
            user = users_factories.BeneficiaryFactory(age=17)

            # Assert factory does what we expect
            assert user.deposit.amount == 50
            assert user.deposit.type == finance_models.DepositType.GRANT_17_18
            next_step = subscription_api.get_user_subscription_state(user).next_step
            assert next_step is None
            assert user.is_beneficiary

            with time_machine.travel(datetime.now() + relativedelta(years=1)):
                next_step = subscription_api.get_user_subscription_state(user).next_step
                assert next_step == subscription_schemas.SubscriptionStep.PHONE_VALIDATION

                subscription_factories.PhoneValidationFraudCheckFactory(user=user)
                user.phoneNumber = "+33606060606"

                subscription_api.activate_beneficiary_if_no_missing_step(user)  # should not activate yet
                next_step = subscription_api.get_user_subscription_state(user).next_step
                assert next_step == subscription_schemas.SubscriptionStep.PROFILE_COMPLETION

                subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

                subscription_api.activate_beneficiary_if_no_missing_step(user)  # should not activate yet
                next_step = subscription_api.get_user_subscription_state(user).next_step
                assert next_step == subscription_schemas.SubscriptionStep.HONOR_STATEMENT

                subscription_factories.HonorStatementFraudCheckFactory(user=user)

                next_step = subscription_api.get_user_subscription_state(user).next_step
                assert next_step is None

                subscription_api.activate_beneficiary_if_no_missing_step(user)
                subscription_state = subscription_api.get_user_subscription_state(user)
                assert subscription_state.young_status.status_type == young_status.YoungStatusType.BENEFICIARY
                assert user.is_beneficiary
                assert user.deposit.amount == 50 + 150
                assert user.recreditAmountToShow == 150
                assert mails_testing.outbox[0]["params"]["CREDIT"] == 150

        @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=1))
        def test_user_with_modified_birth_date_can_get_their_deposit_activated(self):
            user = users_factories.BeneficiaryFactory(age=17)

            # Assert factory does what we expect
            assert user.deposit.amount == 50
            assert user.deposit.type == finance_models.DepositType.GRANT_17_18
            next_step = subscription_api.get_user_subscription_state(user).next_step
            assert next_step is None
            assert user.is_beneficiary

            # then the user is 18 yo, due to an admin action
            users_api.update_user_info(
                user,
                author=users_factories.AdminFactory(),
                validated_birth_date=user.birth_date - relativedelta(years=1),
            )

            # They should be able to finish the subscription steps
            assert user.age == 18
            next_step = subscription_api.get_user_subscription_state(user).next_step
            assert next_step == subscription_schemas.SubscriptionStep.PHONE_VALIDATION

            subscription_factories.PhoneValidationFraudCheckFactory(user=user)
            user.phoneNumber = "+33606060606"

            subscription_api.activate_beneficiary_if_no_missing_step(user)  # should not activate yet
            next_step = subscription_api.get_user_subscription_state(user).next_step
            assert next_step == subscription_schemas.SubscriptionStep.PROFILE_COMPLETION

            subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

            subscription_api.activate_beneficiary_if_no_missing_step(user)  # should not activate yet
            next_step = subscription_api.get_user_subscription_state(user).next_step
            assert next_step == subscription_schemas.SubscriptionStep.HONOR_STATEMENT

            subscription_factories.HonorStatementFraudCheckFactory(user=user)

            next_step = subscription_api.get_user_subscription_state(user).next_step
            assert next_step is None

            subscription_api.activate_beneficiary_if_no_missing_step(user)
            subscription_state = subscription_api.get_user_subscription_state(user)
            assert subscription_state.young_status.status_type == young_status.YoungStatusType.BENEFICIARY
            assert user.is_beneficiary
            assert user.deposit.amount == 200

        def test_user_with_ubble_modified_birth_date_can_get_their_deposit_activated(self):
            user = users_factories.ProfileCompletedUserFactory(
                age=16, beneficiaryFraudChecks__eligibilityType=users_models.EligibilityType.UNDERAGE
            )
            # Ubble sets birth_date to a year before, user is 17yo
            ubble_birth_date = user.birth_date - relativedelta(years=1)
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.UBBLE,
                status=subscription_models.FraudCheckStatus.OK,
                resultContent=subscription_factories.UbbleContentFactory(birth_date=ubble_birth_date),
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )
            user.validatedBirthDate = ubble_birth_date
            subscription_factories.HonorStatementFraudCheckFactory(user=user)
            subscription_api.activate_beneficiary_if_no_missing_step(user)

            assert user.age == 17
            assert user.is_beneficiary

            with time_machine.travel(datetime.now() + relativedelta(years=1)):
                # They should be able to finish the subscription steps
                assert user.age == 18
                next_step = subscription_api.get_user_subscription_state(user).next_step
                assert next_step == subscription_schemas.SubscriptionStep.PHONE_VALIDATION

                subscription_factories.PhoneValidationFraudCheckFactory(user=user)
                user.phoneNumber = "+33606060606"

                subscription_api.activate_beneficiary_if_no_missing_step(user)  # should not activate yet
                next_step = subscription_api.get_user_subscription_state(user).next_step
                assert next_step == subscription_schemas.SubscriptionStep.PROFILE_COMPLETION

                subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

                subscription_api.activate_beneficiary_if_no_missing_step(user)  # should not activate yet
                next_step = subscription_api.get_user_subscription_state(user).next_step
                assert next_step == subscription_schemas.SubscriptionStep.HONOR_STATEMENT

                subscription_factories.HonorStatementFraudCheckFactory(user=user)

                next_step = subscription_api.get_user_subscription_state(user).next_step
                assert next_step is None

                subscription_api.activate_beneficiary_if_no_missing_step(user)
                subscription_state = subscription_api.get_user_subscription_state(user)
                assert subscription_state.young_status.status_type == young_status.YoungStatusType.BENEFICIARY
                assert user.is_beneficiary

    class NextStepPhoneValidationTest:
        def test_next_subscription_step_phone_validation(self):
            user = users_factories.UserFactory(age=18)
            assert (
                subscription_api.get_user_subscription_state(user).next_step
                == subscription_schemas.SubscriptionStep.PHONE_VALIDATION
            )

        def test_no_phone_validation_step_for_underage(self):
            user = users_factories.UserFactory(age=17)

            next_step = subscription_api.get_user_subscription_state(user).next_step

            assert next_step != subscription_schemas.SubscriptionStep.PHONE_VALIDATION

        def test_next_subscription_step_phone_validation_skipped(self):
            user = users_factories.UserFactory(
                age=18, phoneValidationStatus=users_models.PhoneValidationStatusType.SKIPPED_BY_SUPPORT
            )
            assert subscription_api.get_user_subscription_state(user).next_step in (
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
            )

        @time_machine.travel("2019-01-01")
        def test_next_step_phone_validation_after_dms_succeded_at_19(self):
            user = users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 1))
            with time_machine.travel("2018-01-01"):
                subscription_factories.BeneficiaryFraudCheckFactory(
                    user=user,
                    type=subscription_models.FraudCheckType.DMS,
                    status=subscription_models.FraudCheckStatus.KO,
                )
            assert (
                subscription_api.get_user_subscription_state(user).next_step
                == subscription_schemas.SubscriptionStep.PHONE_VALIDATION
            )

        @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=2))
        @pytest.mark.parametrize("age", [19, 20])
        def test_step_phone_validation_for_old_user_that_registered_at_18(self, age):
            birth_date = date.today() - relativedelta(years=age, months=1)
            user = users_factories.UserFactory(dateOfBirth=birth_date)
            date_when_user_was_eighteen = birth_date + relativedelta(years=18, months=1)
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.UBBLE,
                eligibilityType=users_models.EligibilityType.AGE17_18,
                dateCreated=date_when_user_was_eighteen,
            )

            next_step = subscription_api.get_user_subscription_state(user).next_step

            assert next_step == subscription_schemas.SubscriptionStep.PHONE_VALIDATION

    class NextStepProfileCompletionTest:
        def test_next_subscription_step_underage_profile_completion(self):
            user = users_factories.UserFactory(age=17, city=None)
            assert (
                subscription_api.get_user_subscription_state(user).next_step
                == subscription_schemas.SubscriptionStep.PROFILE_COMPLETION
            )

        def test_next_subscription_step_18_profile_completion(self):
            user = users_factories.UserFactory(
                age=18, phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED, city=None
            )
            year_when_user_was_seventeen = date_utils.get_naive_utc_now() - relativedelta(years=1, months=1)
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
                status=subscription_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.AGE17_18,
                resultContent=subscription_factories.ProfileCompletionContentFactory(),
                dateCreated=year_when_user_was_seventeen,
            )

            next_step = subscription_api.get_user_subscription_state(user).next_step

            assert next_step == subscription_schemas.SubscriptionStep.PROFILE_COMPLETION

        def test_user_with_pending_dms_application_should_not_fill_profile(self):
            user = users_factories.UserFactory(
                age=18,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            )
            # Pending DMS application
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.DMS,
                status=subscription_models.FraudCheckStatus.PENDING,
                eligibilityType=users_models.EligibilityType.AGE18,
                resultContent=subscription_factories.DMSContentFactory(city="Brockton Bay"),
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                type=subscription_models.FraudCheckType.HONOR_STATEMENT,
                resultContent=None,
                user=user,
                status=subscription_models.FraudCheckStatus.OK,
            )

            next_step = subscription_api.get_user_subscription_state(user).next_step

            assert next_step is None

        @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME)
        def test_underage_user_with_pending_dms_application_should_not_fill_profile(self):
            before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
            fifteen_years_ago = date_utils.get_naive_utc_now() - relativedelta(years=15, days=1)
            user = users_factories.UserFactory(dateOfBirth=fifteen_years_ago)
            # Pending DMS application
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.DMS,
                status=subscription_models.FraudCheckStatus.PENDING,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                resultContent=subscription_factories.DMSContentFactory(city="Brockton Bay"),
                dateCreated=before_decree,
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.HONOR_STATEMENT,
                status=subscription_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                resultContent=None,
                dateCreated=before_decree,
            )

            next_step = subscription_api.get_user_subscription_state(user).next_step

            assert next_step is None

        @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME)
        @pytest.mark.parametrize("age", [15, 16, 17])
        def test_underage_user_when_registered_before_decree(self, age):
            birth_date = date.today() - relativedelta(years=age, months=1)
            user = users_factories.UserFactory(dateOfBirth=birth_date)
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.UBBLE,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
                dateCreated=settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1),
            )

            next_step = subscription_api.get_user_subscription_state(user).next_step

            assert next_step == subscription_schemas.SubscriptionStep.PROFILE_COMPLETION

    class NextStepHonorStatementTest:
        @pytest.mark.features(ENABLE_EDUCONNECT_AUTHENTICATION=True)
        def test_next_subscription_step_underage_honor_statement(self):
            user = users_factories.UserFactory(
                age=17,
                city="Zanzibar",
                activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
            )
            subscription_factories.ProfileCompletionFraudCheckFactory(
                user=user, eligibilityType=users_models.EligibilityType.UNDERAGE
            )
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.EDUCONNECT,
                status=subscription_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            next_step = subscription_api.get_user_subscription_state(user).next_step

            assert next_step == subscription_schemas.SubscriptionStep.HONOR_STATEMENT

        def test_underage_ubble_already_performed(self):
            user = users_factories.UserFactory(
                age=18,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
                city="Zanzibar",
                activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
            )
            subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.UBBLE,
                status=subscription_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            assert (
                subscription_api.get_user_subscription_state(user).next_step
                == subscription_schemas.SubscriptionStep.HONOR_STATEMENT
            )

        def test_underage_dms_alread_performed(self):
            user = users_factories.UserFactory(
                age=18,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
                city="Zanzibar",
                activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
            )
            subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.DMS,
                status=subscription_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.UNDERAGE,
            )

            assert (
                subscription_api.get_user_subscription_state(user).next_step
                == subscription_schemas.SubscriptionStep.HONOR_STATEMENT
            )

        def test_next_subscription_step_honor_statement(self):
            user = users_factories.UserFactory(
                age=18,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
                city="Zanzibar",
                activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
            )
            subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.UBBLE,
                status=subscription_models.FraudCheckStatus.PENDING,
                eligibilityType=users_models.EligibilityType.AGE18,
            )

            assert (
                subscription_api.get_user_subscription_state(user).next_step
                == subscription_schemas.SubscriptionStep.HONOR_STATEMENT
            )

    class NextStepIdentityCheckTest:
        def test_next_subscription_step_identity_check(self):
            user = users_factories.UserFactory(
                age=18,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
                city="Zanzibar",
                activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value,
            )
            subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
            subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.UBBLE,
                status=subscription_models.FraudCheckStatus.STARTED,
                eligibilityType=users_models.EligibilityType.AGE18,
            )

            assert (
                subscription_api.get_user_subscription_state(user).next_step
                == subscription_schemas.SubscriptionStep.IDENTITY_CHECK
            )

        @pytest.mark.parametrize(
            "feature_flags,user_age,expected_result",
            [
                # User 18
                (
                    {"ENABLE_UBBLE": True},
                    18,
                    [subscription_schemas.IdentityCheckMethod.UBBLE],
                ),
                (
                    {"ENABLE_UBBLE": False},
                    18,
                    [],
                ),
                # User 15 - 17
                # Public schools -> force EDUCONNECT when possible
                (
                    {
                        "ENABLE_EDUCONNECT_AUTHENTICATION": True,
                        "ENABLE_UBBLE": True,
                    },
                    17,
                    [
                        subscription_schemas.IdentityCheckMethod.EDUCONNECT,
                        subscription_schemas.IdentityCheckMethod.UBBLE,
                    ],
                ),
                (
                    {
                        "ENABLE_EDUCONNECT_AUTHENTICATION": True,
                        "ENABLE_UBBLE": False,
                    },
                    17,
                    [subscription_schemas.IdentityCheckMethod.EDUCONNECT],
                ),
                (
                    {
                        "ENABLE_EDUCONNECT_AUTHENTICATION": False,
                        "ENABLE_UBBLE": True,
                    },
                    15,
                    [subscription_schemas.IdentityCheckMethod.UBBLE],
                ),
            ],
        )
        def test_get_allowed_identity_check_methods(self, features, feature_flags, user_age, expected_result):
            dateOfBirth = datetime.today() - relativedelta(years=user_age, months=1)
            user = users_factories.UserFactory(dateOfBirth=dateOfBirth)
            for feature_name in feature_flags:
                setattr(features, feature_name, feature_flags[feature_name])
            assert subscription_api.get_allowed_identity_check_methods(user) == expected_result

    class NextStepMaintenanceTest:
        @pytest.mark.parametrize(
            "feature_flags,user_age,expected_result",
            [
                (
                    {"ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18": True},
                    18,
                    subscription_schemas.MaintenancePageType.WITH_DMS,
                ),
                (
                    {"ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18": False},
                    18,
                    subscription_schemas.MaintenancePageType.WITHOUT_DMS,
                ),
                (
                    {"ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE": True},
                    17,
                    subscription_schemas.MaintenancePageType.WITH_DMS,
                ),
                (
                    {"ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE": False},
                    15,
                    subscription_schemas.MaintenancePageType.WITHOUT_DMS,
                ),
            ],
        )
        @patch("pcapi.core.subscription.api.get_allowed_identity_check_methods", return_value=[])
        def test_get_maintenance_page_type(self, _, features, feature_flags, user_age, expected_result):
            dateOfBirth = datetime.today() - relativedelta(years=user_age, months=1)
            user = users_factories.UserFactory(dateOfBirth=dateOfBirth)
            for feature_name in feature_flags:
                setattr(features, feature_name, feature_flags[feature_name])
            assert subscription_api.get_maintenance_page_type(user) == expected_result


@pytest.mark.usefixtures("db_session")
class OverflowSubscriptionLimitationTest:
    @pytest.mark.features(ENABLE_UBBLE_SUBSCRIPTION_LIMITATION=True)
    @pytest.mark.parametrize("age", [15, 16, 17, 18])
    def test__is_ubble_allowed_if_subscription_overflow(self, age):
        # user birthday is in settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS days
        birth_date = date_utils.get_naive_utc_now() - relativedelta(years=age + 1)
        birth_date += relativedelta(days=settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS - 1)

        # the user has:
        # email v
        user_approching_birthday = users_factories.UserFactory(dateOfBirth=birth_date)

        users_utils.get_age_from_birth_date(user_approching_birthday.dateOfBirth)
        user_not_allowed = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now()
            - relativedelta(years=age, days=settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS + 10)
        )

        assert subscription_api._is_ubble_allowed_if_subscription_overflow(user_approching_birthday)
        assert not subscription_api._is_ubble_allowed_if_subscription_overflow(user_not_allowed)

    @pytest.mark.features(ENABLE_UBBLE_SUBSCRIPTION_LIMITATION=False)
    def test_subscription_is_possible_if_flag_is_false(self):
        user = users_factories.UserFactory()
        assert subscription_api._is_ubble_allowed_if_subscription_overflow(user)


@pytest.mark.usefixtures("db_session")
class CommonSubscriptionTest:
    def test_handle_eligibility_difference_between_declaration_and_identity_provider_no_difference(self):
        user = users_factories.UserFactory()
        fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        assert (
            subscription_api.handle_eligibility_difference_between_declaration_and_identity_provider(user, fraud_check)
            == fraud_check
        )

    def test_handle_eligibility_difference_between_declaration_and_identity_provider_eligibility_diff(self):
        user = users_factories.UserFactory()
        fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=subscription_factories.UbbleContentFactory(),  # default age is 18
        )
        # Profile completion fraud check
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=subscription_factories.ProfileCompletionContentFactory(),
        )
        # Honor statement fraud check
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=subscription_factories.ProfileCompletionContentFactory(),
        )
        assert (
            subscription_api.handle_eligibility_difference_between_declaration_and_identity_provider(user, fraud_check)
            != fraud_check
        )

        user_fraud_checks = sorted(
            db.session.query(subscription_models.BeneficiaryFraudCheck).filter_by(user=user).all(), key=lambda x: x.id
        )
        assert len(user_fraud_checks) == 6
        assert user_fraud_checks[0].eligibilityType == users_models.EligibilityType.UNDERAGE
        assert user_fraud_checks[0].type == subscription_models.FraudCheckType.UBBLE
        assert user_fraud_checks[0].reason == "Eligibility type changed by the identity provider"
        assert user_fraud_checks[0].status == subscription_models.FraudCheckStatus.CANCELED

        assert user_fraud_checks[1].eligibilityType == users_models.EligibilityType.UNDERAGE
        assert user_fraud_checks[1].type == subscription_models.FraudCheckType.PROFILE_COMPLETION
        assert user_fraud_checks[1].reason == "Eligibility type changed by the identity provider"
        assert user_fraud_checks[1].status == subscription_models.FraudCheckStatus.CANCELED

        assert user_fraud_checks[2].eligibilityType == users_models.EligibilityType.UNDERAGE
        assert user_fraud_checks[2].type == subscription_models.FraudCheckType.HONOR_STATEMENT
        assert user_fraud_checks[2].reason == "Eligibility type changed by the identity provider"
        assert user_fraud_checks[2].status == subscription_models.FraudCheckStatus.CANCELED

        assert user_fraud_checks[3].eligibilityType == users_models.EligibilityType.AGE17_18
        assert user_fraud_checks[3].type == subscription_models.FraudCheckType.UBBLE
        assert user_fraud_checks[3].status == subscription_models.FraudCheckStatus.PENDING

        assert user_fraud_checks[4].eligibilityType == users_models.EligibilityType.AGE17_18
        assert user_fraud_checks[4].type == subscription_models.FraudCheckType.PROFILE_COMPLETION
        assert user_fraud_checks[4].status == subscription_models.FraudCheckStatus.OK

        assert user_fraud_checks[5].eligibilityType == users_models.EligibilityType.AGE17_18
        assert user_fraud_checks[5].type == subscription_models.FraudCheckType.HONOR_STATEMENT
        assert user_fraud_checks[5].status == subscription_models.FraudCheckStatus.OK

    def test_handle_eligibility_difference_between_declaration_and_identity_provider_unreadable_document(self):
        user = users_factories.UserFactory()
        fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.PENDING,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=subscription_factories.UbbleContentFactory(birth_date=None),  # default age is 18
        )
        assert (
            subscription_api.handle_eligibility_difference_between_declaration_and_identity_provider(user, fraud_check)
            == fraud_check
        )


@pytest.mark.usefixtures("db_session")
class UpdateBirthDateTest:
    def test_update_birth_date_when_not_yet_underage_beneficiary(self):
        user = users_factories.BaseUserFactory(age=15)
        new_birth_date = user.dateOfBirth - relativedelta(months=2)

        assert user.validatedBirthDate is None

        with atomic():
            subscription_api.update_user_birth_date_if_not_beneficiary(user, new_birth_date)

        assert user.validatedBirthDate == new_birth_date.date()

    def test_update_birth_date_when_eligible_to_upgrade_age18_based_on_user_birth_date(self):
        with time_machine.travel(date_utils.get_naive_utc_now() - relativedelta(years=1)):
            user = users_factories.BeneficiaryFactory(age=17)

        assert user.validatedBirthDate == user.dateOfBirth.date()

        new_birth_date = user.dateOfBirth - relativedelta(months=2)
        with atomic():
            subscription_api.update_user_birth_date_if_not_beneficiary(user, new_birth_date)

        assert user.validatedBirthDate == new_birth_date.date()

    def test_does_not_update_birth_date_when_eligible_to_upgrade_age18_based_on_identity_check_birth_date(self):
        with time_machine.travel(date_utils.get_naive_utc_now() - relativedelta(months=11)):
            user = users_factories.BeneficiaryFactory(age=17)

        assert user.validatedBirthDate == user.dateOfBirth.date()

        new_birth_date = user.dateOfBirth - relativedelta(months=2)
        subscription_api.update_user_birth_date_if_not_beneficiary(user, new_birth_date)

        assert user.validatedBirthDate == user.dateOfBirth.date()

    def test_does_not_update_birth_date_when_not_upgrading(self):
        user = users_factories.BeneficiaryFactory(age=17)

        assert user.validatedBirthDate == user.dateOfBirth.date()

        new_birth_date = user.dateOfBirth - relativedelta(months=2)
        subscription_api.update_user_birth_date_if_not_beneficiary(user, new_birth_date)

        assert user.validatedBirthDate == user.dateOfBirth.date()

    def test_does_not_update_birth_date_when_already_age18(self):
        user = users_factories.BeneficiaryFactory(age=18)

        assert user.validatedBirthDate == user.dateOfBirth.date()

        new_birth_date = user.dateOfBirth - relativedelta(months=2)
        subscription_api.update_user_birth_date_if_not_beneficiary(user, new_birth_date)

        assert user.validatedBirthDate == user.dateOfBirth.date()


@pytest.mark.usefixtures("db_session")
class SubscriptionItemTest:
    def test_phone_validation_item(self):
        user = users_factories.UserFactory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            age=18,
        )
        assert (
            subscription_api.get_phone_validation_subscription_item(user, users_models.EligibilityType.AGE18).status
            == subscription_schemas.SubscriptionItemStatus.OK
        )

    def test_phone_validation_item_with_eligible_user_todo(self):
        user = users_factories.UserFactory(age=18)
        assert (
            subscription_api.get_phone_validation_subscription_item(user, users_models.EligibilityType.AGE17_18).status
            == subscription_schemas.SubscriptionItemStatus.TODO
        )

    @pytest.mark.features(ENABLE_PHONE_VALIDATION=True)
    def test_phone_validation_item_with_eligible_user_validation_todo(self):
        user = users_factories.UserFactory(age=18)
        assert (
            subscription_api.get_phone_validation_subscription_item(user, users_models.EligibilityType.AGE17_18).status
            == subscription_schemas.SubscriptionItemStatus.TODO
        )

    @pytest.mark.features(ENABLE_PHONE_VALIDATION=False)
    def test_phone_validation_item_with_eligible_user_done_without_validation(self):
        user = users_factories.UserFactory(age=18, _phoneNumber="0123456789")
        assert (
            subscription_api.get_phone_validation_subscription_item(user, users_models.EligibilityType.AGE17_18).status
            == subscription_schemas.SubscriptionItemStatus.OK
        )

    def test_phone_validation_item_ko(self):
        user = users_factories.UserFactory(age=18)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            status=subscription_models.FraudCheckStatus.KO,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            eligibilityType=users_models.EligibilityType.AGE17_18,
        )

        assert (
            subscription_api.get_phone_validation_subscription_item(user, users_models.EligibilityType.AGE17_18).status
            == subscription_schemas.SubscriptionItemStatus.KO
        )


@pytest.mark.usefixtures("db_session")
class IdentityCheckSubscriptionStatusTest:
    def test_not_eligible(self):
        user = users_factories.UserFactory(age=20)

        underage_status = subscription_api.get_identity_check_fraud_status(
            user, users_models.EligibilityType.UNDERAGE, None
        )
        age_18_status = subscription_api.get_identity_check_fraud_status(
            user,
            users_models.EligibilityType.AGE18,
            subscription_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.AGE18),
        )

        assert underage_status == subscription_schemas.SubscriptionItemStatus.VOID
        assert age_18_status == subscription_schemas.SubscriptionItemStatus.VOID

    def test_eligible_ex_underage_with_educonnect_has_to_id_check_again(self):
        user = users_factories.UserFactory(age=18, roles=[users_models.UserRole.UNDERAGE_BENEFICIARY])
        year_when_user_was_17 = date_utils.get_naive_utc_now() - relativedelta(years=1)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.OK,
            dateCreated=year_when_user_was_17,
        )

        underage_status = subscription_api.get_identity_check_fraud_status(
            user,
            users_models.EligibilityType.UNDERAGE,
            subscription_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.UNDERAGE),
        )
        age_18_status = subscription_api.get_identity_check_fraud_status(
            user,
            users_models.EligibilityType.AGE17_18,
            subscription_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.AGE17_18),
        )

        assert underage_status == subscription_schemas.SubscriptionItemStatus.OK
        assert age_18_status == subscription_schemas.SubscriptionItemStatus.TODO

    def test_dms_started_ubble_ko(self):
        user = users_factories.UserFactory(age=20)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.KO,
        )

        status = subscription_api.get_identity_check_fraud_status(
            user,
            users_models.EligibilityType.AGE17_18,
            subscription_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.AGE17_18),
        )

        assert status == subscription_schemas.SubscriptionItemStatus.PENDING

    def test_dms_error(self):
        user = users_factories.UserFactory(age=16)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.KO,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.ERROR,
        )

        underage_status = subscription_api.get_identity_check_fraud_status(
            user,
            users_models.EligibilityType.UNDERAGE,
            subscription_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.UNDERAGE),
        )
        age_18_status = subscription_api.get_identity_check_fraud_status(
            user,
            users_models.EligibilityType.AGE18,
            subscription_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.AGE18),
        )

        assert underage_status == subscription_schemas.SubscriptionItemStatus.KO
        assert age_18_status == subscription_schemas.SubscriptionItemStatus.VOID

    def test_ubble_and_educonnect_ko(self):
        user = users_factories.UserFactory(age=17)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.KO,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.KO,
        )

        status = subscription_api.get_identity_check_fraud_status(
            user,
            users_models.EligibilityType.AGE17_18,
            subscription_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.AGE17_18),
        )

        assert status == subscription_schemas.SubscriptionItemStatus.KO

    @pytest.mark.parametrize(
        "fraud_check_type", [subscription_models.FraudCheckType.UBBLE, subscription_models.FraudCheckType.DMS]
    )
    def test_underage_valid_id_check_for_18(self, fraud_check_type):
        user = users_factories.UserFactory(age=18)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=fraud_check_type,
            status=subscription_models.FraudCheckStatus.OK,
        )

        age18_status = subscription_api.get_identity_check_fraud_status(
            user,
            users_models.EligibilityType.AGE17_18,
            subscription_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.AGE17_18),
        )

        assert age18_status == subscription_schemas.SubscriptionItemStatus.OK

    @pytest.mark.parametrize(
        "fraud_check_type", [subscription_models.FraudCheckType.UBBLE, subscription_models.FraudCheckType.DMS]
    )
    def test_17_valid_id_check_for_18(self, fraud_check_type):
        user = users_factories.UserFactory(age=18)
        year_when_user_was_17 = date_utils.get_naive_utc_now() - relativedelta(years=1)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            type=fraud_check_type,
            status=subscription_models.FraudCheckStatus.OK,
            dateCreated=year_when_user_was_17,
        )

        age18_status = subscription_api.get_identity_check_fraud_status(
            user,
            users_models.EligibilityType.AGE17_18,
            subscription_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.AGE17_18),
        )

        assert age18_status == subscription_schemas.SubscriptionItemStatus.OK

    def test_17_educonnect_not_valid_for_18(self):
        user = users_factories.UserFactory(age=18)
        year_when_user_was_17 = date_utils.get_naive_utc_now() - relativedelta(years=1)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.OK,
            dateCreated=year_when_user_was_17,
        )

        age18_status = subscription_api.get_identity_check_fraud_status(
            user,
            users_models.EligibilityType.AGE17_18,
            subscription_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.AGE17_18),
        )

        assert age18_status == subscription_schemas.SubscriptionItemStatus.TODO


@pytest.mark.usefixtures("db_session")
class NeedsToPerformeIdentityCheckTest:
    AGE16_ELIGIBLE_BIRTH_DATE = date_utils.get_naive_utc_now() - relativedelta(years=16, months=4)
    AGE18_ELIGIBLE_BIRTH_DATE = date_utils.get_naive_utc_now() - relativedelta(years=18, months=4)
    AGE20_ELIGIBLE_BIRTH_DATE = date_utils.get_naive_utc_now() - relativedelta(years=20, months=4)

    def test_not_eligible(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE20_ELIGIBLE_BIRTH_DATE)

        assert (
            subscription_api.get_identity_check_fraud_status(
                user,
                user.eligibility,
                subscription_repository.get_relevant_identity_fraud_check(user, user.eligibility),
            )
            == subscription_schemas.SubscriptionItemStatus.VOID
        )

    def test_ex_underage_eligible_18(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE, roles=[users_models.UserRole.UNDERAGE_BENEFICIARY]
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.OK,
        )

        assert (
            subscription_api.get_user_subscription_state(user).next_step
            == subscription_schemas.SubscriptionStep.PHONE_VALIDATION
        )

    def test_ubble_underage_eligible_18_does_not_need_to_redo(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE, roles=[users_models.UserRole.UNDERAGE_BENEFICIARY]
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
        )

        assert (
            subscription_api.get_identity_check_fraud_status(
                user,
                user.eligibility,
                subscription_repository.get_relevant_identity_fraud_check(user, user.eligibility),
            )
            == subscription_schemas.SubscriptionItemStatus.OK
        )

    def test_ubble_started(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.STARTED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
        )

        assert (
            subscription_api.get_user_subscription_state(user).next_step
            == subscription_schemas.SubscriptionStep.IDENTITY_CHECK
        )

    def test_dms_started(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE16_ELIGIBLE_BIRTH_DATE)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        assert (
            not subscription_api.get_user_subscription_state(user).next_step
            == subscription_schemas.SubscriptionStep.IDENTITY_CHECK
        )

    def test_educonnect_ok(self):
        user = users_factories.UserFactory(dateOfBirth=self.AGE16_ELIGIBLE_BIRTH_DATE)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.OK,
        )

        assert (
            not subscription_api.get_user_subscription_state(user).next_step
            == subscription_schemas.SubscriptionStep.IDENTITY_CHECK
        )


@pytest.mark.usefixtures("db_session")
class CompleteProfileTest:
    def test_when_profile_was_proviously_cancelled(self):
        """
        This was a bug when a user previously completed profile but the BeneficiaryCancelled
        was cancelled because of "eligibility_changed" scenario
        """
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.CANCELED,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            reasonCodes=[subscription_models.FraudReasonCode.ELIGIBILITY_CHANGED],
        )

        subscription_api.complete_profile(
            user,
            address="address",
            city="city",
            postal_code="12400",
            activity=users_models.ActivityEnum.STUDENT,
            first_name="harry",
            last_name="cover",
        )

        assert subscription_repository.get_completed_profile_check(user, users_models.EligibilityType.AGE17_18)
        assert (
            db.session.query(subscription_models.BeneficiaryFraudCheck)
            .filter_by(
                userId=user.id,
                type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
                status=subscription_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.AGE17_18,
            )
            .count()
            == 1
        )


@pytest.mark.usefixtures("db_session")
class ActivateBeneficiaryIfNoMissingStepTest:
    def test_activation_success(self):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName="profile-firstname",
            lastName="profile-lastname",
        )
        identity_firstname = "Yolan"
        identity_lastname = "Mac Doumy"
        identity_birth_date = date.today() - relativedelta(years=18, months=3, days=1)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
            resultContent=subscription_factories.UbbleContentFactory(
                first_name=identity_firstname,
                last_name=identity_lastname,
                birth_date=identity_birth_date.isoformat(),
            ),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        is_success = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_success
        assert user.is_beneficiary
        assert user.firstName == identity_firstname
        assert user.lastName == identity_lastname
        assert user.validatedBirthDate == identity_birth_date
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.ACCEPTED_AS_BENEFICIARY_V3.value
        )

    def test_activation_fails_when_no_result_content(self):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
            resultContent=None,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        is_success = subscription_api.activate_beneficiary_if_no_missing_step(user)
        assert not is_success

    def test_admin_review_ko(self):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName="profile-firstname",
            lastName="profile-lastname",
        )
        identity_firstname = "Yolan"
        identity_lastname = "Mac Doumy"
        identity_birth_date = date.today() - relativedelta(years=18, months=3, days=1)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
            resultContent=subscription_factories.UbbleContentFactory(
                first_name=identity_firstname,
                last_name=identity_lastname,
                birth_date=identity_birth_date.isoformat(),
            ),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        subscription_factories.BeneficiaryFraudReviewFactory(user=user, review=subscription_models.FraudReviewStatus.KO)

        is_success = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert not is_success
        assert not user.is_beneficiary

    def test_missing_step(self):
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName=None,
            lastName=None,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
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
        birth_date = date_utils.get_naive_utc_now() - relativedelta(years=18)

        users_factories.BeneficiaryGrant18Factory(firstName=first_name, lastName=last_name, dateOfBirth=birth_date)

        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName=None,
            lastName=None,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        to_invalidate_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            resultContent=subscription_factories.UbbleContentFactory(
                first_name=first_name, last_name=last_name, birth_date=birth_date.date().isoformat()
            ),
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        result = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert not result
        assert not user.is_beneficiary
        assert to_invalidate_check.status == subscription_models.FraudCheckStatus.SUSPICIOUS
        assert to_invalidate_check.reasonCodes == [subscription_models.FraudReasonCode.DUPLICATE_USER]
        assert user.firstName is None
        assert user.lastName is None

    AGE18_ELIGIBLE_BIRTH_DATE = date_utils.get_naive_utc_now() - relativedelta(years=18, months=4)
    UNDERAGE_ELIGIBLE_BIRTH_DATE = date_utils.get_naive_utc_now() - relativedelta(years=17, months=4)

    def eligible_user(
        self,
        validate_phone: bool,
        city: str | None = "Quito",
        is_underage: bool = False,
    ):
        phone_validation_status = users_models.PhoneValidationStatusType.VALIDATED if validate_phone else None
        return users_factories.UserFactory(
            dateOfBirth=self.AGE18_ELIGIBLE_BIRTH_DATE if not is_underage else self.UNDERAGE_ELIGIBLE_BIRTH_DATE,
            phoneValidationStatus=phone_validation_status,
            city=city,
            activity=users_models.ActivityEnum.STUDENT.value,
        )

    def test_activation_success_underage(self):
        user = self.eligible_user(validate_phone=False, is_underage=True)
        identity_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            status=subscription_models.FraudCheckStatus.OK,
            resultContent=subscription_factories.EduconnectContentFactory(
                first_name="Léo",
                last_name="Nard",
                birth_date=self.UNDERAGE_ELIGIBLE_BIRTH_DATE,
            ),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

        is_success = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_success
        assert user.is_beneficiary
        assert user.firstName == "Léo"
        assert user.lastName == "Nard"
        assert user.dateOfBirth.date() == self.UNDERAGE_ELIGIBLE_BIRTH_DATE.date()
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.ACCEPTED_AS_BENEFICIARY_V3.value
        )
        assert user.deposit.source == f"dossier FraudCheckType.EDUCONNECT [{identity_fraud_check.thirdPartyId}]"
        assert user.deposit.amount == 50
        assert user.recreditAmountToShow == 50

    def test_rejected_identity(self):
        user = self.eligible_user(validate_phone=False)

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, type=subscription_models.FraudCheckType.UBBLE, status=subscription_models.FraudCheckStatus.KO
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

        assert not subscription_api.activate_beneficiary_if_no_missing_step(user)
        assert not user.is_beneficiary

    def test_missing_profile_after_dms_application(self):
        user = self.eligible_user(validate_phone=True, city=None)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, type=subscription_models.FraudCheckType.DMS, status=subscription_models.FraudCheckStatus.OK
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
        )

        assert not subscription_api.activate_beneficiary_if_no_missing_step(user)
        assert not user.is_beneficiary

    def test_underage_ubble_valid_for_18(self):
        identity_firstname = "Yolan"
        identity_lastname = "Mac Doumy"
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName=identity_firstname,
            lastName=identity_lastname,
        )
        identity_birth_date = date.today() - relativedelta(years=18, months=3, days=1)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.UBBLE,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=subscription_factories.UbbleContentFactory(
                first_name=identity_firstname,
                last_name=identity_lastname,
                birth_date=identity_birth_date.isoformat(),
            ),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        is_success = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_success
        assert user.is_beneficiary
        assert user.firstName == identity_firstname
        assert user.lastName == identity_lastname
        assert user.validatedBirthDate == identity_birth_date
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.ACCEPTED_AS_BENEFICIARY_V3.value
        )

    def test_underage_dms_valid_for_18(self):
        identity_firstname = "Yolan"
        identity_lastname = "Mac Doumy"
        user = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            firstName=identity_firstname,
            lastName=identity_lastname,
        )
        identity_birth_date = date.today() - relativedelta(years=18, months=3, days=1)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            resultContent=subscription_factories.DMSContentFactory(
                first_name=identity_firstname,
                last_name=identity_lastname,
                birth_date=identity_birth_date.isoformat(),
            ),
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
        )

        is_success = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_success
        assert user.is_beneficiary
        assert user.firstName == identity_firstname
        assert user.lastName == identity_lastname
        assert user.validatedBirthDate == identity_birth_date
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.ACCEPTED_AS_BENEFICIARY_V3.value
        )

    def test_manual_review_is_required_for_post_19yo_dms(self):
        with time_machine.travel(date_utils.get_naive_utc_now() - relativedelta(days=1)):
            user = users_factories.ProfileCompletedUserFactory(age=19)

        dms_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
            resultContent=subscription_factories.DMSContentFactory(
                first_name=user.firstName,
                last_name=user.lastName,
                birth_date=user.birth_date.isoformat(),
            ),
        )

        assert subscription_api.requires_manual_review_before_activation(user, dms_fraud_check)

    def test_manual_review_is_not_required_for_post_19yo_dms_ko(self):
        user = users_factories.ProfileCompletedUserFactory(age=19)

        dms_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.KO,
            eligibilityType=users_models.EligibilityType.AGE18,
            resultContent=subscription_factories.DMSContentFactory(
                first_name=user.firstName,
                last_name=user.lastName,
                birth_date=user.birth_date.isoformat(),
            ),
        )

        assert not subscription_api.requires_manual_review_before_activation(user, dms_fraud_check)

    @time_machine.travel("2024-02-01")
    def test_manual_review_is_not_required_for_pre_19yo_dms(self):
        user = users_factories.ProfileCompletedUserFactory(age=19)

        with time_machine.travel(date_utils.get_naive_utc_now() - relativedelta(days=1)):
            dms_fraud_check = subscription_factories.BeneficiaryFraudCheckFactory(
                user=user,
                type=subscription_models.FraudCheckType.DMS,
                status=subscription_models.FraudCheckStatus.OK,
                eligibilityType=users_models.EligibilityType.AGE18,
                resultContent=subscription_factories.DMSContentFactory(
                    first_name=user.firstName,
                    last_name=user.lastName,
                    birth_date=user.birth_date.isoformat(),
                ),
            )

        assert not subscription_api.requires_manual_review_before_activation(user, dms_fraud_check)

    @time_machine.travel("2025-03-03")
    def test_pre_decree_underage_eligibility(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        user = users_factories.HonorStatementValidatedUserFactory(
            age=17, beneficiaryFraudChecks__dateCreated=before_decree, dateCreated=before_decree
        )

        is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_user_activated
        assert user.is_beneficiary
        assert user.deposit.type == finance_models.DepositType.GRANT_15_17
        assert user.deposit.amount == 30
        assert user.recreditAmountToShow == 30

    @time_machine.travel("2025-03-03")
    def test_pre_decree_at_17_when_registration_started_at_15(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        seventeen_years_ago = before_decree - relativedelta(years=17)
        year_when_user_was_fifteen = before_decree - relativedelta(years=2)
        user = users_factories.HonorStatementValidatedUserFactory(
            validatedBirthDate=seventeen_years_ago,
            beneficiaryFraudChecks__dateCreated=year_when_user_was_fifteen,
        )

        is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_user_activated
        assert user.is_beneficiary
        assert user.deposit.type == finance_models.DepositType.GRANT_17_18
        assert user.deposit.amount == 20 + 0 + 50
        assert user.recreditAmountToShow == 70

    @time_machine.travel("2025-03-03")
    def test_pre_decree_at_17_when_registration_started_at_16(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        seventeen_years_ago = before_decree - relativedelta(years=17)
        year_when_user_was_sixteen = before_decree - relativedelta(years=1)
        user = users_factories.HonorStatementValidatedUserFactory(
            validatedBirthDate=seventeen_years_ago,
            beneficiaryFraudChecks__dateCreated=year_when_user_was_sixteen,
        )

        is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_user_activated
        assert user.is_beneficiary
        assert user.deposit.type == finance_models.DepositType.GRANT_17_18
        assert user.deposit.amount == 30 + 50
        assert user.recreditAmountToShow == 80

    @time_machine.travel("2025-03-03")
    def test_pre_decree_at_16_when_registration_started_at_15(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        sixteen_years_ago = before_decree - relativedelta(years=16)
        year_when_user_was_fifteen = before_decree - relativedelta(years=1)
        user = users_factories.HonorStatementValidatedUserFactory(
            validatedBirthDate=sixteen_years_ago,
            beneficiaryFraudChecks__dateCreated=year_when_user_was_fifteen,
        )

        is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_user_activated
        assert user.is_beneficiary
        assert user.deposit.type == finance_models.DepositType.GRANT_15_17
        assert user.deposit.amount == 20
        assert user.recreditAmountToShow == 20

    @time_machine.travel("2025-03-03")
    def test_pre_decree_18_eligibility(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        birth_date = before_decree - relativedelta(years=18)
        user = users_factories.HonorStatementValidatedUserFactory(
            validatedBirthDate=birth_date, beneficiaryFraudChecks__dateCreated=before_decree
        )

        is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_user_activated
        assert user.is_beneficiary
        assert user.deposit.type == finance_models.DepositType.GRANT_18
        assert user.recreditAmountToShow == 300

    @time_machine.travel("2025-03-03")
    def test_pre_decree_18_eligibility_at_19_year_old(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        birth_date = before_decree - relativedelta(years=18)
        user = users_factories.HonorStatementValidatedUserFactory(
            validatedBirthDate=birth_date, beneficiaryFraudChecks__dateCreated=before_decree
        )

        year_when_user_is_19 = date_utils.get_naive_utc_now() + relativedelta(years=1)
        with time_machine.travel(year_when_user_is_19):
            is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_user_activated
        assert user.is_beneficiary
        assert user.deposit.type == finance_models.DepositType.GRANT_18

    @time_machine.travel("2025-03-03")
    def test_pre_decree_underage_transition_to_18(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        eighteen_years_ago = before_decree - relativedelta(years=18)
        next_week = datetime.today() + relativedelta(weeks=1)
        user = users_factories.Transition1718Factory(
            validatedBirthDate=eighteen_years_ago,
            _phoneNumber="0123456789",
            dateCreated=before_decree,
            deposit__expirationDate=next_week,
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user, dateCreated=before_decree)
        subscription_factories.HonorStatementFraudCheckFactory(user=user, dateCreated=before_decree)

        is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_user_activated
        assert user.is_beneficiary
        assert user.deposit.type == finance_models.DepositType.GRANT_18
        assert user.recreditAmountToShow == 300

    @time_machine.travel("2025-03-03")
    def test_pre_decree_underage_transition_to_18_ignores_false_age_18_fraud_checks(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        nineteen_years_ago = before_decree - relativedelta(years=19)
        eighteen_years_ago = before_decree - relativedelta(years=18)
        next_week = datetime.today() + relativedelta(weeks=1)
        # user has ok underage fraud check
        user = users_factories.Transition1718Factory(
            dateOfBirth=nineteen_years_ago,
            validatedBirthDate=eighteen_years_ago,
            _phoneNumber="0123456789",
            dateCreated=before_decree,
            deposit__expirationDate=next_week,
        )
        # user got their dateOfBirth wrong, so the earliest created fraud check is age18
        last_year = before_decree - relativedelta(years=1)
        subscription_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.AGE18, dateCreated=last_year
        )
        # user goes through the second activation flow when they reach 18 for real
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user, dateCreated=before_decree)
        subscription_factories.HonorStatementFraudCheckFactory(user=user)

        is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_user_activated
        assert user.is_beneficiary
        assert user.deposit.type == finance_models.DepositType.GRANT_18
        assert user.recreditAmountToShow == 300

    @time_machine.travel("2025-03-03")
    def test_underage_transition_to_18_after_decree(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        user = users_factories.Transition1718Factory(_phoneNumber="0123456789", dateCreated=before_decree)
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
        subscription_factories.HonorStatementFraudCheckFactory(user=user)

        is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_user_activated
        assert user.is_beneficiary
        assert user.deposit.type == finance_models.DepositType.GRANT_17_18
        assert user.recreditAmountToShow == 150

    @pytest.mark.parametrize("age", [18, 19, 20])
    def test_post_decree_18_eligibility(self, age):
        user = users_factories.HonorStatementValidatedUserFactory(age=18)

        year_when_user_reached_age = date_utils.get_naive_utc_now() + relativedelta(years=age - 18)
        with time_machine.travel(year_when_user_reached_age):
            is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_user_activated
        assert user.is_beneficiary
        assert user.deposit.type == finance_models.DepositType.GRANT_17_18

        [recredit] = user.deposit.recredits
        assert recredit.recreditType == finance_models.RecreditType.RECREDIT_18
        assert user.recreditAmountToShow == 150

    @pytest.mark.parametrize("age", [18, 19, 20])
    def test_post_decree_when_registration_started_at_17(self, age):
        starting_age = 17
        user = users_factories.HonorStatementValidatedUserFactory(age=starting_age, _phoneNumber="0123456789")

        year_when_user_reached_age = date_utils.get_naive_utc_now() + relativedelta(years=age - starting_age)
        with time_machine.travel(year_when_user_reached_age):
            subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
            subscription_factories.HonorStatementFraudCheckFactory(user=user)

            is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_user_activated
        assert user.is_beneficiary
        assert user.deposit.type == finance_models.DepositType.GRANT_17_18

        recredit_types = [recredit.recreditType for recredit in user.deposit.recredits]
        assert set(recredit_types) == {finance_models.RecreditType.RECREDIT_17, finance_models.RecreditType.RECREDIT_18}
        assert user.recreditAmountToShow == 200

    def test_free_eligibility(self):
        user = users_factories.ProfileCompletedUserFactory(age=16)

        is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_user_activated
        assert user.has_free_beneficiary_role
        assert user.deposit.type == finance_models.DepositType.GRANT_FREE
        assert not user.deposit.recredits
        assert not mails_testing.outbox

    def test_user_with_old_fraud_checks_get_correct_deposit_and_role(self):
        """
        This test is inspired from real life data, and aims to reproduce a bug

        We generate a user that:
        - First had a failed AGE18 activation attempt (thus having some AGE18 ok fraud checks)
        - Then had a successful UNDERAGE activation attempt
        - Finally tries a GRANT_17_18 activation attempt, while being eligible.
          - They used to get an error when activating and get the wrong role (with an awful 500 error)
          - But now they get the right role (and a nice 200 response)
        """

        user = users_factories.PhoneValidatedUserFactory(
            # I immediately give the user the phone, date of birth, and roles that they will have after activation
            phoneNumber="0612345678",
            dateCreated=datetime(2022, 2, 21, 18, 12, 0),
            dateOfBirth=datetime(2007, 1, 17),
            roles=[users_models.UserRole.UNDERAGE_BENEFICIARY],
        )

        # The user first tried a AGE18 activation, but cancelled it.
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            dateCreated=datetime(2022, 6, 14, 15, 30, 00),
            status=subscription_models.FraudCheckStatus.CANCELED,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            reason="Created by script. https://passculture.atlassian.net/browse/PC-15549 ; Eligibility type changed by the identity provider",
            resultContent=None,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            dateCreated=datetime(2022, 9, 30, 16, 20, 00),
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
            reason="[Rattrapage PC-17406] création d'un fraud_check pour tous les utilisateurs dont le numéro est validé",
            resultContent=None,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            dateCreated=datetime(2022, 8, 7, 18, 49, 00),
            status=subscription_models.FraudCheckStatus.CANCELED,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.UBBLE,
            reason="Eligibility type changed by the identity provider",
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            dateCreated=datetime(2022, 8, 7, 19, 3, 00),
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.AGE18,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            reason="statement from /subscription/honor_statement endpoint",
            resultContent=None,
        )

        # Then they tru an UNDERAGE activation (because they are in fact not 18yo)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            dateCreated=datetime(2022, 8, 10, 15, 27, 00),
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            reason="Created by script. https://passculture.atlassian.net/browse/PC-15549",
            resultContent=None,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            dateCreated=datetime(2022, 8, 8, 2, 26, 00),
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.UBBLE,
            reason="",
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            dateCreated=datetime(2022, 8, 10, 15, 27, 00),
            status=subscription_models.FraudCheckStatus.OK,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            reason="statement from /subscription/honor_statement endpoint",
            resultContent=None,
        )

        # And had their deposit UNDERAGE granted
        users_factories.DepositGrantFactory(
            user=user,
            type=finance_models.DepositType.GRANT_15_17,
            dateCreated=datetime(2022, 8, 10, 17, 27),
        )

        # Now, the user tries to activate the 17-18 grant, a few years later (used to give a wrong UNDERAGE role)
        with time_machine.travel(datetime(2025, 3, 10)):
            subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
            subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert user.roles == [users_models.UserRole.BENEFICIARY]
        assert user.deposit.type == finance_models.DepositType.GRANT_17_18

    def test_user_is_not_granted_17_year_old_deposit_twice(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(weeks=1)
        with time_machine.travel(before_decree):
            user = users_factories.BeneficiaryFactory.create(
                age=17,
                phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
            )
            finance_factories.RecreditFactory(
                deposit=user.deposit, recreditType=finance_models.RecreditType.RECREDIT_17
            )

        assert user.deposit
        assert user.deposit.type == finance_models.DepositType.GRANT_15_17
        assert user.deposit.recredits

        after_decree = settings.CREDIT_V3_DECREE_DATETIME + relativedelta(weeks=1)
        with time_machine.travel(after_decree):
            # user updates his profile because he is asked to by the user profile refresh campaign
            subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

        next_year = settings.CREDIT_V3_DECREE_DATETIME + relativedelta(years=1)
        with time_machine.travel(next_year):
            subscription_factories.ProfileCompletionFraudCheckFactory(user=user)
            subscription_factories.HonorStatementFraudCheckFactory(user=user)

            is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert is_user_activated
        assert user.deposits

        assert user.deposit
        assert user.deposit.type == finance_models.DepositType.GRANT_17_18

        seventeen_years_old_recredits = []
        for deposit in user.deposits:
            for recredit in deposit.recredits:
                if recredit.recreditType == finance_models.RecreditType.RECREDIT_17:
                    seventeen_years_old_recredits.append(recredit)
        assert len(seventeen_years_old_recredits) == 1

    def test_transition_from_free_beneficiary_to_17_18(self):
        ex_free_beneficiary = users_factories.EmailValidatedUserFactory(
            roles=[users_models.UserRole.FREE_BENEFICIARY], age=17
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=ex_free_beneficiary)
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=ex_free_beneficiary, status=subscription_models.FraudCheckStatus.OK
        )
        subscription_factories.HonorStatementFraudCheckFactory(user=ex_free_beneficiary)

        is_user_activated = subscription_api.activate_beneficiary_if_no_missing_step(ex_free_beneficiary)

        assert is_user_activated
        assert ex_free_beneficiary.has_underage_beneficiary_role
        assert not ex_free_beneficiary.has_free_beneficiary_role
        assert ex_free_beneficiary.deposit.type == finance_models.DepositType.GRANT_17_18

    @patch("pcapi.core.subscription.api.activate_beneficiary_for_eligibility")
    def test_activation_retry_on_query_canceled(self, mock_activate_beneficiary):
        user = users_factories.HonorStatementValidatedUserFactory(age=18)
        # QueryCanceled often means that locking a database table timed out
        mock_activate_beneficiary.side_effect = psycopg2.errors.QueryCanceled

        with pytest.raises(psycopg2.errors.QueryCanceled):
            subscription_api.activate_beneficiary_if_no_missing_step(user)

        assert len(mock_activate_beneficiary.mock_calls) == 3


@pytest.mark.usefixtures("db_session")
class SubscriptionMessageTest:
    def test_not_eligible(self):
        user = users_factories.UserFactory(dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=20))

        assert subscription_api.get_user_subscription_state(user).subscription_message is None

    def test_already_beneficiary(self):
        user = users_factories.BeneficiaryGrant18Factory()

        assert subscription_api.get_user_subscription_state(user).subscription_message is None

    def test_other_next_step(self):
        user_needing_honor_statement = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=17)
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            user=user_needing_honor_statement,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            user=user_needing_honor_statement,
            status=subscription_models.FraudCheckStatus.PENDING,
        )

        assert subscription_api.get_user_subscription_state(user_needing_honor_statement).subscription_message is None

    @pytest.mark.features(ENABLE_UBBLE=False)
    def test_maintenance(self):
        user_needing_identity_check = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            user=user_needing_identity_check,
            status=subscription_models.FraudCheckStatus.OK,
        )

        message = subscription_api.get_user_subscription_state(user_needing_identity_check).subscription_message

        assert (
            message.user_message
            == "La vérification d'identité est momentanément indisponible. L'équipe du pass Culture met tout en oeuvre pour la rétablir au plus vite."
        )
        assert message.pop_over_icon == subscription_schemas.PopOverIcon.CLOCK

    @patch("pcapi.core.subscription.dms.api.get_dms_subscription_message")
    def test_dms_message_is_returned(self, mocked_dms_message):
        dms_returned_message = subscription_schemas.SubscriptionMessage(
            user_message="Ferme ton application. Attends 10 secondes. Ouvre la, referme. Mange un steak. Reviens. C'est bon.",
            pop_over_icon=subscription_schemas.PopOverIcon.MAGNIFYING_GLASS,
        )
        mocked_dms_message.return_value = dms_returned_message

        user_with_dms_pending = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            user=user_with_dms_pending,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            user=user_with_dms_pending,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS,
            user=user_with_dms_pending,
            status=subscription_models.FraudCheckStatus.ERROR,
        )
        last_dms_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS,
            user=user_with_dms_pending,
            status=subscription_models.FraudCheckStatus.PENDING,
        )

        message = subscription_api.get_user_subscription_state(user_with_dms_pending).subscription_message

        mocked_dms_message.assert_called_once_with(last_dms_check)
        assert message == dms_returned_message

    @patch("pcapi.core.subscription.ubble.api.get_ubble_subscription_message")
    def test_ubble_pending_message_is_returned(self, mocked_ubble_message):
        ubble_returned_message = subscription_schemas.SubscriptionMessage(
            user_message="Prends un miroir, recoiffe-toi, entraine-toi à sourire et reviens.",
            pop_over_icon=subscription_schemas.PopOverIcon.MAGNIFYING_GLASS,
        )
        mocked_ubble_message.return_value = ubble_returned_message

        user_with_ubble_pending = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            user=user_with_ubble_pending,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            user=user_with_ubble_pending,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user_with_ubble_pending,
            status=subscription_models.FraudCheckStatus.ERROR,
        )
        last_ubble_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user_with_ubble_pending,
            status=subscription_models.FraudCheckStatus.PENDING,
        )

        message = subscription_api.get_user_subscription_state(user_with_ubble_pending).subscription_message

        mocked_ubble_message.assert_called_once_with(last_ubble_check)
        assert message == ubble_returned_message

    @patch("pcapi.core.subscription.ubble.api.get_ubble_subscription_message")
    def test_ubble_retryable_message_is_returned(self, mocked_ubble_message):
        ubble_returned_message = subscription_schemas.SubscriptionMessage(
            user_message="Prends un miroir, recoiffe-toi, entraine-toi à sourire et reviens.",
            pop_over_icon=subscription_schemas.PopOverIcon.MAGNIFYING_GLASS,
        )
        mocked_ubble_message.return_value = ubble_returned_message

        user_with_ubble_pending = users_factories.UserFactory(
            dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            user=user_with_ubble_pending,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            user=user_with_ubble_pending,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user_with_ubble_pending,
            status=subscription_models.FraudCheckStatus.ERROR,
        )
        last_ubble_check = subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.UBBLE,
            user=user_with_ubble_pending,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.ID_CHECK_EXPIRED],
        )

        message = subscription_api.get_user_subscription_state(user_with_ubble_pending).subscription_message

        mocked_ubble_message.assert_called_once_with(last_ubble_check)
        assert message == ubble_returned_message

    @patch("pcapi.core.subscription.educonnect.api.get_educonnect_subscription_message")
    def test_educonnect_message_is_returned(self, mocked_educonnect_message):
        educonnect_returned_message = subscription_schemas.SubscriptionMessage(
            user_message="Pour une vie édulcorée.",
            pop_over_icon=subscription_schemas.PopOverIcon.MAGNIFYING_GLASS,
        )
        mocked_educonnect_message.return_value = educonnect_returned_message

        user_with_educonnect = users_factories.UserFactory(age=17)
        subscription_factories.BeneficiaryFraudCheckFactory(
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
            user=user_with_educonnect,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
            user=user_with_educonnect,
            status=subscription_models.FraudCheckStatus.OK,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            user=user_with_educonnect,
            status=subscription_models.FraudCheckStatus.KO,
        )
        last_educocheck = subscription_factories.BeneficiaryFraudCheckFactory(
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            type=subscription_models.FraudCheckType.EDUCONNECT,
            user=user_with_educonnect,
            status=subscription_models.FraudCheckStatus.SUSPICIOUS,
            reasonCodes=[subscription_models.FraudReasonCode.DUPLICATE_USER],
        )

        message = subscription_api.get_user_subscription_state(user_with_educonnect).subscription_message

        mocked_educonnect_message.assert_called_once_with(last_educocheck)
        assert message == educonnect_returned_message


@pytest.mark.usefixtures("db_session")
class HasCompletedProfileTest:
    def test_has_completed_underage_profile(self):
        user = users_factories.UserFactory(age=18, activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value)
        year_when_user_was_17 = date_utils.get_naive_utc_now() - relativedelta(years=1)
        subscription_factories.ProfileCompletionFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            dateCreated=year_when_user_was_17,
        )

        has_completed_underage_profile = subscription_api.has_completed_profile_for_given_eligibility(
            user, users_models.EligibilityType.UNDERAGE
        )
        has_completed_18_profile = subscription_api.has_completed_profile_for_given_eligibility(user, user.eligibility)

        assert has_completed_underage_profile
        assert not has_completed_18_profile

    def test_has_completed_with_profile_completion_ok(self):
        user = users_factories.UserFactory(dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18))
        subscription_factories.ProfileCompletionFraudCheckFactory(
            user=user, status=subscription_models.FraudCheckStatus.OK
        )
        assert subscription_api.has_completed_profile_for_given_eligibility(user, user.eligibility) is True

    def test_has_not_completed_with_profile_completion_cancelled(self):
        user = users_factories.UserFactory(dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18))
        subscription_factories.ProfileCompletionFraudCheckFactory(
            user=user, status=subscription_models.FraudCheckStatus.CANCELED
        )
        assert subscription_api.has_completed_profile_for_given_eligibility(user, user.eligibility) is False

    def test_has_completed_with_dms_form_filled(self):
        user = users_factories.UserFactory(dateOfBirth=date_utils.get_naive_utc_now() - relativedelta(years=18))
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS, user=user, status=subscription_models.FraudCheckStatus.PENDING
        )
        assert subscription_api.has_completed_profile_for_given_eligibility(user, user.eligibility) is True

    def test_has_not_completed_with_dms_form_filled_for_underage(self):
        user = users_factories.UserFactory(age=18)
        year_when_user_was_17 = date_utils.get_naive_utc_now() - relativedelta(years=1)
        subscription_factories.BeneficiaryFraudCheckFactory(
            type=subscription_models.FraudCheckType.DMS,
            user=user,
            status=subscription_models.FraudCheckStatus.PENDING,
            eligibilityType=users_models.EligibilityType.UNDERAGE,
            dateCreated=year_when_user_was_17,
        )
        assert subscription_api.has_completed_profile_for_given_eligibility(user, user.eligibility) is False
        assert subscription_api._has_completed_profile_for_previous_eligibility_only(user)

    def test_has_completed_17_profile(self):
        user = users_factories.UserFactory(age=18, activity=users_models.ActivityEnum.MIDDLE_SCHOOL_STUDENT.value)
        year_when_user_was_17 = date_utils.get_naive_utc_now() - relativedelta(years=1)
        subscription_factories.ProfileCompletionFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE17_18,
            dateCreated=year_when_user_was_17,
        )

        has_completed_18_profile = subscription_api.has_completed_profile_for_given_eligibility(user, user.eligibility)

        assert not has_completed_18_profile


@pytest.mark.usefixtures("db_session")
class GetStatusFromFraudCheckTest:
    def get_date_of_birth_to_be_eligible(self, eligibility_type):
        return date_utils.get_naive_utc_now() - relativedelta(
            years=17 if eligibility_type == users_models.EligibilityType.UNDERAGE else 18
        )

    @pytest.mark.parametrize(
        "eligibility",
        [
            users_models.EligibilityType.UNDERAGE,
            users_models.EligibilityType.AGE18,
            users_models.EligibilityType.AGE17_18,
        ],
    )
    def should_be_void_when_not_eligible(self, eligibility):
        user = users_factories.UserFactory()

        assert (
            subscription_api.get_identity_check_fraud_status(
                user, eligibility, subscription_repository.get_relevant_identity_fraud_check(user, user.eligibility)
            )
            == subscription_schemas.SubscriptionItemStatus.VOID
        )

    @time_machine.travel(settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1))
    @pytest.mark.parametrize("eligibility", [users_models.EligibilityType.UNDERAGE, users_models.EligibilityType.AGE18])
    def should_be_todo_when_eligible_before_decree(self, eligibility):
        user = users_factories.UserFactory(dateOfBirth=self.get_date_of_birth_to_be_eligible(eligibility))

        id_fraud_check_status = subscription_api.get_identity_check_fraud_status(
            user, eligibility, subscription_repository.get_relevant_identity_fraud_check(user, eligibility)
        )

        assert id_fraud_check_status == subscription_schemas.SubscriptionItemStatus.TODO

    @pytest.mark.parametrize("age", [17, 18])
    def should_be_todo_when_eligible(self, age):
        user = users_factories.UserFactory(age=age)

        id_fraud_check_status = subscription_api.get_identity_check_fraud_status(
            user, user.eligibility, subscription_repository.get_relevant_identity_fraud_check(user, user.eligibility)
        )

        assert id_fraud_check_status == subscription_schemas.SubscriptionItemStatus.TODO

    @pytest.mark.parametrize(
        "eligibility",
        [
            users_models.EligibilityType.UNDERAGE,
            users_models.EligibilityType.AGE18,
            users_models.EligibilityType.AGE17_18,
        ],
    )
    def should_be_ok_when_ok_fraud_check(self, eligibility):
        user = users_factories.UserFactory(dateOfBirth=self.get_date_of_birth_to_be_eligible(eligibility))
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, eligibilityType=eligibility, status=subscription_models.FraudCheckStatus.OK
        )

        assert (
            subscription_api.get_identity_check_fraud_status(
                user, eligibility, subscription_repository.get_relevant_identity_fraud_check(user, eligibility)
            )
            == subscription_schemas.SubscriptionItemStatus.OK
        )

    @pytest.mark.parametrize(
        "eligibility",
        [
            users_models.EligibilityType.UNDERAGE,
            users_models.EligibilityType.AGE18,
            users_models.EligibilityType.AGE17_18,
        ],
    )
    @pytest.mark.parametrize(
        "fraud_check_type",
        [
            subscription_models.FraudCheckType.EDUCONNECT,
            subscription_models.FraudCheckType.UBBLE,
        ],
    )
    @pytest.mark.parametrize(
        "fraud_check_status",
        [
            subscription_models.FraudCheckStatus.SUSPICIOUS,
            subscription_models.FraudCheckStatus.KO,
        ],
    )
    def should_be_todo_when_check_retryable(self, eligibility, fraud_check_type, fraud_check_status):
        user = users_factories.UserFactory(
            dateOfBirth=self.get_date_of_birth_to_be_eligible(eligibility),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=eligibility,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=eligibility,
            status=fraud_check_status,
            type=fraud_check_type,
            reasonCodes=[subscription_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE],
        )

        user_subscription_state = subscription_api.get_user_subscription_state(user)

        assert user_subscription_state.fraud_status == subscription_schemas.SubscriptionItemStatus.TODO

    @pytest.mark.parametrize(
        "eligibility",
        [
            users_models.EligibilityType.UNDERAGE,
            users_models.EligibilityType.AGE18,
            users_models.EligibilityType.AGE17_18,
        ],
    )
    @pytest.mark.parametrize(
        "fraud_check_status, expected_status",
        [
            (subscription_models.FraudCheckStatus.SUSPICIOUS, subscription_schemas.SubscriptionItemStatus.SUSPICIOUS),
            (subscription_models.FraudCheckStatus.KO, subscription_schemas.SubscriptionItemStatus.KO),
        ],
    )
    def should_ko_or_suspicious_when_ubble_check_not_retryable(self, eligibility, fraud_check_status, expected_status):
        user = users_factories.UserFactory(dateOfBirth=self.get_date_of_birth_to_be_eligible(eligibility))
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=eligibility,
            status=fraud_check_status,
            type=subscription_models.FraudCheckType.UBBLE,
            reasonCodes=[subscription_models.FraudReasonCode.AGE_TOO_OLD],
        )

        assert (
            subscription_api.get_identity_check_fraud_status(
                user, eligibility, subscription_repository.get_relevant_identity_fraud_check(user, eligibility)
            )
            == expected_status
        )

    @pytest.mark.parametrize(
        "eligibility",
        [
            users_models.EligibilityType.UNDERAGE,
            users_models.EligibilityType.AGE18,
            users_models.EligibilityType.AGE17_18,
        ],
    )
    def should_be_pending_if_pending_fraud_check(self, eligibility):
        user = users_factories.UserFactory(dateOfBirth=self.get_date_of_birth_to_be_eligible(eligibility))
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user, eligibilityType=eligibility, status=subscription_models.FraudCheckStatus.PENDING
        )

        assert (
            subscription_api.get_identity_check_fraud_status(
                user, eligibility, subscription_repository.get_relevant_identity_fraud_check(user, eligibility)
            )
            == subscription_schemas.SubscriptionItemStatus.PENDING
        )

    def should_be_todo_if_educonnect_for_age_18(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.get_date_of_birth_to_be_eligible(users_models.EligibilityType.AGE18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.KO,
            type=subscription_models.FraudCheckType.EDUCONNECT,
        )

        user_subscription_state = subscription_api.get_user_subscription_state(user)

        assert user_subscription_state.fraud_status == subscription_schemas.SubscriptionItemStatus.TODO

    @pytest.mark.parametrize(
        "eligibility",
        [
            users_models.EligibilityType.UNDERAGE,
            users_models.EligibilityType.AGE18,
            users_models.EligibilityType.AGE17_18,
        ],
    )
    def should_be_ko_if_third_ubble_try(self, eligibility):
        user = users_factories.UserFactory(dateOfBirth=self.get_date_of_birth_to_be_eligible(eligibility))
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=eligibility,
            status=subscription_models.FraudCheckStatus.KO,
            type=subscription_models.FraudCheckType.UBBLE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=eligibility,
            status=subscription_models.FraudCheckStatus.KO,
            type=subscription_models.FraudCheckType.UBBLE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=eligibility,
            status=subscription_models.FraudCheckStatus.KO,
            type=subscription_models.FraudCheckType.UBBLE,
        )

        assert (
            subscription_api.get_identity_check_fraud_status(
                user, eligibility, subscription_repository.get_relevant_identity_fraud_check(user, eligibility)
            )
            == subscription_schemas.SubscriptionItemStatus.KO
        )

    @pytest.mark.parametrize(
        "eligibility",
        [
            users_models.EligibilityType.UNDERAGE,
            users_models.EligibilityType.AGE18,
            users_models.EligibilityType.AGE17_18,
        ],
    )
    def should_be_pending_when_dms_started(self, eligibility):
        user = users_factories.UserFactory(dateOfBirth=self.get_date_of_birth_to_be_eligible(eligibility))
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=eligibility,
            type=subscription_models.FraudCheckType.DMS,
            status=subscription_models.FraudCheckStatus.STARTED,
        )

        assert (
            subscription_api.get_identity_check_fraud_status(
                user, eligibility, subscription_repository.get_relevant_identity_fraud_check(user, eligibility)
            )
            == subscription_schemas.SubscriptionItemStatus.PENDING
        )

    def should_not_be_eligible_when_ko_amin_review(self):
        user = users_factories.UserFactory(
            dateOfBirth=self.get_date_of_birth_to_be_eligible(users_models.EligibilityType.AGE18),
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudReviewFactory(
            user=user,
            review=subscription_models.FraudReviewStatus.KO,
        )

        user_subscription_state = subscription_api.get_user_subscription_state(user)

        assert user_subscription_state.fraud_status == subscription_schemas.SubscriptionItemStatus.KO
        assert user_subscription_state.young_status == young_status.NonEligible()


@pytest.mark.usefixtures("db_session")
class StepperTest:
    def get_step(
        self,
        step: subscription_schemas.SubscriptionStep,
        step_completion_state: subscription_schemas.SubscriptionStepCompletionState,
        subtitle: str | None = None,
    ):
        return subscription_schemas.SubscriptionStepDetails(
            name=step,
            title=subscription_schemas.SubscriptionStepTitle[step.name],
            subtitle=subtitle,
            completion_state=step_completion_state,
        )

    def test_get_stepper_title_18_yo(self):
        user = users_factories.EligibleGrant18Factory()
        assert subscription_api.get_stepper_title_and_subtitle(
            user, subscription_api.get_user_subscription_state(user)
        ) == subscription_schemas.SubscriptionStepperDetails(
            title=f"C'est très rapide{u_nbsp}!",
            subtitle=f"Pour débloquer tes 150€ tu dois suivre les étapes suivantes{u_nbsp}:",
        )

    @time_machine.travel("2025-03-03")
    def test_get_stepper_title_pre_decree_18_yo(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        birth_date = before_decree - relativedelta(years=18)
        user = users_factories.HonorStatementValidatedUserFactory(
            validatedBirthDate=birth_date, beneficiaryFraudChecks__dateCreated=before_decree
        )

        title_and_subtitle = subscription_api.get_stepper_title_and_subtitle(
            user, subscription_api.get_user_subscription_state(user)
        )

        assert title_and_subtitle == subscription_schemas.SubscriptionStepperDetails(
            title=f"C'est très rapide{u_nbsp}!",
            subtitle=f"Pour débloquer tes 300€ tu dois suivre les étapes suivantes{u_nbsp}:",
        )

    def test_get_stepper_title_underage_user(self):
        user = users_factories.EligibleUnderageFactory(age=17)
        assert subscription_api.get_stepper_title_and_subtitle(
            user, subscription_api.get_user_subscription_state(user)
        ) == subscription_schemas.SubscriptionStepperDetails(
            title=f"C'est très rapide{u_nbsp}!",
            subtitle=f"Pour débloquer tes 50€ tu dois suivre les étapes suivantes{u_nbsp}:",
        )

    @time_machine.travel("2025-03-03")
    def test_get_stepper_title_pre_decree_17_yo(self):
        before_decree = settings.CREDIT_V3_DECREE_DATETIME - relativedelta(days=1)
        birth_date = before_decree - relativedelta(years=17)
        user = users_factories.HonorStatementValidatedUserFactory(
            validatedBirthDate=birth_date, beneficiaryFraudChecks__dateCreated=before_decree
        )

        title_and_subtitle = subscription_api.get_stepper_title_and_subtitle(
            user, subscription_api.get_user_subscription_state(user)
        )

        assert title_and_subtitle == subscription_schemas.SubscriptionStepperDetails(
            title=f"C'est très rapide{u_nbsp}!",
            subtitle=f"Pour débloquer tes 30€ tu dois suivre les étapes suivantes{u_nbsp}:",
        )

    def test_get_stepper_title_18_yo_retrying_ubble(self):
        user = users_factories.EligibleGrant18Factory(
            isEmailValidated=True,
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.KO,
            type=subscription_models.FraudCheckType.UBBLE,
            reasonCodes=[subscription_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE],
        )

        assert subscription_api.get_stepper_title_and_subtitle(
            user, subscription_api.get_user_subscription_state(user)
        ) == subscription_schemas.SubscriptionStepperDetails(
            title="La vérification de ton identité a échoué",
            subtitle=None,
        )

    def test_get_subscription_steps_to_display_for_18yo_has_not_started(self):
        user = users_factories.EligibleGrant18Factory()

        steps = subscription_api.get_subscription_steps_to_display(
            user, subscription_api.get_user_subscription_state(user)
        )

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.CURRENT,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
        ]

    def test_get_subscription_steps_to_display_for_18yo_has_validated_phone(self):
        user = users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
        )

        steps = subscription_api.get_subscription_steps_to_display(
            user, subscription_api.get_user_subscription_state(user)
        )

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.CURRENT,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
        ]

    def test_get_subscription_steps_to_display_for_18yo_has_completed_profile(self):
        user = users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
        )

        steps = subscription_api.get_subscription_steps_to_display(
            user, subscription_api.get_user_subscription_state(user)
        )

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.CURRENT,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
        ]

    def test_get_subscription_steps_to_display_for_18yo_has_ubble_issue(self):
        user = users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.KO,
            type=subscription_models.FraudCheckType.UBBLE,
            reasonCodes=[subscription_models.FraudReasonCode.ID_CHECK_EXPIRED],
        )

        steps = subscription_api.get_subscription_steps_to_display(
            user, subscription_api.get_user_subscription_state(user)
        )

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.RETRY,
                subtitle="Réessaie avec un autre document d’identité valide",
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
        ]

    def test_get_subscription_steps_to_display_for_18yo_has_completed_id_check(self):
        user = users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.UBBLE,
        )

        steps = subscription_api.get_subscription_steps_to_display(
            user, subscription_api.get_user_subscription_state(user)
        )

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.CURRENT,
            ),
        ]

    def test_get_subscription_steps_to_display_for_18yo_has_completed_everything(self):
        user = users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PHONE_VALIDATION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.PROFILE_COMPLETION,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.UBBLE,
        )
        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.OK,
            type=subscription_models.FraudCheckType.HONOR_STATEMENT,
        )

        steps = subscription_api.get_subscription_steps_to_display(
            user, subscription_api.get_user_subscription_state(user)
        )

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.COMPLETED,
            ),
        ]

    def test_get_subscription_steps_to_display_for_18yo_with_15_17_profile(self):
        user = users_factories.EligibleGrant18Factory()
        year_when_user_was_17 = date_utils.get_naive_utc_now() - relativedelta(years=1)
        subscription_factories.ProfileCompletionFraudCheckFactory(
            user=user, eligibilityType=users_models.EligibilityType.UNDERAGE, dateCreated=year_when_user_was_17
        )

        steps = subscription_api.get_subscription_steps_to_display(
            user, subscription_api.get_user_subscription_state(user)
        )

        assert steps == [
            self.get_step(
                subscription_schemas.SubscriptionStep.PHONE_VALIDATION,
                subscription_schemas.SubscriptionStepCompletionState.CURRENT,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.PROFILE_COMPLETION,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
                subtitle=subscription_schemas.PROFILE_COMPLETION_STEP_EXISTING_DATA_SUBTITLE,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.IDENTITY_CHECK,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
            self.get_step(
                subscription_schemas.SubscriptionStep.HONOR_STATEMENT,
                subscription_schemas.SubscriptionStepCompletionState.DISABLED,
            ),
        ]


class TestQueriesTest:
    @pytest.mark.usefixtures("db_session")
    def test_num_queries(self):
        user = users_factories.EligibleGrant18Factory(
            phoneValidationStatus=users_models.PhoneValidationStatusType.VALIDATED
        )
        subscription_factories.ProfileCompletionFraudCheckFactory(user=user)

        subscription_factories.BeneficiaryFraudCheckFactory(
            user=user,
            eligibilityType=users_models.EligibilityType.AGE18,
            status=subscription_models.FraudCheckStatus.KO,
            type=subscription_models.FraudCheckType.UBBLE,
            reasonCodes=[subscription_models.FraudReasonCode.ID_CHECK_EXPIRED],
        )

        fetched_user = (
            db.session.query(users_models.User)
            .filter(users_models.User.id == user.id)
            .options(
                joinedload(users_models.User.beneficiaryFraudChecks),
                joinedload(users_models.User.beneficiaryFraudReviews),
                joinedload(users_models.User.action_history),
            )
            .one()
        )

        # 3 features flags checked in one query, no N+1 query when fraud checks and reviews joinedloaded
        # but the ff is already cached by BeneficiaryFraudCheckFactory.eligibilityType
        with assert_num_queries(0):
            subscription_api.get_user_subscription_state(fetched_user)
