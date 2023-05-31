from pcapi import settings
from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational.adage_backends import serialize
from pcapi.routes.adage.v1.serialization.prebooking import AdageReibursementNotification
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingEdition
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse
from pcapi.routes.serialization import venues_serialize
from pcapi.utils.module_loading import import_string


def notify_prebooking(data: EducationalBookingResponse) -> None:
    backend = import_string(settings.ADAGE_BACKEND)
    backend().notify_prebooking(data=data)


def notify_offer_or_stock_edition(data: EducationalBookingEdition) -> None:
    backend = import_string(settings.ADAGE_BACKEND)
    backend().notify_offer_or_stock_edition(data=data)


def get_adage_offerer(siren: str) -> list[AdageVenue]:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().get_adage_offerer(siren=siren)
    return result


def notify_booking_cancellation_by_offerer(data: EducationalBookingResponse) -> None:
    backend = import_string(settings.ADAGE_BACKEND)
    backend().notify_booking_cancellation_by_offerer(data=data)


def get_cultural_partners() -> list[dict[str, str | int | float | None]]:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().get_cultural_partners()
    return result


def notify_institution_association(data: serialize.AdageCollectiveOffer) -> None:
    backend = import_string(settings.ADAGE_BACKEND)
    backend().notify_institution_association(data=data)


def get_cultural_partner(siret: str) -> venues_serialize.AdageCulturalPartner:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().get_cultural_partner(siret)
    return result


def get_adage_educational_institutions(ansco: str) -> list[serialize.AdageEducationalInstitution]:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().get_adage_educational_institutions(ansco)
    return result


def get_adage_educational_redactor_from_uai(uai: str) -> list[dict[str, str]]:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().get_adage_educational_redactor_from_uai(uai)
    return result


def notify_reimburse_collective_booking(data: AdageReibursementNotification) -> None:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().notify_reimburse_collective_booking(data)
    return result


def notify_redactor_when_collective_request_is_made(data: serialize.AdageCollectiveRequest) -> None:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().notify_redactor_when_collective_request_is_made(data)
    return result
