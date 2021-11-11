import pytest

from pcapi.core.payments.models import Deposit
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_app_users import create_industrial_app_users


@pytest.mark.usefixtures("db_session")
class CreateIndustrialWebappUsersTest:
    def test_create_industrial_app_users(self):
        create_industrial_app_users()
        assert User.query.count() == 5 * 2 * 2 + 3 * 2 + 2 * 2 + 3 + 11
        assert Deposit.query.count() == 5 * 2 * 2 * 2 + 3 * 2 + 8

        ex_underage = User.query.filter_by(email="exunderage_18@example.com").first()
        ex_beneficiary = User.query.filter_by(email="exbene_20@example.com").first()
        beneficiary_and_exunderage = User.query.filter_by(email="bene_18_exunderage@example.com").first()

        assert ex_underage.age == 18
        assert ex_underage.roles == [UserRole.UNDERAGE_BENEFICIARY]
        assert ex_underage.deposit
        assert not ex_underage.has_active_deposit

        assert ex_beneficiary.age == 20
        assert ex_beneficiary.roles == [UserRole.BENEFICIARY]
        assert ex_beneficiary.deposit
        assert not ex_beneficiary.has_active_deposit

        assert beneficiary_and_exunderage.has_active_deposit
        assert beneficiary_and_exunderage.deposit.amount == 300
