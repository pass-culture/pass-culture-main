from pcapi.core.payments.models import DepositType
from pcapi.models.api_errors import ApiErrors


class DepositTypeAlreadyGrantedException(ApiErrors):
    def __init__(self, deposit_type: DepositType) -> None:
        super().__init__({"user": [f'Cet utilisateur a déjà été crédité de la subvention "{deposit_type.name}".']})


class UserNotGrantable(Exception):
    pass


class UserHasAlreadyActiveDeposit(UserNotGrantable):
    pass
