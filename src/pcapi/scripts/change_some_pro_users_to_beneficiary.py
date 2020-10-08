from typing import List
from pcapi.models import UserSQLEntity, UserOfferer
from pcapi.repository import repository
from pcapi.model_creators.generic_creators import create_deposit


def change_pro_users_to_beneficiary(pro_users_ids: List[int]) -> None:
    users = UserSQLEntity.query.filter(UserSQLEntity.id.in_(pro_users_ids)).all()
    maximum_wallet_balance = 500
    for user in users:
        user.canBookFreeOffers = True
        user.needsToFillCulturalSurvey = True
        deposit = create_deposit(user, amount=maximum_wallet_balance)
        repository.save(user, deposit)
        user_offerer = UserOfferer.query.filter_by(user=user).all()
        repository.delete(*user_offerer)
