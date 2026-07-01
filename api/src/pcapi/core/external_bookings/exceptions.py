class ExternalBookingException(Exception):
    pass


class ConfigurationException(ExternalBookingException):
    pass


class TimeoutException(Exception):
    pass


class ExternalBookingAlreadyCancelledError(Exception):
    def __init__(self, remainingQuantity: int | None) -> None:
        self.remainingQuantity = remainingQuantity
        super().__init__()


class ShowSoldOutException(Exception):
    def __init__(self, remainingQuantity: int) -> None:
        self.remainingQuantity = remainingQuantity
        super().__init__()


class ShowRemovedException(Exception):
    """
    Exception raised when show does no longer exist on provider side
    (this error can occur with cinema integrations)
    """

    pass
