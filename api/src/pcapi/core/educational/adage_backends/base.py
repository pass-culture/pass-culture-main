from pcapi import settings
from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational.adage_backends.serialize import AdageCollectiveOffer
from pcapi.core.educational.models import AdageApiResult
from pcapi.routes.adage.v1.serialization import prebooking
from pcapi.routes.serialization import venues_serialize


class AdageClient:
    def __init__(self) -> None:
        self.base_url = settings.ADAGE_API_URL

    def notify_prebooking(self, data: prebooking.EducationalBookingResponse) -> AdageApiResult:
        raise NotImplementedError()

    def notify_offer_or_stock_edition(self, data: prebooking.EducationalBookingEdition) -> AdageApiResult:
        raise NotImplementedError()

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        raise NotImplementedError()

    def notify_booking_cancellation_by_offerer(self, data: prebooking.EducationalBookingResponse) -> AdageApiResult:
        raise NotImplementedError()

    def get_cultural_partners(self) -> list[dict[str, str | int | float | None]]:
        raise NotImplementedError()

    def notify_institution_association(self, data: AdageCollectiveOffer) -> AdageApiResult:
        raise NotImplementedError()

    def get_cultural_partner(self, siret: str) -> venues_serialize.AdageCulturalPartner:
        raise NotImplementedError()
