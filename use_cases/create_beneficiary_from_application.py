from domain.user_emails import send_activation_email
from domain.beneficiary.beneficiary_repository import BeneficiaryRepository
from domain.beneficiary.beneficiary_pre_subscription_repository import BeneficiaryPreSubscriptionRepository

from utils.mailing import send_raw_email

class CreateBeneficiaryFromApplication:
    def __init__(self,
                 beneficiary_jouve_repository: BeneficiaryPreSubscriptionRepository,
                 beneficiary_sql_repository: BeneficiaryRepository):
        self.beneficiary_jouve_repository = beneficiary_jouve_repository
        self.beneficiary_sql_repository = beneficiary_sql_repository

    def execute(self, application_id: int) -> None:
        beneficiary_pre_subscription = self.beneficiary_jouve_repository.get_application_by(application_id)
        beneficiary = self.beneficiary_sql_repository.save(beneficiary_pre_subscription)

        send_activation_email(user=beneficiary, send_email=send_raw_email)
