from pcapi import settings
from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.core.educational.adage_backends import serialize
from pcapi.routes.adage.v1.serialization import prebooking
from pcapi.routes.serialization import venues_serialize


class AdageClient:
    def __init__(self) -> None:
        self.base_url = settings.ADAGE_API_URL

    def notify_prebooking(self, data: prebooking.EducationalBookingResponse) -> None:
        raise NotImplementedError()

    def notify_offer_or_stock_edition(self, data: prebooking.EducationalBookingEdition) -> None:
        raise NotImplementedError()

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        raise NotImplementedError()

    def notify_booking_cancellation_by_offerer(self, data: prebooking.EducationalBookingResponse) -> None:
        raise NotImplementedError()

    def get_cultural_partners(self) -> list[dict[str, str | int | float | None]]:
        raise NotImplementedError()

    def notify_institution_association(self, data: serialize.AdageCollectiveOffer) -> None:
        raise NotImplementedError()

    def get_cultural_partner(self, siret: str) -> venues_serialize.AdageCulturalPartner:
        raise NotImplementedError()

    def get_adage_educational_institutions(self, ansco: str) -> list[serialize.AdageEducationalInstitution]:
        raise NotImplementedError()

    def get_adage_educational_redactor_from_uai(self, uai: str) -> list[dict[str, str]]:
        raise NotImplementedError()

    def notify_reimburse_collective_booking(self, data: prebooking.AdageReibursementNotification) -> None:
        raise NotImplementedError()

    def notify_redactor_when_collective_request_is_made(self, data: serialize.AdageCollectiveRequest) -> None:
        raise NotImplementedError()
