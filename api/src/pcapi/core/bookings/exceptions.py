from decimal import Decimal

from pcapi.models.api_errors import ApiErrors


class OfferIsAlreadyBooked(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error("offerId", "Cette offre a déja été reservée par l'utilisateur")


class QuantityIsInvalid(ApiErrors):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.add_error("quantity", message)


class StockIsNotBookable(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error("stock", "Ce stock n'est pas réservable")


class PhysicalExpenseLimitHasBeenReached(ApiErrors):
    def __init__(self, celling_amount: int) -> None:
        super().__init__()
        self.add_error(
            "global",
            f"Le plafond de {celling_amount} € pour les biens culturels ne vous permet pas " "de réserver cette offre.",
        )


class DigitalExpenseLimitHasBeenReached(ApiErrors):
    def __init__(self, celling_amount: Decimal) -> None:
        super().__init__()
        self.add_error(
            "global",
            f"Le plafond de {celling_amount} € pour les offres numériques ne vous permet pas "
            "de réserver cette offre.",
        )


class CannotBookFreeOffers(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error("cannotBookFreeOffers", "Votre compte ne vous permet pas de faire de réservation.")


class NoActivationCodeAvailable(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error("noActivationCodeAvailable", "Ce stock ne contient plus de code d'activation disponible.")


class OfferCategoryNotBookableByUser(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error("offerCategory", "Vous n'êtes pas autorisé à réserver cette catégorie d'offre")


class UserHasInsufficientFunds(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error("insufficientFunds", "Le solde de votre pass est insuffisant pour réserver cette offre.")


class BookingIsAlreadyUsed(Exception):
    pass


class BookingIsNotUsed(Exception):
    pass


class BookingHasActivationCode(Exception):
    pass


class BookingHasAlreadyBeenUsed(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error("booking", "Cette offre a déjà été utilisée")


class BookingIsAlreadyRefunded(Exception):
    pass


class BookingIsAlreadyCancelled(Exception):
    pass


class BookingIsNotCancelledCannotBeUncancelled(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error("booking", "Cette réservation n'est pas annulée et ne peut pas être dés-annulée")


class BookingIsCancelled(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error("booking", "Cette réservation a été annulée et ne peut être marquée comme étant utilisée")


class BookingRefused(Exception):
    pass


class BookingIsNotConfirmed(Exception):
    pass


class CannotCancelConfirmedBooking(ApiErrors):
    def __init__(self, after_creation: str, before_event: str) -> None:
        super().__init__()
        self.add_error("booking", f"Impossible d'annuler une réservation {after_creation}{before_event}")


class BookingDoesntExist(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error("bookingId", "bookingId ne correspond à aucune réservation")


class CannotDeleteBookingWithReimbursementException(ApiErrors):
    def __init__(self) -> None:
        super().__init__()
        self.add_error(
            "cannotDeleteBookingWithReimbursementException",
            "Réservation non supprimable car elle est liée à un remboursement",
        )


class OneSideCancellationForbidden(Exception):
    def __init__(self) -> None:
        super().__init__("Annulation unilatérale impossible")


class ConfirmationLimitDateHasPassed(Exception):
    pass


class BookingIsExpired(Exception):
    pass


class BookingDepositCreditExpired(Exception):
    pass
