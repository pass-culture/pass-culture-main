class ExternalBookingException(Exception):
    pass


class ExternalBookingConfigurationException(ExternalBookingException):
    pass


class ExternalBookingTimeoutException(Exception):
    pass


class ExternalBookingAlreadyCancelledError(Exception):
    def __init__(self, remainingQuantity: int | None) -> None:
        self.remainingQuantity = remainingQuantity
        super().__init__()


class ExternalBookingNotEnoughSeatsError(Exception):
    def __init__(self, remainingQuantity: int) -> None:
        self.remainingQuantity = remainingQuantity
        super().__init__()


class ExternalBookingShowDoesNotExistError(Exception):
    """
    Exception raised when show does no longer exist on provider side
    (this error can occur with cinema integrations)
    """

    pass
