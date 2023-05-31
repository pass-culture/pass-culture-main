import pytest

import pcapi.core.fraud.models as fraud_models
import pcapi.core.subscription.models as subscription_models
from pcapi.core.users import constants as users_constants
import pcapi.core.users.generator as users_generator
import pcapi.core.users.models as users_models


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
        assert user.is_beneficiary is False

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

    def test_generate_default_user(self):
        user_data = users_generator.GenerateUserData(
            age=users_constants.ELIGIBILITY_AGE_18,
            step=subscription_models.SubscriptionStep.EMAIL_VALIDATION,
            is_beneficiary=False,
        )
        user = users_generator.generate_user(user_data)

        assert user.isEmailValidated is True
        assert user.age == users_constants.ELIGIBILITY_AGE_18
        assert user.is_beneficiary is False

    def test_generate_beneficiary_user(self):
        user_data = users_generator.GenerateUserData(
            age=users_constants.ELIGIBILITY_AGE_18,
            is_beneficiary=True,
        )
        user = users_generator.generate_user(user_data)

        assert user.isEmailValidated is True
        assert user.age == users_constants.ELIGIBILITY_AGE_18
        assert user.is_beneficiary is True
        assert users_models.UserRole.BENEFICIARY in user.roles
        assert user.deposit.type == users_models.DepositType.GRANT_18

    @pytest.mark.parametrize(
        "age",
        [
            users_constants.ELIGIBILITY_UNDERAGE_RANGE[0],
            users_constants.ELIGIBILITY_UNDERAGE_RANGE[1],
            users_constants.ELIGIBILITY_UNDERAGE_RANGE[2],
            users_constants.ELIGIBILITY_AGE_18,
        ],
    )
    @pytest.mark.parametrize(
        "step, tests",
        [
            (subscription_models.SubscriptionStep.EMAIL_VALIDATION, assert_user_passed_email_validation),
            (subscription_models.SubscriptionStep.PHONE_VALIDATION, assert_user_passed_phone_validation),
            (subscription_models.SubscriptionStep.PROFILE_COMPLETION, assert_user_passed_profile_completion),
            (subscription_models.SubscriptionStep.IDENTITY_CHECK, assert_user_passed_identity_check),
            (subscription_models.SubscriptionStep.HONOR_STATEMENT, assert_user_passed_honor_statement),
        ],
    )
    def test_generate_user_at_step(self, age, step, tests):
        user_data = users_generator.GenerateUserData(
            age=age,
            step=step,
            is_beneficiary=False,
        )
        user = users_generator.generate_user(user_data)
        tests(self, user)

    @pytest.mark.parametrize(
        "age",
        [
            users_constants.ELIGIBILITY_UNDERAGE_RANGE[0],
            users_constants.ELIGIBILITY_UNDERAGE_RANGE[1],
            users_constants.ELIGIBILITY_UNDERAGE_RANGE[2],
        ],
    )
    def test_generate_underage_beneficiary_user(self, age):
        user_data = users_generator.GenerateUserData(
            age=age,
            is_beneficiary=True,
        )
        user = users_generator.generate_user(user_data)

        assert user.isEmailValidated is True
        assert user.age == age
        assert user.is_beneficiary is True
        assert users_models.UserRole.UNDERAGE_BENEFICIARY in user.roles
        assert user.deposit.type == users_models.DepositType.GRANT_15_17
