from pcapi.core.external_bookings.exceptions import ExternalBookingException


class BoostAPIException(ExternalBookingException):
    pass


class BoostInvalidTokenException(BoostAPIException):
    pass


class BoostLoginException(BoostAPIException):
    pass
