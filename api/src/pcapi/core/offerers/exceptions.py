from pcapi.domain.client_exceptions import ClientError


class ApiKeyCountMaxReached(Exception):
    pass


class ApiKeyPrefixGenerationError(Exception):
    pass


class CannotFindOffererForOfferId(Exception):
    pass


class CannotFindOffererUserEmail(Exception):
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


class OffererAlreadyClosedException(Exception):
    pass


class FutureClosureDate(Exception):
    pass


class UserOffererAlreadyValidatedException(Exception):
    pass


class InactiveSirenException(Exception):
    pass


class NotACollectivity(Exception):
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
            "Entité juridique non désactivable car elle contient des réservations",
        )


class CannotDeleteOffererWithBookingsException(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "cannotDeleteOffererWithBookingsException",
            "Entité juridique non supprimable car elle contient des réservations",
        )


class CannotDeleteOffererWithActiveOrFutureCustomReimbursementRule(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "CannotDeleteOffererWithActiveOrFutureCustomReimbursementRule",
            "Entité juridique non supprimable car elle est associée à un tarif dérogatoire",
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


class CannotDeleteVenueWithActiveOrFutureCustomReimbursementRule(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "CannotDeleteVenueWithActiveOrFutureCustomReimbursementRule",
            "Partenaire culturel non supprimable car il est associé à un tarif dérogatoire",
        )


class EmailAlreadyInvitedException(ClientError):
    def __init__(self) -> None:
        super().__init__("EmailAlreadyInvitedException", "Une invitation a déjà été envoyée à ce collaborateur")


class InviteAgainImpossibleException(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "InviteAgainImpossibleException", "Impossible de renvoyer une invitation pour ce collaborateur"
        )


class UserAlreadyAttachedToOffererException(ClientError):
    def __init__(self) -> None:
        super().__init__("UserAlreadyAttachedToOffererException", "Ce collaborateur est déjà membre de votre structure")
