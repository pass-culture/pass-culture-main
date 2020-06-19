from domain.user_emails import send_activation_email
from infrastructure.repository.beneficiary import \
    beneficiary_pre_subscription_sql_converter
from infrastructure.repository.beneficiary.beneficiary_jouve_repository import \
    BeneficiaryJouveRepository
from models.beneficiary_import import BeneficiaryImportSources
from models.beneficiary_import_status import ImportStatus
from models.deposit import Deposit
from repository import repository
from repository.beneficiary_import_queries import \
    save_beneficiary_import_with_status
from utils.mailing import send_raw_email


def create_beneficiary_from_application(application_id: int) -> None:
    beneficiary_pre_subscription = BeneficiaryJouveRepository.get_application_by(application_id)
    beneficiary = beneficiary_pre_subscription_sql_converter.to_model(beneficiary_pre_subscription)

    deposit = create_deposit(application_id)
    beneficiary.deposits = [deposit]

    repository.save(beneficiary)

    save_beneficiary_import_with_status(
        status=ImportStatus.CREATED,
        application_id=application_id,
        user=beneficiary,
        source=BeneficiaryImportSources.jouve,
        source_id=None)

    send_activation_email(user=beneficiary, send_email=send_raw_email)


def create_deposit(application_id: int) -> Deposit:
    deposit = Deposit()
    deposit.amount = 500
    deposit.source = f'dossier jouve [{application_id}]'

    return deposit
