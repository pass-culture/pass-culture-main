from pcapi import settings
import pcapi.core.payments.api as payments_api
from pcapi.core.users.models import User
from pcapi.repository import repository


def grant_wallet_to_existing_users(user_ids: list[int]):
    if settings.IS_PROD:
        raise ValueError("This action is not available on production")
    users = User.query.filter(User.id.in_(user_ids)).all()
    for user in users:
        user.add_beneficiary_role()
        deposit = payments_api.create_deposit(user, "public")
        repository.save(user, deposit)
