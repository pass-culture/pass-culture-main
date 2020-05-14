from abc import ABC, abstractmethod

from domain.beneficiary.beneficiary import Beneficiary


class BeneficiaryRepository(ABC):
    @abstractmethod
    def find_beneficiary_by_user_id(self, user_id: int) -> Beneficiary:
        pass
