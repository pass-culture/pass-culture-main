class ExternalBookingException(Exception):
    pass


class ExternalBookingSoldOutError(Exception):
    pass


class ExternalBookingNotEnoughSeatsError(Exception):
    pass
