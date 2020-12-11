from pcapi.models.deposit import DEPOSIT_DEFAULT_AMOUNT
from pcapi.models.deposit import Deposit
from pcapi.models import UserSQLEntity


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
