from pcapi.domain.beneficiary.beneficiary_repository import BeneficiaryRepository
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_exceptions import CantRegisterBeneficiary
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_repository import (
    BeneficiaryPreSubscriptionRepository,
)
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_validator import validate
from pcapi.domain.user_emails import send_activation_email
from pcapi.domain.user_emails import send_rejection_email_to_beneficiary_pre_subscription
from pcapi.utils.mailing import send_raw_email


class CreateBeneficiaryFromApplication:
    def __init__(self,
                 beneficiary_pre_subscription_repository: BeneficiaryPreSubscriptionRepository,
                 beneficiary_repository: BeneficiaryRepository):
        self.beneficiary_pre_subscription_repository = beneficiary_pre_subscription_repository
        self.beneficiary_repository = beneficiary_repository

    def execute(self, application_id: int) -> None:
        beneficiary_pre_subscription = self.beneficiary_pre_subscription_repository.get_application_by(
            application_id)

        try:
            validate(beneficiary_pre_subscription)

        except CantRegisterBeneficiary as cant_register_beneficiary_exception:
            self.beneficiary_repository.reject(beneficiary_pre_subscription,
                                               detail=str(cant_register_beneficiary_exception))
            send_rejection_email_to_beneficiary_pre_subscription(beneficiary_pre_subscription=beneficiary_pre_subscription,
                                                                 error=cant_register_beneficiary_exception,
                                                                 send_email=send_raw_email)

        else:
            beneficiary = self.beneficiary_repository.save(
                beneficiary_pre_subscription)
            send_activation_email(user=beneficiary, send_email=send_raw_email)
