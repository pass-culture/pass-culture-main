from abc import ABC, abstractmethod

from domain.beneficiary.beneficiary_pre_subscription import BeneficiaryPreSubscription


class BeneficiaryPreSubscriptionRepository(ABC):
    @abstractmethod
    def get_application_by(cls, application_id: int) -> BeneficiaryPreSubscription:
        pass
