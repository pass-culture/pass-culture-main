from pcapi.core.educational.adage_backends.base import AdageNotifier
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse

from .. import testing


class AdageSpyNotifier(AdageNotifier):
    def notify_prebooking(self, data: EducationalBookingResponse) -> AdageApiResult:
        testing.adage_requests.append({"url": self.url, "sent_data": data})
        return AdageApiResult(sent_data=data, response={"status_code": 201}, success=True)
