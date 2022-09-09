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
