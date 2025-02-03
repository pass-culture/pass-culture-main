import pytest

import pcapi.core.finance.models as finance_models
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.sandboxes.scripts.creators.industrial.create_industrial_app_users import create_industrial_app_users


@pytest.mark.usefixtures("db_session")
@pytest.mark.features(WIP_ENABLE_CREDIT_V3=0)
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
        assert not ex_underage.has_active_deposit

        assert ex_beneficiary.age == 20
        assert ex_beneficiary.roles == [UserRole.BENEFICIARY]
        assert ex_beneficiary.deposit
        assert not ex_beneficiary.has_active_deposit

        assert beneficiary_and_exunderage.has_active_deposit
        assert beneficiary_and_exunderage.deposit.amount == 300
