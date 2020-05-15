
class BankInformations(object):
    def __init__(self,
                 application_id: str = None,
                 status: str = None,
                 iban: str = None,
                 bic: str = None):
        self.application_id = application_id
        self.status = status
        self.iban = iban
        self.bic = bic
