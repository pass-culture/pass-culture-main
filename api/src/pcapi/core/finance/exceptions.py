class FinanceError(Exception):
    pass


class NonCancellablePricingError(FinanceError):
    pass


class InvalidSiret(Exception):
    pass


class WrongLengthSiret(InvalidSiret):
    pass


class NotAllDigitSiret(InvalidSiret):
    pass


class ReimbursementRuleValidationError(Exception):
    pass


class ConflictingReimbursementRule(ReimbursementRuleValidationError):
    def __init__(self, msg, conflicts):  # type: ignore [no-untyped-def]
        super().__init__(msg)
        self.conflicts = conflicts


class WrongDateForReimbursementRule(ReimbursementRuleValidationError):
    pass


class UnknownSubcategoryForReimbursementRule(ReimbursementRuleValidationError):
    pass
