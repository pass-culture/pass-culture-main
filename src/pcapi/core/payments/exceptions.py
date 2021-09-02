from pcapi.models.api_errors import ApiErrors
from pcapi.models.deposit import DepositType


class DepositTypeAlreadyGrantedException(ApiErrors):
    def __init__(self, deposit_type: DepositType) -> None:
        super().__init__({"user": [f'Cet utilisateur a déjà été crédité de la subvention "{deposit_type.name}".']})


class NoMatchingGrantForUserException(ApiErrors):
    def __init__(self, age) -> None:
        super().__init__({"user": [f"Aucune subvention n'existe pour l'âge de l'utilisateur ({age} ans)"]})
