from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.model_creators.generic_creators import create_deposit
from pcapi.model_creators.generic_creators import create_user
from pcapi.models import Deposit
from pcapi.models import UserSQLEntity
from pcapi.repository import repository
from pcapi.scripts.grant_wallet_to_existing_users import grant_wallet_to_existing_users


@pytest.mark.usefixtures("db_session")
def test_should_grant_wallet_to_existing_users(app):
    # given
    beneficiary = create_user(email="email@example.com")
    beneficiary_2 = create_user(email="email2@example.com")

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
