from abc import ABC, abstractmethod

from domain.bank_informations.bank_informations import BankInformations


class BankInformationsRepository(ABC):
    @abstractmethod
    def find_by_offerer(self, offerer_id: str) -> BankInformations:
        pass

    @abstractmethod
    def find_by_venue(self, venue_id: str) -> BankInformations:
        pass

    @abstractmethod
    def get_by_application(self, application_id: str) -> BankInformations:
        pass
