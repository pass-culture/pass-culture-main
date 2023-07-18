class BoostAPIException(Exception):
    pass


class BoostInvalidTokenException(BoostAPIException):
    pass


class BoostLoginException(BoostAPIException):
    pass
