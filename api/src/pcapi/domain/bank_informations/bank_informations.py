from datetime import datetime

from pcapi.core.finance.models import BankInformationStatus


class BankInformations:
    def __init__(
        self,
        application_id: int | None = None,
        status: BankInformationStatus | None = None,
        iban: str | None = None,
        bic: str | None = None,
        offerer_id: int | None = None,
        venue_id: int | None = None,
        date_modified: datetime | None = None,
    ):
        self.id = None
        self.application_id = application_id
        self.status = status
        self.iban = iban
        self.bic = bic
        self.offerer_id = offerer_id
        self.venue_id = venue_id
        self.date_modified = date_modified
