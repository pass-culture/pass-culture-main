from abc import ABC
from abc import abstractmethod

from pcapi.domain.beneficiary.beneficiary import Beneficiary
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription


class BeneficiaryRepository(ABC):
    @classmethod
    @abstractmethod
    def save(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription) -> Beneficiary:
        pass

    @classmethod
    @abstractmethod
    def reject(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription, detail: str) -> None:
        pass
