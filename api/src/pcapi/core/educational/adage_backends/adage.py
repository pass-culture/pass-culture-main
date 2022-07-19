from pydantic import parse_obj_as

from pcapi import settings
from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational.adage_backends.base import AdageClient
from pcapi.core.educational.adage_backends.serialize import AdageCollectiveOffer
from pcapi.core.educational.exceptions import AdageException
from pcapi.core.educational.exceptions import CulturalPartnerNotFoundException
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingEdition
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse
from pcapi.utils import requests


class AdageHttpClient(AdageClient):
    def __init__(self) -> None:
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

        return AdageApiResult(sent_data=data, response=dict(api_response.json()), success=True)  # type: ignore [arg-type]

    def notify_offer_or_stock_edition(self, data: EducationalBookingEdition) -> AdageApiResult:
        api_url = f"{self.base_url}/v1/prereservation-edit"
        api_response = requests.post(
            api_url,
            headers={self.header_key: self.api_key, "Content-Type": "application/json"},
            data=data.json(),
        )

        if api_response.status_code != 201:
            raise AdageException(
                "Error posting booking edition notification to Adage API.",
                api_response.status_code,
                api_response.text,
            )

        return AdageApiResult(sent_data=data.dict(), response=dict(api_response.json()), success=True)

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        api_url = f"{self.base_url}/v1/partenaire-culturel/{siren}"

        api_response = requests.get(
            api_url,
            headers={self.header_key: self.api_key},
        )

        if api_response.status_code == 404:
            raise CulturalPartnerNotFoundException("Requested siren is not a known cultural partner for Adage")
        if api_response.status_code != 200:
            raise AdageException("Error getting Adage API", api_response.status_code, api_response.text)

        return parse_obj_as(list[AdageVenue], api_response.json())

    def notify_booking_cancellation_by_offerer(self, data: EducationalBookingResponse) -> AdageApiResult:
        api_url = f"{self.base_url}/v1/prereservation-annule"
        api_response = requests.post(
            api_url,
            headers={self.header_key: self.api_key, "Content-Type": "application/json"},
            data=data.json(),
        )

        if api_response.status_code != 201:
            raise AdageException(
                "Error posting booking cancellation by offerer notification to Adage API.",
                api_response.status_code,
                api_response.text,
            )

        return AdageApiResult(sent_data=data.dict(), response=dict(api_response.json()), success=True)

    def get_cultural_partners(self) -> list[dict[str, str | int | float | None]]:
        api_url = f"{self.base_url}/v1/partenaire-culturel"
        api_response = requests.get(
            api_url,
            headers={self.header_key: self.api_key},
        )

        if api_response.status_code == 404:
            raise CulturalPartnerNotFoundException("Requested  cultural partners not found for Adage")
        if api_response.status_code != 200:
            raise AdageException("Error getting Adage API", api_response.status_code, api_response.text)

        return api_response.json()

    def notify_institution_association(self, data: AdageCollectiveOffer) -> AdageApiResult:
        api_url = f"{self.base_url}/v1/offre-assoc"
        api_response = requests.post(
            api_url, headers={self.header_key: self.api_key, "Content-Type": "application/json"}, data=data.json()
        )

        if api_response.status_code != 200:
            raise AdageException("Error getting Adage API", api_response.status_code, api_response.text)

        return AdageApiResult(sent_data=data.dict(), response=dict(api_response.json()), success=True)
