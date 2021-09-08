class FinanceError(Exception):
    pass


class NonCancellablePricingError(FinanceError):
    pass
