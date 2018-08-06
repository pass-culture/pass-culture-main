import pytest

from models import Deposit, User
from tests.conftest import clean_database


@pytest.mark.standalone
@clean_database
def test_deposit_creation_1(app):
    # given
    user = User()
    user.email = 'test@example.com'
    user.setPassword('abcd1234../')
    user.publicName = 'John Bob'
    user.departementCode = '93'

    deposit = Deposit()
    deposit.user = user
    deposit.amount = 200
    deposit.source = "test money"

    # when
    deposit.save()

    # then
    assert Deposit.query.count() == 1


@pytest.mark.standalone
@clean_database
def test_deposit_creation_2(app):
    # given
    user = User()
    user.email = 'test@example.com'
    user.setPassword('abcd1234../')
    user.publicName = 'John Bob'
    user.departementCode = '93'

    deposit = Deposit()
    deposit.user = user
    deposit.amount = 200
    deposit.source = "test money"

    # when
    deposit.save()

    # then
    assert Deposit.query.count() == 1
