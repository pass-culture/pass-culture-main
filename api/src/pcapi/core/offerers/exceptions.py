from pcapi.models.api_errors import ApiErrors


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


class CannotSuspendOffererWithBookingsException(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error(
            "cannotSuspendOffererWithBookingsException",
            "Entité juridique non désactivable car elle contient des réservations",
        )


class CannotDeleteOffererWithBookingsException(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error(
            "cannotDeleteOffererWithBookingsException",
            "Entité juridique non supprimable car elle contient des réservations",
        )


class CannotDeleteVenueWithBookingsException(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error(
            "cannotDeleteVenueWithBookingsException",
            "Partenaire culturel non supprimable car il contient des réservations",
        )


class CannotDeleteVenueUsedAsPricingPointException(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error(
            "cannotDeleteVenueUsedAsPricingPointException",
            "Partenaire culturel non supprimable car il est utilisé comme point de valorisation d'un autre partenaire culturel",
        )


class CannotDeleteVenueUsedAsReimbursementPointException(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error(
            "cannotDeleteVenueUsedAsReimbursementPointException",
            "Partenaire culturel non supprimable car il est utilisé comme point de remboursement d'un autre partenaire culturel",
        )


class EmailAlreadyInvitedException(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error("EmailAlreadyInvitedException", "Une invitation a déjà été envoyée à ce collaborateur")


class UserAlreadyAttachedToOffererException(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error("UserAlreadyAttachedToOffererException", "Ce collaborateur est déjà membre de votre structure")
