import datetime

from pcapi import settings
from pcapi.connectors.serialization.api_adage_serializers import AdageVenue
from pcapi.serialization.educational.adage import shared as adage_serialize


class AdageClient:
    def __init__(self) -> None:
        self.base_url = settings.ADAGE_API_URL

    def notify_prebooking(self, data: adage_serialize.EducationalBookingResponse) -> None:
        raise NotImplementedError()

    def notify_offer_or_stock_edition(self, data: adage_serialize.EducationalBookingEdition) -> None:
        raise NotImplementedError()

    def get_adage_offerer(self, siren: str) -> list[AdageVenue]:
        raise NotImplementedError()

    def notify_booking_cancellation_by_offerer(self, data: adage_serialize.EducationalBookingResponse) -> None:
        raise NotImplementedError()

    def get_cultural_partners(
        self, since_date: datetime.datetime | None = None
    ) -> list[dict[str, str | int | float | None]]:
        raise NotImplementedError()

    def notify_institution_association(self, data: adage_serialize.AdageCollectiveOffer) -> None:
        raise NotImplementedError()

    def get_cultural_partner(self, siret: str) -> adage_serialize.AdageCulturalPartner:
        raise NotImplementedError()

    def get_adage_educational_institutions(self, ansco: str) -> list[adage_serialize.AdageEducationalInstitution]:
        raise NotImplementedError()

    def get_adage_educational_redactor_from_uai(self, uai: str) -> list[dict[str, str]]:
        raise NotImplementedError()

    def notify_reimburse_collective_booking(self, data: adage_serialize.AdageReimbursementNotification) -> None:
        raise NotImplementedError()

    def notify_redactor_when_collective_request_is_made(self, data: adage_serialize.AdageCollectiveRequest) -> None:
        raise NotImplementedError()
