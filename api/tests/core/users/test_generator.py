import pytest

from pcapi.core.users import constants as users_constants
import pcapi.core.users.generator as users_generator
import pcapi.core.users.models as users_models


pytestmark = pytest.mark.usefixtures("db_session")


class UserGeneratorTest:
    def test_generate_default_user(self):
        user_data = users_generator.GenerateUserData(
            age=users_constants.ELIGIBILITY_AGE_18, is_email_validated=True, is_beneficiary=False
        )
        user = users_generator.generate_user(user_data)

        assert user.isEmailValidated is True
        assert user.age == users_constants.ELIGIBILITY_AGE_18
        assert user.is_beneficiary is False

    def test_generate_beneficiary_user(self):
        user_data = users_generator.GenerateUserData(
            age=users_constants.ELIGIBILITY_AGE_18, is_email_validated=True, is_beneficiary=True
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
        ],
    )
    def test_generate_underage_beneficiary_user(self, age):
        user_data = users_generator.GenerateUserData(age=age, is_email_validated=True, is_beneficiary=True)
        user = users_generator.generate_user(user_data)

        assert user.isEmailValidated is True
        assert user.age == age
        assert user.is_beneficiary is True
        assert users_models.UserRole.UNDERAGE_BENEFICIARY in user.roles
        assert user.deposit.type == users_models.DepositType.GRANT_15_17
