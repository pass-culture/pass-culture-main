from pydantic import parse_obj_as

from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational.adage_backends.base import AdageClient
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization import venue as venue_serialization
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse

from .. import testing


class AdageSpyClient(AdageClient):
    def notify_prebooking(self, data: EducationalBookingResponse) -> AdageApiResult:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/prereservation", "sent_data": data})
        return AdageApiResult(sent_data=data, response={"status_code": 201}, success=True)  # type: ignore [arg-type]

    def notify_offer_or_stock_edition(self, data: EducationalBookingResponse) -> AdageApiResult:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/prereservation-edit", "sent_data": data})
        return AdageApiResult(sent_data=data.dict(), response={"status_code": 201}, success=True)

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        raise Exception("Do not use the spy for this method, mock the get request instead")

    def notify_booking_cancellation_by_offerer(self, data: EducationalBookingResponse) -> AdageApiResult:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/prereservation-annule", "sent_data": data})
        return AdageApiResult(sent_data=data.dict(), response={"status_code": 201}, success=True)

    def get_cultural_partners(self) -> venue_serialization.AdageCulturalPartners:
        testing.adage_requests.append({"url": f"{self.base_url}/v1/partenaire-culturel", "sent_data": ""})
        data = [
            {
                "id": 0,
                "venueId": 0,
                "siret": 0,
                "regionId": 0,
                "academieId": "string",
                "statutId": 0,
                "labelId": 0,
                "typeId": 0,
                "communeId": "string",
                "libelle": "string",
                "adresse": "string",
                "siteWeb": 0,
                "latitude": 0,
                "longitude": 0,
                "statutLibelle": "string",
                "labelLibelle": "string",
                "typeIcone": "string",
                "typeLibelle": "string",
                "communeLibelle": "string",
                "communeDepartement": "string",
                "academieLibelle": "string",
                "regionLibelle": "string",
                "domaines": "string",
                "actif": 0,
                "dateModification": "2022-06-27T08:52:27.597Z",
            },
            {
                "id": 1,
                "venueId": 0,
                "siret": 0,
                "regionId": 0,
                "academieId": "string",
                "statutId": 0,
                "labelId": 0,
                "typeId": 0,
                "communeId": "string",
                "libelle": "string",
                "adresse": "string",
                "siteWeb": 0,
                "latitude": 0,
                "longitude": 0,
                "statutLibelle": "string",
                "labelLibelle": "string",
                "typeIcone": "string",
                "typeLibelle": "string",
                "communeLibelle": "string",
                "communeDepartement": "string",
                "academieLibelle": "string",
                "regionLibelle": "string",
                "domaines": "string",
                "actif": 0,
                "dateModification": "2021-06-27T08:52:27.597Z",
            },
        ]
        return parse_obj_as(venue_serialization.AdageCulturalPartners, {"partners": data})
