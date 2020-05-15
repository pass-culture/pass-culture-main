from domain.bank_informations.bank_informations import BankInformations


class Offerer(object):
    def __init__(self,
                 id: str = None,
                 siren: str = None):
        self.id = id
        self.siren = siren
