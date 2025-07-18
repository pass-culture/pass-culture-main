import datetime
import typing

from pcapi import settings
from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational import schemas as educational_schemas
from pcapi.core.educational.adage_backends import serialize
from pcapi.utils.module_loading import import_string


if typing.TYPE_CHECKING:
    from pcapi.core.educational.adage_backends.base import AdageClient


def _get_backend() -> "AdageClient":
    backend_class = import_string(settings.ADAGE_BACKEND)
    return backend_class()


def notify_prebooking(data: educational_schemas.EducationalBookingResponse) -> None:
    _get_backend().notify_prebooking(data=data)


def notify_offer_or_stock_edition(data: educational_schemas.EducationalBookingEdition) -> None:
    _get_backend().notify_offer_or_stock_edition(data=data)


def get_adage_offerer(siren: str) -> list[AdageVenue]:
    result = _get_backend().get_adage_offerer(siren=siren)
    return result


def notify_booking_cancellation_by_offerer(data: educational_schemas.EducationalBookingResponse) -> None:
    _get_backend().notify_booking_cancellation_by_offerer(data=data)


def get_cultural_partners(since_date: datetime.datetime | None = None) -> list[dict[str, str | int | float | None]]:
    result = _get_backend().get_cultural_partners(since_date=since_date)
    return result


def notify_institution_association(data: serialize.AdageCollectiveOffer) -> None:
    _get_backend().notify_institution_association(data=data)


def get_cultural_partner(siret: str) -> educational_schemas.AdageCulturalPartner:
    result = _get_backend().get_cultural_partner(siret)
    return result


def get_adage_educational_institutions(ansco: str) -> list[serialize.AdageEducationalInstitution]:
    result = _get_backend().get_adage_educational_institutions(ansco)
    return result


def get_adage_educational_redactor_from_uai(uai: str) -> list[dict[str, str]]:
    result = _get_backend().get_adage_educational_redactor_from_uai(uai)
    return result


def notify_reimburse_collective_booking(data: educational_schemas.AdageReimbursementNotification) -> None:
    _get_backend().notify_reimburse_collective_booking(data)


def notify_redactor_when_collective_request_is_made(data: serialize.AdageCollectiveRequest) -> None:
    _get_backend().notify_redactor_when_collective_request_is_made(data)
