from pcapi.domain.client_exceptions import ClientError
from pcapi.models.api_errors import ApiErrors


class EducationalInstitutionUnknown(ClientError):
    def __init__(self) -> None:
        super().__init__("educationalInstitution", "Cette institution est inconnue")


class StockNotBookable(ClientError):
    def __init__(self, stock_id: int) -> None:
        super().__init__("stock", f"Le stock {stock_id} n'est pas réservable")


class EducationalYearNotFound(ClientError):
    def __init__(self) -> None:
        super().__init__(
            "educationalYear", "Aucune année scolaire correspondant à la réservation demandée n'a été trouvée"
        )


class OfferIsNotEducational(ClientError):
    def __init__(self, offer_id: int) -> None:
        super().__init__("offer", f"L'offre {offer_id} n'est pas une offre éducationnelle")


class OfferIsNotEvent(ClientError):
    def __init__(self, offer_id: int) -> None:
        super().__init__("offer", f"L'offre {offer_id} n'est pas une offre évènementielle")


class InsufficientFund(Exception):
    pass


class InsufficientMinistryFund(Exception):
    pass


class InsufficientTemporaryFund(Exception):
    pass


class EducationalDepositNotFound(Exception):
    pass


class EducationalBookingNotFound(Exception):
    pass


class EducationalBookingNotRefusable(Exception):
    pass


class EducationalBookingAlreadyCancelled(Exception):
    pass


class BookingIsCancelled(Exception):
    pass


class MissingRequiredRedactorInformation(Exception):
    pass


class EducationalStockAlreadyExists(Exception):
    pass


class OfferIsNotShowcase(Exception):
    pass


class CollectiveStockAlreadyExists(Exception):
    pass


class StockDoesNotExist(ApiErrors):
    status_code = 400


class CollectiveOfferStockBookedAndBookingNotPending(Exception):
    def __init__(self, status, booking_id):  # type: ignore [no-untyped-def]
        self.booking_status = status
        super().__init__()


class CollectiveOfferNotFound(Exception):
    pass


class CollectiveOfferTemplateNotFound(Exception):
    pass


class CollectiveStockNotFound(Exception):
    pass


class EducationalDomainsNotFound(Exception):
    pass


class EducationalInstitutionNotFound(Exception):
    pass


class CollectiveOfferNotEditable(Exception):
    pass


class CollectiveStockNotBookableByUser(Exception):
    pass


class AdageException(Exception):
    def __init__(self, message, status_code, response_text):  # type: ignore [no-untyped-def]
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(message)


class CulturalPartnerNotFoundException(Exception):
    pass


class InvalidInterventionArea(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__()
