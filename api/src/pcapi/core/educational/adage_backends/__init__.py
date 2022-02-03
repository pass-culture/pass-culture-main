from pcapi import settings
from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingEdition
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse
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
