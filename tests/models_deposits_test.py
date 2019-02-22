import pytest

from models import Deposit, PcObject
from tests.conftest import clean_database
from tests.test_utils import create_user


@pytest.mark.standalone
@clean_database
def test_deposit_creation_1(app):
    # given
    user = create_user()

    deposit = Deposit()
    deposit.user = user
    deposit.amount = 200
    deposit.source = "test money"

    # when
    PcObject.check_and_save(deposit)

    # then
    assert Deposit.query.count() == 1


@pytest.mark.standalone
@clean_database
def test_deposit_creation_2(app):
    # given
    user = create_user()

    deposit = Deposit()
    deposit.user = user
    deposit.amount = 200
    deposit.source = "test money"

    # when
    PcObject.check_and_save(deposit)

    # then
    assert Deposit.query.count() == 1
