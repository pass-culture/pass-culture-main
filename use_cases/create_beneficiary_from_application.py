from domain.user_emails import send_activation_email
from domain.beneficiary.beneficiary_repository import BeneficiaryRepository
from domain.beneficiary.beneficiary_pre_subscription_repository import BeneficiaryPreSubscriptionRepository
from domain.beneficiary.beneficiary_pre_subscription_validator import check_email_is_not_taken, check_not_a_dupplicate, CantRegisterBeneficiary

from utils.mailing import send_raw_email

from models import BeneficiaryImport, ImportStatus, BeneficiaryImportSources
from repository import repository
from domain.beneficiary.beneficiary_pre_subscription import \
    BeneficiaryPreSubscription


def create_rejected_beneficiary_import(beneficiary_pre_subscription: BeneficiaryPreSubscription, detail: str) -> BeneficiaryImport:
    beneficiary_import = BeneficiaryImport()

    beneficiary_import.applicationId = beneficiary_pre_subscription.application_id
    beneficiary_import.sourceId = None
    beneficiary_import.source = beneficiary_pre_subscription.source
    beneficiary_import.setStatus(status=ImportStatus.REJECTED, detail=detail)

    repository.save(beneficiary_import)


class CreateBeneficiaryFromApplication:
    def __init__(self,
                 beneficiary_jouve_repository: BeneficiaryPreSubscriptionRepository,
                 beneficiary_sql_repository: BeneficiaryRepository):
        self.beneficiary_jouve_repository = beneficiary_jouve_repository
        self.beneficiary_sql_repository = beneficiary_sql_repository

    def execute(self, application_id: int) -> None:
        beneficiary_pre_subscription = self.beneficiary_jouve_repository.get_application_by(application_id)

        try:
            check_email_is_not_taken(beneficiary_pre_subscription)
            check_not_a_dupplicate(beneficiary_pre_subscription)

            beneficiary = self.beneficiary_sql_repository.save(beneficiary_pre_subscription)

        except CantRegisterBeneficiary as error:
            create_rejected_beneficiary_import(beneficiary_pre_subscription, detail=str(error))

        else:
            send_activation_email(user=beneficiary, send_email=send_raw_email)
