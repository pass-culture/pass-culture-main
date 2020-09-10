from typing import List

from models import UserSQLEntity
from repository import repository
from tests.model_creators.generic_creators import create_deposit


def grant_wallet_to_existing_users(user_ids: List[int]):
    users = UserSQLEntity.query.filter(UserSQLEntity.id.in_(user_ids)).all()
    maximum_wallet_balance = 500
    for user in users:
        user.canBookFreeOffers = True
        if not user.wallet_balance:
            deposit = create_deposit(user, amount=maximum_wallet_balance)
            repository.save(user, deposit)
