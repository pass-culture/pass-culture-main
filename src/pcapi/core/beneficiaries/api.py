from pcapi.core.users import api as users_api
from pcapi.models import Deposit
from pcapi.models import UserSQLEntity
from pcapi.models.db import db
from pcapi.models.deposit import DEPOSIT_DEFAULT_AMOUNT

from . import exceptions


def activate_beneficiary(user: UserSQLEntity, deposit_source: str) -> UserSQLEntity:
    if not users_api.is_user_eligible(user):
        raise exceptions.NotEligible()
    user.isBeneficiary = True
    deposit = create_deposit(user, deposit_source=deposit_source)
    db.session.add_all((user, deposit))
    db.session.flush()
    return user


def create_deposit(beneficiary: UserSQLEntity, deposit_source: str) -> Deposit:

    # should we add a check ?
    # existing_deposits = Deposit.query.filter_by(userId=user_to_activate.id).all()
    # if existing_deposits:
    #     error = AlreadyActivatedException()
    #     error.add_error("user", "Cet utilisateur a déjà crédité son pass Culture")
    #     raise error

    deposit = Deposit(
        amount=DEPOSIT_DEFAULT_AMOUNT,
        source=deposit_source,
        userId=beneficiary.id,
    )
    return deposit
