import pytest

import pcapi.core.fraud.factories as fraud_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import Deposit
from pcapi.models import User
from pcapi.repository import repository
from pcapi.scripts.beneficiary.delete_or_suspend_account_from_file import suspend_or_delete_from_file


@pytest.mark.usefixtures("db_session")
def test_delete_user_when_she_has_no_deposit():
    admin = users_factories.AdminFactory()
    user_without_deposit = users_factories.UserFactory(email="user_to_delete@example.com")
    users_factories.FavoriteFactory(user=user_without_deposit)
    fraud_factories.BeneficiaryFraudCheckFactory(user=user_without_deposit)
    fraud_factories.BeneficiaryFraudResultFactory(user=user_without_deposit)
    fraud_factories.BeneficiaryFraudReviewFactory(user=user_without_deposit, author=admin)

    deposit = Deposit.query.all()
    repository.delete(*deposit)
    suspend_or_delete_from_file(
        "tests/scripts/beneficiary/users_to_delete_fixture.txt",
        admin.email,
    )
    assert User.query.all() == [admin]


@pytest.mark.usefixtures("db_session")
def test_suspend_user_when_he_has_deposit():
    admin = users_factories.AdminFactory()
    user_with_deposit = users_factories.BeneficiaryGrant18Factory(email="user_to_suspend@example.com")

    suspend_or_delete_from_file(
        "tests/scripts/beneficiary/users_to_delete_fixture.txt",
        admin.email,
    )

    user = User.query.filter(User.email == user_with_deposit.email).one()
    assert user.isActive == False
