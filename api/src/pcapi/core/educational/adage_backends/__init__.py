from pcapi import settings
from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational.adage_backends.serialize import AdageCollectiveOffer
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingEdition
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse
from pcapi.routes.serialization import venues_serialize
from pcapi.utils.module_loading import import_string


def notify_prebooking(data: EducationalBookingResponse) -> AdageApiResult:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().notify_prebooking(data=data)
    return result


def notify_offer_or_stock_edition(data: EducationalBookingEdition) -> AdageApiResult:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().notify_offer_or_stock_edition(data=data)
    return result


def get_adage_offerer(siren: str) -> list[AdageVenue]:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().get_adage_offerer(siren=siren)
    return result


def notify_booking_cancellation_by_offerer(data: EducationalBookingResponse) -> AdageApiResult:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().notify_booking_cancellation_by_offerer(data=data)
    return result


def get_cultural_partners() -> list[dict[str, str | int | float | None]]:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().get_cultural_partners()
    return result


def notify_institution_association(data: AdageCollectiveOffer) -> AdageApiResult:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().notify_institution_association(data=data)
    return result


def get_cultural_partner(siret: str) -> venues_serialize.AdageCulturalPartner:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().get_cultural_partner(siret)
    return result
