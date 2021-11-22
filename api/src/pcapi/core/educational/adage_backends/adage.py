import requests

from pcapi import settings
from pcapi.connectors.api_adage import AdageException
from pcapi.core.educational.adage_backends.base import AdageNotifier
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse


class AdageHttpNotifier(AdageNotifier):
    def __init__(self):
        self.api_key = settings.ADAGE_API_KEY
        self.header_key = "X-omogen-api-key"
        super().__init__()

    def notify_prebooking(self, data: EducationalBookingResponse) -> AdageApiResult:
        api_response = requests.post(
            self.url,
            headers={self.header_key: self.api_key, "Content-Type": "application/json"},
            data=data.json(),
        )

        if api_response.status_code != 201:
            raise AdageException(
                "Error posting new prebooking to Adage API.", api_response.status_code, api_response.text
            )

        return AdageApiResult(sent_data=data, response=dict(api_response.json()), success=True)
