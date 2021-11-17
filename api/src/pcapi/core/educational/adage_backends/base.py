from pcapi import settings
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse


class AdageNotifier:
    def __init__(self):
        self.base_url = settings.ADAGE_API_URL
        self.url = f"{self.base_url}/v1/prereservation"

    def notify_prebooking(self, data: EducationalBookingResponse) -> AdageApiResult:
        raise NotImplementedError()
