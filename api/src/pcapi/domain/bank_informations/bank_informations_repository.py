from abc import ABC
from abc import abstractmethod

from pcapi.domain.bank_informations.bank_informations import BankInformations


class BankInformationsRepository(ABC):
    @abstractmethod
    def find_by_offerer(self, offerer_id: int) -> BankInformations | None:
        pass

    @abstractmethod
    def find_by_venue(self, venue_id: int) -> BankInformations | None:
        pass

    @abstractmethod
    def get_by_application(self, application_id: int) -> BankInformations | None:
        pass

    @abstractmethod
    def save(self, bank_informations: BankInformations) -> BankInformations | None:
        pass

    @abstractmethod
    def update_by_application_id(self, bank_informations: BankInformations) -> BankInformations | None:
        pass

    @abstractmethod
    def update_by_offerer_id(self, bank_informations: BankInformations) -> BankInformations | None:
        pass

    @abstractmethod
    def update_by_venue_id(self, bank_informations: BankInformations) -> BankInformations | None:
        pass
