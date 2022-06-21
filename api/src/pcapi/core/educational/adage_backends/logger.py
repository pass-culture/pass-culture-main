import logging

from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational.adage_backends.base import AdageClient
from pcapi.core.educational.exceptions import CulturalPartnerNotFoundException
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingEdition
from pcapi.routes.adage.v1.serialization.prebooking import EducationalBookingResponse


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
