import pytest

from pcapi.core.users.factories import FavoriteFactory
from pcapi.core.users.factories import UserFactory
from pcapi.models import Deposit
from pcapi.models import User
from pcapi.repository import repository
from pcapi.scripts.beneficiary.delete_or_suspend_account_from_csv import _delete_or_suspend_account_from_csv


@pytest.mark.usefixtures("db_session")
def test_delete_user():
    UserFactory(email="romain.chaffal@beta.gouv.fr", isAdmin=True)
    user_without_deposit = UserFactory()
    FavoriteFactory(user=user_without_deposit)
    deposit = Deposit.query.all()
    repository.delete(*deposit)

    _delete_or_suspend_account_from_csv(user_without_deposit.email)
    User.query.one()


@pytest.mark.usefixtures("db_session")
def test_suspend_user():
    UserFactory(email="romain.chaffal@beta.gouv.fr", isAdmin=True)
    user_with_deposit = UserFactory()

    _delete_or_suspend_account_from_csv(user_with_deposit.email)

    user = User.query.filter(User.email == user_with_deposit.email).one()
    assert user.isActive == False
