from pydantic import parse_obj_as
import requests

from pcapi import settings
from pcapi.connectors.api_adage import AdageException
from pcapi.core.educational.adage_backends.base import AdageClient
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse


class AdageHttpClient(AdageClient):
    def __init__(self):
        self.api_key = settings.ADAGE_API_KEY
        self.header_key = "X-omogen-api-key"
        super().__init__()

    def notify_prebooking(self, data: EducationalBookingResponse) -> AdageApiResult:
        api_url = f"{self.base_url}/v1/prereservation"
        api_response = requests.post(
            api_url,
            headers={self.header_key: self.api_key, "Content-Type": "application/json"},
            data=data.json(),
        )

        if api_response.status_code != 201:
            raise AdageException(
                "Error posting new prebooking to Adage API.", api_response.status_code, api_response.text
            )

        return AdageApiResult(sent_data=data, response=dict(api_response.json()), success=True)
