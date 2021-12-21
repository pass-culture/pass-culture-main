from datetime import datetime


class BankInformations:
    def __init__(
        self,
        application_id: str = None,
        status: str = None,
        iban: str = None,
        bic: str = None,
        offerer_id: int = None,
        venue_id: int = None,
        date_modified: datetime = None,
    ):
        self.id = None
        self.application_id = application_id
        self.status = status
        self.iban = iban
        self.bic = bic
        self.offerer_id = offerer_id
        self.venue_id = venue_id
        self.date_modified = date_modified
