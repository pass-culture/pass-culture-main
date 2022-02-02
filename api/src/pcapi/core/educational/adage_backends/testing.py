from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational.adage_backends.base import AdageClient
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse

from .. import testing


class AdageSpyClient(AdageClient):
    def notify_prebooking(self, data: EducationalBookingResponse) -> AdageApiResult:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/prereservation", "sent_data": data})
        return AdageApiResult(sent_data=data, response={"status_code": 201}, success=True)

    def notify_offer_or_stock_edition(self, data: EducationalBookingResponse) -> AdageApiResult:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/prereservation-edit", "sent_data": data})
        return AdageApiResult(sent_data=data.dict(), response={"status_code": 201}, success=True)

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        raise Exception("Do not use the spy for this method, mock the get request instead")

    def notify_booking_cancellation_by_offerer(self, data: EducationalBookingResponse) -> AdageApiResult:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/prereservation-annule", "sent_data": data})
        return AdageApiResult(sent_data=data.dict(), response={"status_code": 201}, success=True)
