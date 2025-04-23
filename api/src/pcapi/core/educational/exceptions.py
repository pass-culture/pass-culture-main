import typing

from pcapi.core.core_exception import CoreException


if typing.TYPE_CHECKING:
    from pcapi.core.educational.models import CollectiveBookingStatus
    from pcapi.core.educational.models import CollectiveOfferAllowedAction
    from pcapi.core.educational.models import CollectiveOfferTemplateAllowedAction


class EducationalException(CoreException):
    pass


class EducationalInstitutionUnknown(EducationalException):
    pass


class CollectiveStockNotBookable(EducationalException):
    pass


class EducationalYearNotFound(EducationalException):
    pass


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


class CollectiveStockAlreadyExists(Exception):
    pass


class CollectiveStockDoesNotExist(EducationalException):
    pass


class PriceRequesteCantBedHigherThanActualPrice(Exception):
    pass


class CollectiveOfferStockBookedAndBookingNotPending(Exception):
    def __init__(self, status: "CollectiveBookingStatus", booking_id: int) -> None:
        self.booking_status = status
        super().__init__()


class MultipleCollectiveBookingFound(Exception):
    pass


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


class EducationalInstitutionNotFound(Exception):
    pass


class OffererOfVenueDontMatchOfferer(Exception):
    pass


class VenueIdDontExist(Exception):
    pass


class EducationalInstitutionIsNotActive(Exception):
    pass


class EducationalRedactorCannotBeLinked(Exception):
    pass


class CollectiveOfferNotEditable(Exception):
    pass


class CollectiveOfferForbiddenAction(Exception):
    def __init__(self, action: "CollectiveOfferAllowedAction") -> None:
        self.action = action
        super().__init__()


class CollectiveOfferTemplateForbiddenAction(Exception):
    def __init__(self, action: "CollectiveOfferTemplateAllowedAction") -> None:
        self.action = action
        super().__init__()


class CollectiveOfferForbiddenFields(Exception):
    def __init__(self, allowed_fields: list[str]) -> None:
        self.allowed_fields = allowed_fields
        super().__init__()


class CollectiveStockNotBookableByUser(Exception):
    pass


class AdageException(Exception):
    def __init__(self, message: str, status_code: int, response_text: str) -> None:
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(message)


class AdageInvalidEmailException(AdageException):
    pass


class CulturalPartnerNotFoundException(Exception):
    pass


class CollectiveBookingIsAlreadyUsed(Exception):
    pass


class NoCollectiveBookingToCancel(Exception):
    pass


class AdageEducationalInstitutionNotFound(Exception):
    pass


class BookingIsAlreadyRefunded(Exception):
    pass


class EducationalRedactorNotFound(Exception):
    pass


class OffererNotAllowedToDuplicate(Exception):
    pass


class CantGetImageFromUrl(Exception):
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


class StartEducationalYearMissing(Exception):
    field = "dates.start"
    msg = "no educational year/budget for the given start date"


class EndEducationalYearMissing(Exception):
    field = "dates.end"
    msg = "no educational year/budget for the given end date"


class EndDatetimeBeforeStartDatetime(Exception):
    pass


# DOMAINS / NATIONAL PROGRAMS
class EducationalDomainsNotFound(Exception):
    pass


class EducationalDomainNotFound(Exception):
    pass


class MissingDomains(Exception):
    pass


class NationalProgramNotFound(Exception):
    pass


class IllegalNationalProgram(Exception):
    pass


class InactiveNationalProgram(Exception):
    pass
