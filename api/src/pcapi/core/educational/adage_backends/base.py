import datetime

from pcapi import settings
from pcapi.core.educational import schemas
from pcapi.core.educational.adage_backends import serialize


class AdageClient:
    def __init__(self) -> None:
        self.base_url = settings.ADAGE_API_URL

    def notify_prebooking(self, data: schemas.EducationalBookingResponse) -> None:
        raise NotImplementedError()

    def notify_offer_or_stock_edition(self, data: schemas.EducationalBookingEdition) -> None:
        raise NotImplementedError()

    def get_adage_offerer(self, siren: str) -> list[schemas.AdageCulturalPartner]:
        raise NotImplementedError()

    def notify_booking_cancellation_by_offerer(self, data: schemas.EducationalBookingResponse) -> None:
        raise NotImplementedError()

    def get_cultural_partners(
        self, since_date: datetime.datetime | None = None
    ) -> list[dict[str, str | int | float | None]]:
        raise NotImplementedError()

    def notify_institution_association(self, data: serialize.AdageCollectiveOffer) -> None:
        raise NotImplementedError()

    def get_cultural_partner(self, siret: str) -> schemas.AdageCulturalPartner:
        raise NotImplementedError()

    def get_adage_educational_institutions(self, ansco: str) -> list[serialize.AdageEducationalInstitution]:
        raise NotImplementedError()

    def get_adage_educational_redactor_from_uai(self, uai: str) -> list[dict[str, str]]:
        raise NotImplementedError()

    def notify_reimburse_collective_booking(self, data: schemas.AdageReimbursementNotification) -> None:
        raise NotImplementedError()

    def notify_redactor_when_collective_request_is_made(self, data: serialize.AdageCollectiveRequest) -> None:
        raise NotImplementedError()
