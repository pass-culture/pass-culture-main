from pcapi.models import UserSQLEntity
from pcapi.models.deposit import DEPOSIT_DEFAULT_AMOUNT
from pcapi.models.deposit import Deposit

from . import exceptions


def create_deposit(beneficiary: UserSQLEntity, deposit_source: str) -> Deposit:
    existing_deposits = bool(Deposit.query.filter_by(userId=beneficiary.id).count())
    if existing_deposits:
        raise exceptions.AlreadyActivatedException({"user": ["Cet utilisateur a déjà crédité son pass Culture"]})

    deposit = Deposit(
        amount=DEPOSIT_DEFAULT_AMOUNT,
        source=deposit_source,
        userId=beneficiary.id,
    )
    return deposit
