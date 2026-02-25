import datetime
import typing

from pcapi import settings
from pcapi.core.educational import schemas
from pcapi.core.educational.adage.backends.adage import AdageHttpClient
from pcapi.core.educational.adage.backends.logger import AdageLoggerClient
from pcapi.core.educational.adage.backends.testing import AdageSpyClient


type Client = AdageHttpClient | AdageLoggerClient | AdageSpyClient

BACKEND_BY_KEY: typing.Final[dict[str, type[Client]]] = {
    "AdageHttpClient": AdageHttpClient,
    "AdageLoggerClient": AdageLoggerClient,
    "AdageSpyClient": AdageSpyClient,
    # TODO(jcicurel-pass): we keep these imports for now until we have updated the ADAGE_BACKEND setting in each environment
    "pcapi.core.educational.adage_backends.adage.AdageHttpClient": AdageHttpClient,
    "pcapi.core.educational.adage_backends.logger.AdageLoggerClient": AdageLoggerClient,
    "pcapi.core.educational.adage_backends.testing.AdageSpyClient": AdageSpyClient,
}


def _get_backend() -> Client:
    return BACKEND_BY_KEY[settings.ADAGE_BACKEND]()


def notify_prebooking(data: schemas.EducationalBookingResponse) -> None:
    _get_backend().notify_prebooking(data=data)


def notify_offer_or_stock_edition(data: schemas.EducationalBookingEdition) -> None:
    _get_backend().notify_offer_or_stock_edition(data=data)


def get_adage_offerer(siren: str) -> list[schemas.AdageCulturalPartner]:
    result = _get_backend().get_adage_offerer(siren=siren)
    return result


def notify_booking_cancellation_by_offerer(data: schemas.EducationalBookingResponse) -> None:
    _get_backend().notify_booking_cancellation_by_offerer(data=data)


def get_cultural_partners(since_date: datetime.datetime | None = None) -> list[dict[str, str | int | float | None]]:
    result = _get_backend().get_cultural_partners(since_date=since_date)
    return result


def notify_institution_association(data: schemas.AdageCollectiveOffer) -> None:
    _get_backend().notify_institution_association(data=data)


def get_adage_educational_institutions(ansco: str) -> list[schemas.AdageEducationalInstitution]:
    result = _get_backend().get_adage_educational_institutions(ansco)
    return result


def get_adage_educational_redactor_from_uai(uai: str) -> list[dict[str, str]]:
    result = _get_backend().get_adage_educational_redactor_from_uai(uai)
    return result


def notify_reimburse_collective_booking(data: schemas.AdageReimbursementNotification) -> None:
    _get_backend().notify_reimburse_collective_booking(data)


def notify_redactor_when_collective_request_is_made(data: schemas.AdageCollectiveRequest) -> None:
    _get_backend().notify_redactor_when_collective_request_is_made(data)
