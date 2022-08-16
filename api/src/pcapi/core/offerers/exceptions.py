class ApiKeyCountMaxReached(Exception):
    pass


class ApiKeyPrefixGenerationError(Exception):
    pass


class ApiKeyDeletionDenied(Exception):
    pass


class ValidationTokenNotFoundError(Exception):
    pass


class CannotFindOffererForOfferId(Exception):
    pass


class CannotFindOffererUserEmail(Exception):
    pass


class CannotFindOffererSiren(Exception):
    pass


class MissingOffererIdQueryParameter(Exception):
    pass


class InvalidVenueBannerContent(Exception):
    pass


class VenueBannerTooBig(Exception):
    pass


class CannotLinkVenueToPricingPoint(Exception):
    pass


class VenueNotFoundException(Exception):
    pass
