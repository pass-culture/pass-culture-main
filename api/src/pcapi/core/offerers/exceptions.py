from pcapi.domain.client_exceptions import ClientError


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


class OffererNotFoundException(Exception):
    pass


class OffererAlreadyValidatedException(Exception):
    pass


class OffererAlreadyRejectedException(Exception):
    pass


class UserOffererNotFoundException(Exception):
    pass


class UserOffererAlreadyValidatedException(Exception):
    pass


class CannotDeleteOffererWithBookingsException(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "cannotDeleteOffererWithBookingsException",
            "Structure juridique non supprimable car elle contient des réservations",
        )


class CannotDeleteVenueWithBookingsException(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "cannotDeleteVenueWithBookingsException",
            "Lieu non supprimable car il contient des réservations",
        )


class CannotDeleteOffererUsedAsPricingPointException(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "cannotDeleteOffererUsedAsPricingPointException",
            "Structure juridique non supprimable car elle est utilisée comme point de valorisation d'un lieu",
        )


class CannotDeleteVenueUsedAsPricingPointException(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "cannotDeleteVenueUsedAsPricingPointException",
            "Lieu non supprimable car il est utilisé comme point de valorisation d'un autre lieu",
        )
