from pcapi.models.api_errors import ApiErrors

from . import models


class FinanceError(Exception):
    pass


class NonCancellablePricingError(FinanceError):
    pass


class InvalidSiret(Exception):
    pass


class ReimbursementRuleValidationError(Exception):
    pass


class ConflictingReimbursementRule(ReimbursementRuleValidationError):
    def __init__(self, msg: str, conflicts: set) -> None:
        super().__init__(msg)
        self.conflicts = conflicts


class WrongDateForReimbursementRule(ReimbursementRuleValidationError):
    pass


class UnknownSubcategoryForReimbursementRule(ReimbursementRuleValidationError):
    pass


class DepositTypeAlreadyGrantedException(ApiErrors):
    def __init__(self, deposit_type: models.DepositType) -> None:
        super().__init__({"user": [f'Cet utilisateur a déjà été crédité de la subvention "{deposit_type.name}".']})


class UserNotGrantable(Exception):
    pass


class UserHasAlreadyActiveDeposit(UserNotGrantable):
    pass
