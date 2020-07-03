from abc import ABC, abstractmethod

from domain.beneficiary.beneficiary import Beneficiary
from domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription


class BeneficiaryRepository(ABC):
    @abstractmethod
    def find_beneficiary_by_user_id(self, user_id: int) -> Beneficiary:
        pass

    @classmethod
    @abstractmethod
    def save(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription) -> Beneficiary:
        pass

    @classmethod
    @abstractmethod
    def reject(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription, detail: str) -> None:
        pass
