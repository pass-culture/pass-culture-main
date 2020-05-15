from domain.bank_informations.bank_informations import BankInformations


class Offerer(object):
    def __init__(self,
                 siren: str = None):
        self.siren = siren
