from pcapi.domain.client_exceptions import ClientError
from pcapi.models.api_errors import ApiErrors

from . import models


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


class CollectiveBookingAlreadyCancelled(Exception):
    pass


class BookingIsCancelled(Exception):
    pass


class MissingRequiredRedactorInformation(Exception):
    pass


class EducationalStockAlreadyExists(Exception):
    pass


class CollectiveStockAlreadyExists(Exception):
    pass


class StockDoesNotExist(ApiErrors):
    status_code = 400


class PriceRequesteCantBedHigherThanActualPrice(Exception):
    pass


class CollectiveOfferStockBookedAndBookingNotPending(Exception):
    def __init__(self, status: models.CollectiveBookingStatus, booking_id: int) -> None:
        self.booking_status = status
        super().__init__()


class CollectiveOfferNotFound(Exception):
    pass


class CollectiveOfferRequestNotFound(Exception):
    pass


class CollectiveOfferTemplateNotFound(Exception):
    pass


class CollectiveOfferIsPublicApi(Exception):
    pass


class CollectiveStockNotFound(Exception):
    pass


class EducationalDomainsNotFound(Exception):
    pass


class EducationalDomainNotFound(Exception):
    pass


class EducationalInstitutionNotFound(Exception):
    pass


class OffererOfVenueDontMatchOfferer(Exception):
    pass


class VenueIdDontExist(Exception):
    pass


class EducationalInstitutionIsNotActive(Exception):
    pass


class EducationalRedcatorCannotBeLinked(Exception):
    pass


class CollectiveOfferNotEditable(Exception):
    pass


class CollectiveStockNotBookableByUser(Exception):
    pass


class AdageException(Exception):
    def __init__(self, message: str, status_code: int, response_text: str) -> None:
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(message)


class CulturalPartnerNotFoundException(Exception):
    pass


class CollectiveBookingIsAlreadyUsed(Exception):
    pass


class InvalidInterventionArea(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__()


class NoCollectiveBookingToCancel(Exception):
    pass


class AdageEducationalInstitutionNotFound(Exception):
    pass


class BookingIsAlreadyRefunded(Exception):
    pass


class EducationalRedactorNotFound(Exception):
    pass


class ValidationFailedOnCollectiveOffer(Exception):
    pass


class OffererNotAllowedToDuplicate(Exception):
    pass


class CantGetImageFromUrl(Exception):
    pass


class NationalProgramNotFound(Exception):
    pass


class NoAdageInstitution(Exception):
    pass


class MissingAdageInstitution(Exception):
    pass


class UpdateCollectiveOfferTemplateError(Exception):
    field = "global"
    msg = ""


class StartsBeforeOfferCreation(UpdateCollectiveOfferTemplateError):
    field = "dates.start"
    msg = "Can't start before template creation date"


class StartAndEndEducationalYearDifferent(Exception):
    field = "dates.start"
    msg = "start and end dates in different school year"
