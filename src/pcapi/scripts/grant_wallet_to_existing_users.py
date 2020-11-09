from typing import List

from pcapi.model_creators.generic_creators import create_deposit
from pcapi.models import UserSQLEntity
from pcapi.repository import repository
from pcapi.utils import config


def grant_wallet_to_existing_users(user_ids: List[int]):
    if config.IS_PROD:
        raise ValueError("This action is not available on production")
    users = UserSQLEntity.query.filter(UserSQLEntity.id.in_(user_ids)).all()
    maximum_wallet_balance = 500
    for user in users:
        user.canBookFreeOffers = True
        deposit = create_deposit(user, amount=maximum_wallet_balance)
        repository.save(user, deposit)
