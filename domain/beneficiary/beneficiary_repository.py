from abc import ABC, abstractmethod

from domain.beneficiary.beneficiary import Beneficiary
from domain.beneficiary.beneficiary_pre_subscription import BeneficiaryPreSubscription
from models import UserSQLEntity


class BeneficiaryRepository(ABC):
    @abstractmethod
    def find_beneficiary_by_user_id(self, user_id: int) -> Beneficiary:
        pass

    @classmethod
    @abstractmethod
    def save(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription) -> UserSQLEntity:
        pass

    @classmethod
    @abstractmethod
    def reject(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription, detail: str) -> None:
        pass
