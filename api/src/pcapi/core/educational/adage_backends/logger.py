import logging

from pcapi.core.educational.adage_backends.base import AdageNotifier
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse


logger = logging.getLogger(__name__)


class AdageLoggerNotifier(AdageNotifier):
    def notify_prebooking(self, data: EducationalBookingResponse) -> AdageApiResult:
        logger.info("Adage has been notified at %s, with payload: %s", self.url, data)
        return AdageApiResult(sent_data=data, response={"status_code": 201}, success=True)
