from unittest.mock import patch, MagicMock

from models import UserSQLEntity, Deposit
from repository import repository
from scripts.grant_wallet_to_existing_users import grant_wallet_to_existing_users
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_deposit


@clean_database
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


@clean_database
@patch('scripts.grant_wallet_to_existing_users.repository')
def test_should_not_grant_wallet_to_users_with_non_empty_wallet(mocked_repository, app):
    # given
    mocked_repository.save = MagicMock()
    beneficiary = create_user(email='email@example.com')
    beneficiary_2 = create_user(email='email2@example.com')

    deposit = create_deposit(beneficiary, amount=300)
    repository.save(beneficiary, beneficiary_2, deposit)

    # when
    grant_wallet_to_existing_users([beneficiary.id, beneficiary_2.id])

    # then
    deposit = Deposit.query.filter_by(userId=beneficiary_2.id).all()
    deposit_for_beneficiary_2 = deposit[0]

    mocked_repository.save.assert_called_once_with(beneficiary_2, deposit_for_beneficiary_2)
