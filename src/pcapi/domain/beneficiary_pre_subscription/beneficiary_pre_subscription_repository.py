from abc import ABC, abstractmethod

from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription


class BeneficiaryPreSubscriptionRepository(ABC):
    @abstractmethod
    def get_application_by(self, application_id: int) -> BeneficiaryPreSubscription:
        pass
