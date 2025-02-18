import pytest

import pcapi.core.finance.models as finance_models
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_app_users import create_industrial_app_users
from pcapi.sandboxes.scripts.creators.test_cases import create_users_for_credit_v3_tests


@pytest.mark.usefixtures("db_session")
class CreateIndustrialWebappUsersTest:
    def test_create_industrial_app_users(self):
        create_industrial_app_users()
        assert User.query.count() == 46
        assert finance_models.Deposit.query.count() == 54

        ex_underage = User.query.filter_by(email="exunderage_18@example.com").first()
        ex_beneficiary = User.query.filter_by(email="exbene_20@example.com").first()
        beneficiary_and_exunderage = User.query.filter_by(email="bene_18_exunderage@example.com").first()

        assert ex_underage.age == 18
        assert ex_underage.roles == [UserRole.UNDERAGE_BENEFICIARY]
        assert ex_underage.deposit
        assert ex_underage.has_active_deposit

        assert ex_beneficiary.age == 20
        assert ex_beneficiary.roles == [UserRole.BENEFICIARY]
        assert ex_beneficiary.deposit
        assert ex_beneficiary.has_active_deposit

        assert beneficiary_and_exunderage.has_active_deposit
        assert beneficiary_and_exunderage.deposit.amount == 150


@pytest.mark.usefixtures("db_session")
class CreateTestCasesTest:
    def test_create_users_for_credit_v3_tests(self):
        create_users_for_credit_v3_tests()

        credit_v3_tests_users = User.query.filter(
            User.email.in_(
                [
                    "user18avantdecret@test.com",
                    "user18apresdecret@test.com",
                    "user17avantdecret@test.com",
                    "user17apresdecret@test.com",
                    "user16avantdecret@test.com",
                    "user16apresdecret@test.com",
                    "user15avantdecret@test.com",
                    "user15apresdecret@test.com",
                ]
            )
        ).all()

        assert len(credit_v3_tests_users) == 8

        for user in credit_v3_tests_users:
            assert user.is_beneficiary
            if user.email == "user18avantdecret@test.com":
                assert user.age == 18
                assert user.deposit.type == finance_models.DepositType.GRANT_18

            if user.email == "user18apresdecret@test.com":
                assert user.age == 18
                assert user.deposit.type == finance_models.DepositType.GRANT_17_18

            if user.email == "user17avantdecret@test.com":
                assert user.age == 17
                assert user.deposit.type == finance_models.DepositType.GRANT_15_17

            if user.email == "user17apresdecret@test.com":
                assert user.age == 17
                assert user.deposit.type == finance_models.DepositType.GRANT_17_18

            if user.email == "user16avantdecret@test.com":
                assert user.age == 16
                assert user.deposit.type == finance_models.DepositType.GRANT_15_17

            if user.email == "user16apresdecret@test.com":
                assert user.age == 16
                assert user.deposit.type == finance_models.DepositType.GRANT_17_18

            if user.email == "user15avantdecret@test.com":
                assert user.age == 15
                assert user.deposit.type == finance_models.DepositType.GRANT_15_17

            if user.email == "user15apresdecret@test.com":
                assert user.age == 15
                assert user.deposit.type == finance_models.DepositType.GRANT_17_18
