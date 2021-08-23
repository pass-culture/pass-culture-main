from pcapi.domain.client_exceptions import ClientError


class EducationalInstitutionUnknown(ClientError):
    def __init__(self) -> None:
        super().__init__("educationalInstitution", "Cette institution est inconnue")


class StockNotBookable(ClientError):
    def __init__(self, stock_id) -> None:
        super().__init__("stock", f"Le stock {stock_id} n'est pas réservable")


class EducationalYearNotFound(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "educationalYear", "Aucune année scolaire correspondant à la réservation demandée n'a été trouvée"
        )


class OfferIsNotEducational(ClientError):
    def __init__(self, offer_id) -> None:
        super().__init__("offer", f"L'offre {offer_id} n'est pas une offre éducationnelle")


class OfferIsNotEvent(ClientError):
    def __init__(self, offer_id) -> None:
        super().__init__("offer", f"L'offre {offer_id} n'est pas une offre évènementielle")


class InsufficientFund(Exception):
    pass


class InsufficientTemporaryFund(Exception):
    pass


class EducationalDepositNotFound(Exception):
    pass


class EducationalBookingNotFound(Exception):
    pass


class EducationalBookingNotConfirmedYet(Exception):
    pass


class EducationalBookingNotRefusable(Exception):
    pass


class EducationalBookingAlreadyCancelled(Exception):
    pass


class EducationalBookingIsRefused(Exception):
    pass


class BookingIsCancelled(Exception):
    pass
