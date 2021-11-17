from pcapi import settings
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse
from pcapi.utils.module_loading import import_string


def notify_prebooking(data: EducationalBookingResponse) -> AdageApiResult:
    backend = import_string(settings.ADAGE_BACKEND)
    result = backend().notify_prebooking(data=data)
    return result
