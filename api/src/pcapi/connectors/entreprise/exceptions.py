class EntrepriseException(Exception):
    pass  # base class, never raised directly


SireneException = EntrepriseException


class ApiException(EntrepriseException):
    pass  # error from the API itself


class ApiUnavailable(ApiException):
    pass


class RateLimitExceeded(ApiException):
    pass


class UnknownEntityException(EntrepriseException):
    pass  # SIREN or SIRET that does not exist


class InvalidFormatException(EntrepriseException):
    pass  # likely a SIREN or SIRET with the wrong number of digits


class NonPublicDataException(EntrepriseException):
    # Some SIREN/SIRET is marked as "non diffusibles", which means
    # that we cannot access information about them from the Sirene
    # API.
    pass
