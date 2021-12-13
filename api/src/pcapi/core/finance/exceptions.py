class FinanceError(Exception):
    pass


class NonCancellablePricingError(FinanceError):
    pass


class InvalidSiret(Exception):
    pass
