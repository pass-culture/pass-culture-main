from domain.user_emails import send_activation_email
from domain.beneficiary.beneficiary_repository import BeneficiaryRepository
from domain.beneficiary.beneficiary_pre_subscription_repository import BeneficiaryPreSubscriptionRepository
from domain.beneficiary.beneficiary_pre_subscription_validator import validate, CantRegisterBeneficiary

from utils.mailing import send_raw_email

from models import BeneficiaryImport, ImportStatus, BeneficiaryImportSources
from repository import repository
from domain.beneficiary.beneficiary_pre_subscription import \
    BeneficiaryPreSubscription


class CreateBeneficiaryFromApplication:
    def __init__(self,
                 beneficiary_jouve_repository: BeneficiaryPreSubscriptionRepository,
                 beneficiary_sql_repository: BeneficiaryRepository):
        self.beneficiary_jouve_repository = beneficiary_jouve_repository
        self.beneficiary_sql_repository = beneficiary_sql_repository

    def execute(self, application_id: int) -> None:
        beneficiary_pre_subscription = self.beneficiary_jouve_repository.get_application_by(application_id)

        try:
            validate(beneficiary_pre_subscription)
            beneficiary = self.beneficiary_sql_repository.save(beneficiary_pre_subscription)

        except CantRegisterBeneficiary as cant_register_beneficiary_exception:
            self.beneficiary_sql_repository.reject(beneficiary_pre_subscription,
                                                   detail=str(cant_register_beneficiary_exception))

        else:
            send_activation_email(user=beneficiary, send_email=send_raw_email)
