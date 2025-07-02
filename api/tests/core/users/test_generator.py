import datetime

import pytest
from dateutil.relativedelta import relativedelta

import pcapi.core.finance.models as finance_models
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.models as fraud_models
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.generator as users_generator
import pcapi.core.users.models as users_models
from pcapi.core.fraud import repository as fraud_repository
from pcapi.core.users import constants as users_constants


pytestmark = pytest.mark.usefixtures("db_session")


class UserGeneratorTest:
    def has_fraud_check_validated(self, user, fraud_check_type) -> bool:
        return any(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_check_type and fraud_check.status == fraud_models.FraudCheckStatus.OK
        )

    def assert_user_passed_email_validation(self, user: users_models.User):
        assert user.isEmailValidated is True

    def assert_user_passed_phone_validation(self, user: users_models.User):
        self.assert_user_passed_email_validation(user)
        if user.age >= users_constants.ELIGIBILITY_AGE_18:
            assert user.phoneValidationStatus == users_models.PhoneValidationStatusType.VALIDATED
            assert user.phoneNumber
            assert self.has_fraud_check_validated(user, fraud_models.FraudCheckType.PHONE_VALIDATION)
        elif user.age in users_constants.ELIGIBILITY_UNDERAGE_RANGE:
            assert user.phoneNumber is None
            assert user.phoneValidationStatus is None

    def assert_user_passed_profile_completion(self, user: users_models.User):
        self.assert_user_passed_phone_validation(user)
        assert user.address
        assert user.city
        assert user.firstName
        assert user.lastName
        assert user.postalCode
        assert self.has_fraud_check_validated(user, fraud_models.FraudCheckType.PROFILE_COMPLETION)

    def assert_user_passed_identity_check(self, user: users_models.User):
        self.assert_user_passed_profile_completion(user)
        assert user.validatedBirthDate
        assert user.idPieceNumber
        assert self.has_fraud_check_validated(
            user, fraud_models.FraudCheckType.UBBLE
        ) or self.has_fraud_check_validated(user, fraud_models.FraudCheckType.EDUCONNECT)

    def assert_user_passed_honor_statement(self, user: users_models.User):
        self.assert_user_passed_identity_check(user)
        assert self.has_fraud_check_validated(user, fraud_models.FraudCheckType.HONOR_STATEMENT)

    def assert_user_is_beneficiary(
        self,
        user: users_models.User,
        expected_deposit_type: users_models.DepositType = users_models.DepositType.GRANT_17_18,
    ):
        self.assert_user_passed_honor_statement(user)
        expected_role = (
            users_models.UserRole.BENEFICIARY
            if user.age == users_constants.ELIGIBILITY_AGE_18
            else users_models.UserRole.UNDERAGE_BENEFICIARY
        )
        assert user.is_beneficiary is True
        assert expected_role in user.roles
        assert user.deposit.type == expected_deposit_type

    def test_generate_default_user(self):
        user_data = users_generator.GenerateUserData()
        user = users_generator.generate_user(user_data)

        assert user.isEmailValidated is True
        assert user.age == users_constants.ELIGIBILITY_AGE_18
        assert user.is_beneficiary is False

    def test_generate_beneficiary_user(self):
        user_data = users_generator.GenerateUserData(step=users_generator.GeneratedSubscriptionStep.BENEFICIARY)
        user = users_generator.generate_user(user_data)

        self.assert_user_is_beneficiary(user)

    @pytest.mark.parametrize(
        "age",
        [
            users_constants.ELIGIBILITY_UNDERAGE_RANGE[2],
            users_constants.ELIGIBILITY_AGE_18,
        ],
    )
    @pytest.mark.parametrize(
        "step, tests",
        [
            (users_generator.GeneratedSubscriptionStep.EMAIL_VALIDATION, assert_user_passed_email_validation),
            (users_generator.GeneratedSubscriptionStep.PHONE_VALIDATION, assert_user_passed_phone_validation),
            (users_generator.GeneratedSubscriptionStep.PROFILE_COMPLETION, assert_user_passed_profile_completion),
            (users_generator.GeneratedSubscriptionStep.IDENTITY_CHECK, assert_user_passed_identity_check),
            (users_generator.GeneratedSubscriptionStep.HONOR_STATEMENT, assert_user_passed_honor_statement),
            (users_generator.GeneratedSubscriptionStep.BENEFICIARY, assert_user_is_beneficiary),
        ],
    )
    def test_generate_user_at_step(self, age, step, tests):
        user_data = users_generator.GenerateUserData(
            age=age,
            id_provider=users_generator.GeneratedIdProvider.UBBLE,
            step=step,
        )
        user = users_generator.generate_user(user_data)
        tests(self, user)

    @pytest.mark.parametrize(
        "id_provider",
        [
            users_generator.GeneratedIdProvider.DMS,
            users_generator.GeneratedIdProvider.EDUCONNECT,
            users_generator.GeneratedIdProvider.UBBLE,
        ],
    )
    def test_user_generated_with_id_provider(self, id_provider: users_generator.GeneratedIdProvider):
        user_data = users_generator.GenerateUserData(
            age=users_constants.ELIGIBILITY_AGE_18,
            id_provider=id_provider,
            step=users_generator.GeneratedSubscriptionStep.IDENTITY_CHECK,
        )
        user = users_generator.generate_user(user_data)
        self.has_fraud_check_validated(user, id_provider.value)

    def test_generate_underage_beneficiary_user(self):
        user_data = users_generator.GenerateUserData(
            age=17,
            step=users_generator.GeneratedSubscriptionStep.BENEFICIARY,
        )
        user = users_generator.generate_user(user_data)

        assert user.age == 17
        self.assert_user_is_beneficiary(user, expected_deposit_type=users_models.DepositType.GRANT_17_18)

    def test_email_is_consistent_with_user_data_when_no_names(self):
        user_data = users_generator.GenerateUserData(
            age=users_constants.ELIGIBILITY_AGE_18,
            step=users_generator.GeneratedSubscriptionStep.EMAIL_VALIDATION,
        )
        user = users_generator.generate_user(user_data)
        assert user.email == f"user.{user.id}@passculture.gen"

    def test_email_is_consistent_with_user_data_when_names(self):
        user_data = users_generator.GenerateUserData(
            age=users_constants.ELIGIBILITY_AGE_18,
            step=users_generator.GeneratedSubscriptionStep.PROFILE_COMPLETION,
        )
        user = users_generator.generate_user(user_data)
        assert user.email == f"{user.firstName}.{user.lastName}.{user.id}@passculture.gen".lower()

    def test_id_piece_number_is_valid(self):
        user_data = users_generator.GenerateUserData(
            age=users_constants.ELIGIBILITY_AGE_18,
            step=users_generator.GeneratedSubscriptionStep.IDENTITY_CHECK,
        )
        user = users_generator.generate_user(user_data)
        fraud_item = fraud_api.validate_id_piece_number_format_fraud_item(user.idPieceNumber)
        assert fraud_item.status == fraud_models.FraudStatus.OK

    def test_profile_completion_is_consistent_with_user_data(self):
        user_data = users_generator.GenerateUserData(
            age=users_constants.ELIGIBILITY_AGE_18,
            step=users_generator.GeneratedSubscriptionStep.PROFILE_COMPLETION,
        )
        user = users_generator.generate_user(user_data)
        profile_completion = fraud_repository.get_completed_profile_check(user, user.eligibility)
        assert profile_completion.resultContent["address"] == user.address
        assert profile_completion.resultContent["city"] == user.city
        assert profile_completion.resultContent["firstName"] == user.firstName
        assert profile_completion.resultContent["lastName"] == user.lastName
        assert profile_completion.resultContent["postalCode"] == user.postalCode

    def test_identity_check_is_consistent_with_user_data(self):
        user_data = users_generator.GenerateUserData(
            age=users_constants.ELIGIBILITY_AGE_18,
            step=users_generator.GeneratedSubscriptionStep.IDENTITY_CHECK,
        )
        user = users_generator.generate_user(user_data)
        identity_check = fraud_repository.get_relevant_identity_fraud_check(user, user.eligibility)
        assert identity_check.resultContent["first_name"] == user.firstName
        assert identity_check.resultContent["last_name"] == user.lastName
        assert identity_check.resultContent["birth_date"] == str(user.birth_date)

    def test_user_in_transition_17_18(self):
        user_data = users_generator.GenerateUserData(transition_17_18=True)
        user = users_generator.generate_user(user_data)
        assert user.age == users_constants.ELIGIBILITY_AGE_18
        assert user.has_underage_beneficiary_role
        assert user.deposit.type == finance_models.DepositType.GRANT_17_18
        assert user.deposit.expirationDate < datetime.datetime.utcnow()
        user_subscription_state = subscription_api.get_user_subscription_state(user)
        assert user_subscription_state.next_step == subscription_models.SubscriptionStep.PHONE_VALIDATION

    @pytest.mark.parametrize(
        "id_provider",
        [
            users_generator.GeneratedIdProvider.DMS,
            users_generator.GeneratedIdProvider.EDUCONNECT,
            users_generator.GeneratedIdProvider.UBBLE,
        ],
    )
    def test_id_provider_in_transition_17_18(self, id_provider):
        user_data = users_generator.GenerateUserData(transition_17_18=True, id_provider=id_provider)
        user = users_generator.generate_user(user_data)
        assert self.has_fraud_check_validated(user, id_provider.value)

    def test_user_generated_with_date_created(self):
        date_in_the_past = datetime.datetime.utcnow() - relativedelta(months=5)
        user_data = users_generator.GenerateUserData(
            step=users_generator.GeneratedSubscriptionStep.BENEFICIARY, date_created=date_in_the_past
        )

        user = users_generator.generate_user(user_data)

        profile_completion_check = next(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.PROFILE_COMPLETION
        )
        assert profile_completion_check.dateCreated == date_in_the_past

        identity_fraud_check = next(
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.UBBLE
        )
        assert identity_fraud_check.dateCreated == date_in_the_past
        assert identity_fraud_check.source_data().get_registration_datetime().date() == date_in_the_past.date()

    @pytest.mark.parametrize("age", [15, 16])
    def test_free_beneficiary_generation(self, age):
        user_data = users_generator.GenerateUserData(
            age=age, step=users_generator.GeneratedSubscriptionStep.BENEFICIARY
        )

        user = users_generator.generate_user(user_data)

        assert user.has_free_beneficiary_role
        assert user.deposit.type == finance_models.DepositType.GRANT_FREE
        assert user.deposit.amount == 0
