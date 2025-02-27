import pytest

from pcapi.core.finance.api import recredit_users
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
            if user.email == "user18avantdecret@test.com":
                assert user.age == 18
                assert user.is_beneficiary
                assert user.deposit.type == finance_models.DepositType.GRANT_18
                assert user.deposit.amount == 300

            if user.email == "user18apresdecret@test.com":
                assert user.age == 18
                assert user.is_beneficiary
                assert user.deposit.type == finance_models.DepositType.GRANT_17_18
                assert user.deposit.amount == 150

            if user.email == "user17avantdecret@test.com":
                assert user.age == 17
                assert user.is_beneficiary
                assert user.deposit.type == finance_models.DepositType.GRANT_15_17
                assert user.deposit.amount == 30

            if user.email == "user17apresdecret@test.com":
                assert user.age == 17
                assert user.is_beneficiary
                assert user.deposit.type == finance_models.DepositType.GRANT_17_18
                assert user.deposit.amount == 50

            if user.email == "user16avantdecret@test.com":
                assert user.age == 16
                assert user.is_beneficiary
                assert user.deposit.type == finance_models.DepositType.GRANT_15_17
                assert user.deposit.amount == 30

            if user.email == "user16apresdecret@test.com":
                assert user.age == 16
                assert not user.is_beneficiary
                assert not user.deposit

            if user.email == "user15avantdecret@test.com":
                assert user.age == 15
                assert user.is_beneficiary
                assert user.deposit.type == finance_models.DepositType.GRANT_15_17
                assert user.deposit.amount == 20

            if user.email == "user15apresdecret@test.com":
                assert user.age == 15
                assert not user.is_beneficiary
                assert not user.deposit

    def test_create_users_for_credit_v3_tests_with_underage_deposits(self):
        create_users_for_credit_v3_tests()

        credit_v3_tests_users = User.query.filter(
            User.email.in_(
                [
                    "user18redepotavantdecret@test.com",
                    "user18redepotapresdecret@test.com",
                    "user17anniversaireavantdecret@test.com",
                    "user17anniversaireapresdecret@test.com",
                    "user16anniversaireavantdecret@test.com",
                    "user16anniversaireapresdecret@test.com",
                ]
            )
        ).all()

        assert len(credit_v3_tests_users) == 6

        for user in credit_v3_tests_users:
            assert user.is_beneficiary
            if user.email == "user18redepotavantdecret@test.com":
                assert user.age == 18
                assert user.deposit.type == finance_models.DepositType.GRANT_18

                underage_deposit = next(
                    deposit for deposit in user.deposits if deposit.type == finance_models.DepositType.GRANT_15_17
                )
                assert underage_deposit
                assert underage_deposit.amount == 80
                assert len(underage_deposit.recredits) == 2

                recredit_types_and_amounts = [
                    (recredit.recreditType, recredit.amount) for recredit in underage_deposit.recredits
                ]
                assert (finance_models.RecreditType.RECREDIT_16, 30) in recredit_types_and_amounts
                assert (finance_models.RecreditType.RECREDIT_17, 30) in recredit_types_and_amounts

            if user.email == "user18redepotapresdecret@test.com":
                assert user.age == 18
                assert user.deposit.type == finance_models.DepositType.GRANT_17_18

                underage_deposit = next(
                    deposit for deposit in user.deposits if deposit.type == finance_models.DepositType.GRANT_15_17
                )
                assert underage_deposit
                assert underage_deposit.amount == 80
                assert len(underage_deposit.recredits) == 2

                recredit_types_and_amounts = [
                    (recredit.recreditType, recredit.amount) for recredit in underage_deposit.recredits
                ]
                assert (finance_models.RecreditType.RECREDIT_16, 30) in recredit_types_and_amounts
                assert (finance_models.RecreditType.RECREDIT_17, 30) in recredit_types_and_amounts

            if user.email == "user17anniversaireavantdecret@test.com":
                assert user.age == 17
                assert user.deposit.type == finance_models.DepositType.GRANT_15_17
                assert user.deposit.amount == 20 + 30 + 30

                recredit_types_and_amounts = [
                    (recredit.recreditType, recredit.amount) for recredit in user.deposit.recredits
                ]
                assert (finance_models.RecreditType.RECREDIT_16, 30) in recredit_types_and_amounts
                assert (finance_models.RecreditType.RECREDIT_17, 30) in recredit_types_and_amounts

            if user.email == "user17anniversaireapresdecret@test.com":
                assert user.age == 17
                # At this point, the RECREDIT_17 is not yet applied.
                assert user.deposit.type == finance_models.DepositType.GRANT_15_17
                assert user.deposit.amount == 20 + 30
                # assert user.deposit.type == finance_models.DepositType.GRANT_17_18
                # assert user.deposit.amount == 20 + 30 + 50

            if user.email == "user16anniversaireavantdecret@test.com":
                assert user.age == 16
                assert user.deposit.type == finance_models.DepositType.GRANT_15_17
                assert user.deposit.amount == 20
                assert not user.deposit.recredits

            if user.email == "user16anniversaireapresdecret@test.com":
                assert user.age == 16
                assert user.deposit.type == finance_models.DepositType.GRANT_15_17
                assert user.deposit.amount == 20
                assert not user.deposit.recredits

        recredit_users()

        # check 16 yo users are not recredited
        user_16_before_decree = User.query.filter_by(email="user16anniversaireavantdecret@test.com").one()
        assert user_16_before_decree.deposit.type == finance_models.DepositType.GRANT_15_17
        assert user_16_before_decree.deposit.amount == 20
        assert not user_16_before_decree.deposit.recredits

        user_16_after_decree = User.query.filter_by(email="user16anniversaireapresdecret@test.com").one()
        assert user_16_after_decree.deposit.type == finance_models.DepositType.GRANT_15_17
        assert user_16_after_decree.deposit.amount == 20
        assert not user_16_after_decree.deposit.recredits

        # Check user 17 yo is recredited
        user_17_after_decree = User.query.filter_by(email="user17anniversaireapresdecret@test.com").one()
        # At this point, the RECREDIT_17 is applied.
        assert user_17_after_decree.deposit.type == finance_models.DepositType.GRANT_17_18
        assert user_17_after_decree.deposit.amount == 20 + 30 + 50

        recredit_types_and_amounts = [
            (recredit.recreditType, recredit.amount) for recredit in user_17_after_decree.deposit.recredits
        ]
        assert (finance_models.RecreditType.RECREDIT_17, 50) in recredit_types_and_amounts
        assert (finance_models.RecreditType.PREVIOUS_DEPOSIT, 20 + 30) in recredit_types_and_amounts
