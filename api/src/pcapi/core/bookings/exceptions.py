from decimal import Decimal

from pcapi.domain.client_exceptions import ClientError


class OfferIsAlreadyBooked(ClientError):
    def __init__(self) -> None:
        super().__init__("offerId", "Cette offre a déja été reservée par l'utilisateur")


class QuantityIsInvalid(ClientError):
    def __init__(self, message: str) -> None:
        super().__init__("quantity", message)


class StockIsNotBookable(ClientError):
    def __init__(self) -> None:
        super().__init__("stock", "Ce stock n'est pas réservable")


class PhysicalExpenseLimitHasBeenReached(ClientError):
    def __init__(self, celling_amount: int) -> None:
        super().__init__(
            "global",
            f"Le plafond de {celling_amount} € pour les biens culturels ne vous permet pas " "de réserver cette offre.",
        )


class DigitalExpenseLimitHasBeenReached(ClientError):
    def __init__(self, celling_amount: Decimal) -> None:
        super().__init__(
            "global",
            f"Le plafond de {celling_amount} € pour les offres numériques ne vous permet pas "
            "de réserver cette offre.",
        )


class CannotBookFreeOffers(ClientError):
    def __init__(self) -> None:
        super().__init__("cannotBookFreeOffers", "Votre compte ne vous permet pas de faire de réservation.")


class NoActivationCodeAvailable(ClientError):
    def __init__(self) -> None:
        super().__init__("noActivationCodeAvailable", "Ce stock ne contient plus de code d'activation disponible.")


class EducationalOfferCannotBeBooked(ClientError):
    def __init__(self) -> None:
        super().__init__("offerId", "Cette offre est réservée aux rédacteurs de projets")


class OfferCategoryNotBookableByUser(ClientError):
    def __init__(self) -> None:
        super().__init__("offerCategory", "Vous n'êtes pas autorisé à réserver cette catégorie d'offre")


class UserHasInsufficientFunds(ClientError):
    def __init__(self) -> None:
        super().__init__("insufficientFunds", "Le solde de votre pass est insuffisant pour réserver cette offre.")


class BookingIsAlreadyUsed(Exception):
    pass


class BookingHasAlreadyBeenUsed(ClientError):
    def __init__(self) -> None:
        super().__init__("booking", "Cette offre a déjà été utilisée")


class BookingIsAlreadyRefunded(Exception):
    pass


class BookingIsAlreadyCancelled(Exception):
    pass


class BookingIsNotCancelledCannotBeUncancelled(ClientError):
    def __init__(self) -> None:
        super().__init__("booking", "Cette réservation n'est pas annulée et ne peut pas être dés-annulée")


class BookingIsCancelled(ClientError):
    def __init__(self) -> None:
        super().__init__("booking", "Cette réservation a été annulée et ne peut être marquée comme étant utilisée")


class BookingRefused(Exception):
    pass


class BookingIsNotConfirmed(Exception):
    pass


class CannotCancelConfirmedBooking(ClientError):
    def __init__(self, after_creation: str, before_event: str) -> None:
        super().__init__("booking", f"Impossible d'annuler une réservation {after_creation}{before_event}")


class BookingDoesntExist(ClientError):
    def __init__(self) -> None:
        super().__init__("bookingId", "bookingId ne correspond à aucune réservation")


class CannotDeleteBookingWithReimbursementException(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "cannotDeleteBookingWithReimbursementException",
            "Réservation non supprimable car elle est liée à un remboursement",
        )


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


class CannotMarkAsConfirmedIndividualBooking(Exception):
    pass


class ConfirmationLimitDateHasPassed(Exception):
    pass


class BookingIsExpired(Exception):
    pass


class BookingNotConfirmed(Exception):
    pass
