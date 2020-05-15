from datetime import datetime


class BankInformations(object):
    def __init__(self,
                 application_id: str = None,
                 status: str = None,
                 iban: str = None,
                 bic: str = None,
                 offerer_id: int = None,
                 date_modified_at_last_provider: datetime = None):
        self.application_id = application_id
        self.status = status
        self.iban = iban
        self.bic = bic
        self.offerer_id = offerer_id
        self.date_modified_at_last_provider = date_modified_at_last_provider
