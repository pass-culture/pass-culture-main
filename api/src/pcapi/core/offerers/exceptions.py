from pcapi.domain.client_exceptions import ClientError


class ApiKeyCountMaxReached(Exception):
    pass


class ApiKeyPrefixGenerationError(Exception):
    pass


class ApiKeyDeletionDenied(Exception):
    pass


class CannotFindOffererForOfferId(Exception):
    pass


class CannotFindOffererUserEmail(Exception):
    pass


class CannotFindOffererSiren(Exception):
    pass


class CannotFindProviderOfferer(Exception):
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


class OffererAlreadyValidatedException(Exception):
    pass


class OffererAlreadyRejectedException(Exception):
    pass


class UserOffererAlreadyValidatedException(Exception):
    pass


class InactiveSirenException(Exception):
    pass


class OffererAddressLabelAlreadyUsed(Exception):
    pass


class OffererAddressNotEditableException(Exception):
    pass


class OffererAddressCreationError(Exception):
    pass


class CannotSuspendOffererWithBookingsException(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "cannotSuspendOffererWithBookingsException",
            "Entité non désactivable car elle contient des réservations",
        )


class CannotDeleteOffererWithBookingsException(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "cannotDeleteOffererWithBookingsException",
            "Entité non supprimable car elle contient des réservations",
        )


class CannotDeleteVenueWithBookingsException(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "cannotDeleteVenueWithBookingsException",
            "Partenaire culturel non supprimable car il contient des réservations",
        )


class CannotDeleteVenueUsedAsPricingPointException(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "cannotDeleteVenueUsedAsPricingPointException",
            "Partenaire culturel non supprimable car il est utilisé comme point de valorisation d'un autre partenaire culturel",
        )


class CannotDeleteVenueUsedAsReimbursementPointException(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "cannotDeleteVenueUsedAsReimbursementPointException",
            "Partenaire culturel non supprimable car il est utilisé comme point de remboursement d'un autre partenaire culturel",
        )


class EmailAlreadyInvitedException(ClientError):
    def __init__(self) -> None:
        super().__init__("EmailAlreadyInvitedException", "Une invitation a déjà été envoyée à ce collaborateur")


class UserAlreadyAttachedToOffererException(ClientError):
    def __init__(self) -> None:
        super().__init__("UserAlreadyAttachedToOffererException", "Ce collaborateur est déjà membre de votre structure")
