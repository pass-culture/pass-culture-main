from pcapi.models.api_errors import ApiErrors


class NotEligible(Exception):
    pass


class AlreadyActivatedException(ApiErrors):
    pass
