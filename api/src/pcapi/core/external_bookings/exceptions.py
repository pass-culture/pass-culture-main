class ExternalBookingException(Exception):
    pass


class ExternalBookingSoldOutError(Exception):
    pass


class ExternalBookingNotEnoughSeatsError(Exception):
    def __init__(self, remainingQuantity: int) -> None:
        self.remainingQuantity = remainingQuantity
        super().__init__()
