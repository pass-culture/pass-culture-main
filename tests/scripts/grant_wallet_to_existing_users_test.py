from unittest.mock import patch, MagicMock

from models import UserSQLEntity, Deposit
from repository import repository
from scripts.grant_wallet_to_existing_users import grant_wallet_to_existing_users
import pytest
from model_creators.generic_creators import create_user, create_deposit


@pytest.mark.usefixtures("db_session")
def test_should_grant_wallet_to_existing_users(app):
    # given
    beneficiary = create_user(email='email@example.com')
    beneficiary_2 = create_user(email='email2@example.com')

    repository.save(beneficiary, beneficiary_2)

    # when
    grant_wallet_to_existing_users([beneficiary.id, beneficiary_2.id])

    # then
    users = UserSQLEntity.query.join(Deposit).with_entities(Deposit.amount, UserSQLEntity.canBookFreeOffers).all()
    user_1 = users[0]
    user_2 = users[1]

    assert user_1.amount == 500
    assert user_1.canBookFreeOffers
    assert user_2.amount == 500
    assert user_2.canBookFreeOffers
