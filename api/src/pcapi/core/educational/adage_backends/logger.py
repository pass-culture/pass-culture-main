import logging

from pydantic import parse_obj_as

from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational.adage_backends.base import AdageClient
from pcapi.core.educational.exceptions import CulturalPartnerNotFoundException
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingEdition
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse
from pcapi.routes.serialization import venues_serialize


logger = logging.getLogger(__name__)


class AdageLoggerClient(AdageClient):
    def notify_prebooking(self, data: EducationalBookingResponse) -> AdageApiResult:
        logger.info("Adage has been notified at %s, with payload: %s", f"{self.base_url}/v1/prereservation", data)
        return AdageApiResult(sent_data=data, response={"status_code": 201}, success=True)  # type: ignore [arg-type]

    def notify_offer_or_stock_edition(self, data: EducationalBookingEdition) -> AdageApiResult:
        logger.info("Adage has been notified at %s, with payload: %s", f"{self.base_url}/v1/prereservation-edit", data)
        return AdageApiResult(sent_data=data.dict(), response={"status_code": 201}, success=True)

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        logger.info("Adage has been called at %s, with siren: %s", f"{self.base_url}/v1/partenaire-culturel", siren)

        if siren in ["950469494", "881457238", "851924100", "832321053"]:
            return [AdageVenue.parse_obj({"siret": "95046949400021"})]

        raise CulturalPartnerNotFoundException("Requested siren is not a known cultural partner for Adage")

    def notify_booking_cancellation_by_offerer(self, data: EducationalBookingResponse) -> AdageApiResult:
        logger.info(
            "Adage has been notified at %s, with payload: %s", f"{self.base_url}/v1/prereservation-annule", data
        )
        return AdageApiResult(sent_data=data.dict(), response={"status_code": 201}, success=True)

    def get_cultural_partners(self) -> venues_serialize.AdageCulturalPartners:
        logger.info("Adage has been called at %s", f"{self.base_url}/v1/partenaire-culturel")
        data = [
            {
                "id": 1,
                "venueId": 12,
                "siret": 51234567900017,
                "regionId": 2,
                "academieId": "ac-versaille",
                "statutId": 2,
                "labelId": 3,
                "typeId": 1,
                "communeId": "Paris",
                "libelle": "a cultural partner",
                "adresse": "10 rue de la ville d'à coté",
                "siteWeb": 0,
                "latitude": 0,
                "longitude": 0,
                "statutLibelle": "Association",
                "labelLibelle": "pouet",
                "typeIcone": "image",
                "typeLibelle": "a type",
                "communeLibelle": "Paris",
                "communeDepartement": "Paris",
                "academieLibelle": "versaille",
                "regionLibelle": "ile de france",
                "domaines": "des domaines",
                "actif": 0,
                "dateModification": "2022-06-27T08:52:27.597Z",
            },
            {
                "id": 2,
                "venueId": 13,
                "siret": 65498732000011,
                "regionId": 3,
                "academieId": "un id d'academie",
                "statutId": 3,
                "labelId": 1,
                "typeId": 1,
                "communeId": "une comune",
                "libelle": "un libelle",
                "adresse": "1 impasse d'une ville lointaine",
                "siteWeb": 0,
                "latitude": 0,
                "longitude": 0,
                "statutLibelle": "entreprise privée",
                "labelLibelle": "sans label",
                "typeIcone": "film",
                "typeLibelle": "maison",
                "communeLibelle": "une commune libelle",
                "communeDepartement": "corse du sud",
                "academieLibelle": "Lille",
                "regionLibelle": "Corse",
                "domaines": "d'autres domaines",
                "actif": 0,
                "dateModification": "2022-06-27T08:52:27.597Z",
            },
        ]
        return parse_obj_as(venues_serialize.AdageCulturalPartners, {"partners": data})
