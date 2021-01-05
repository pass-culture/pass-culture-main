from typing import List

from pcapi import settings
from pcapi.core.users.models import UserSQLEntity
from pcapi.model_creators.generic_creators import create_deposit
from pcapi.repository import repository


def grant_wallet_to_existing_users(user_ids: List[int]):
    if settings.IS_PROD:
        raise ValueError("This action is not available on production")
    users = UserSQLEntity.query.filter(UserSQLEntity.id.in_(user_ids)).all()
    maximum_wallet_balance = 500
    for user in users:
        user.isBeneficiary = True
        deposit = create_deposit(user, amount=maximum_wallet_balance)
        repository.save(user, deposit)
