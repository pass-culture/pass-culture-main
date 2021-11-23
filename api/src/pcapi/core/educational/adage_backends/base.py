from pcapi import settings
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse


class AdageClient:
    def __init__(self):
        self.base_url = settings.ADAGE_API_URL

    def notify_prebooking(self, data: EducationalBookingResponse) -> AdageApiResult:
        raise NotImplementedError()
