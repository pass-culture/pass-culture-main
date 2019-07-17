import os
import re
from datetime import datetime
from typing import Callable, List

from connectors.api_demarches_simplifiees import get_application_details
from domain.admin_emails import send_remote_beneficiaries_import_report_email
from domain.demarches_simplifiees import get_all_application_ids_for_procedure
from domain.password import generate_reset_token, random_password
from domain.user_emails import send_activation_notification_email
from models import User, PcObject, Deposit, ApiErrors
from models.beneficiary_import import BeneficiaryImport, ImportStatus
from repository.user_queries import find_by_first_and_last_names_and_birth_date_or_email, \
    has_already_been_created
from scripts.beneficiary import THIRTY_DAYS_IN_HOURS
from utils.logger import logger
from utils.mailing import send_raw_email, DEV_EMAIL_ADDRESS

TOKEN = os.environ.get('DEMARCHES_SIMPLIFIEES_TOKEN', None)
PROCEDURE_ID = os.environ.get('DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID', None)
VALIDATED_APPLICATION = 'closed'


def run(
        process_applications_updated_after: datetime,
        get_all_applications_ids: Callable[..., dict] = get_all_application_ids_for_procedure,
        get_details: Callable[..., dict] = get_application_details,
        existing_user: Callable[[str], User] = has_already_been_created
):
    error_messages = []
    new_beneficiaries = []
    REPORT_RECIPIENTS = os.environ.get('DEMARCHES_SIMPLIFIEES_ENROLLMENT_REPORT_RECIPIENTS', DEV_EMAIL_ADDRESS)

    logger.info('[BATCH][REMOTE IMPORT BENEFICIARIES] Start import from Démarches Simplifiées')
    applications_ids = get_all_applications_ids(PROCEDURE_ID, TOKEN, process_applications_updated_after)
    logger.info(f'[BATCH][REMOTE IMPORT BENEFICIARIES] {len(applications_ids)} applications to process')

    for id in applications_ids:
        details = get_details(id, PROCEDURE_ID, TOKEN)
        try:
            information = parse_beneficiary_information(details)
        except Exception:
            error = f"Le dossier {id} contient des erreurs et a été ignoré"
            logger.error(f'[BATCH][REMOTE IMPORT BENEFICIARIES] {error}')
            error_messages.append(error)
            continue

        if not existing_user(information['application_id']):
            process_beneficiary_application(information, error_messages, new_beneficiaries)

    send_remote_beneficiaries_import_report_email(new_beneficiaries, error_messages, REPORT_RECIPIENTS, send_raw_email)
    logger.info('[BATCH][REMOTE IMPORT BENEFICIARIES] End import from Démarches Simplifiées')


class DuplicateBeneficiaryError(Exception):
    def __init__(self, application_id: int, duplicate_beneficiaries: List[User]):
        number_of_beneficiaries = len(duplicate_beneficiaries)
        self.duplicate_ids = ", ".join([str(u.id) for u in duplicate_beneficiaries])
        self.message = '%s utilisateur(s) en doublons (%s) pour le dossier %s' % (
            number_of_beneficiaries, self.duplicate_ids, application_id
        )


def process_beneficiary_application(
        information: dict, error_messages: List[str], new_beneficiaries,
        find_duplicate_users: Callable[[str, str, str], User] = find_by_first_and_last_names_and_birth_date_or_email
):
    try:
        new_beneficiary = create_beneficiary_from_application(information, find_duplicate_users=find_duplicate_users)
    except DuplicateBeneficiaryError as e:
        logger.warning(f'[BATCH][REMOTE IMPORT BENEFICIARIES] Duplicate beneficiaries found : {e.message}')
        error_messages.append(e.message)
        beneficiary_import = BeneficiaryImport()
        beneficiary_import.status = ImportStatus.DUPLICATE
        beneficiary_import.detail = f"Utilisateur en doublon : {e.duplicate_ids}"
        beneficiary_import.demarcheSimplifieeApplicationId = information['application_id']
        PcObject.save(beneficiary_import)

    else:
        try:
            beneficiary_import = BeneficiaryImport()
            beneficiary_import.beneficiary = new_beneficiary
            beneficiary_import.status = ImportStatus.CREATED
            beneficiary_import.demarcheSimplifieeApplicationId = information['application_id']
            PcObject.save(beneficiary_import)
        except ApiErrors as e:
            logger.warning(f"[BATCH][REMOTE IMPORT BENEFICIARIES] Could not save application "
                           f"{information['application_id']}, because of error : {str(e)}")
            error_messages.append(str(e))
        else:
            new_beneficiaries.append(new_beneficiary)
            send_activation_notification_email(new_beneficiary, send_raw_email)


def parse_beneficiary_information(application_detail: dict) -> dict:
    dossier = application_detail['dossier']

    information = {
        'last_name': dossier['individual']['nom'],
        'first_name': dossier['individual']['prenom'],
        'email': dossier['email'],
        'application_id': dossier['id']
    }

    for field in dossier['champs']:
        label = field['type_de_champ']['libelle']
        value = field['value']

        if label == 'Veuillez indiquer votre département':
            information['department'] = re.search('^[0-9]{2,3}|[2BbAa]{2}', value).group(0)
        if label == 'Date de naissance':
            information['birth_date'] = datetime.strptime(value, '%Y-%m-%d')
        if label == 'Numéro de téléphone':
            information['phone'] = value
        if label == 'Code postal de votre adresse de résidence':
            space_free = value.strip().replace(' ', '')
            information['postal_code'] = re.search('^[0-9]{5}', space_free).group(0)

    return information


def create_beneficiary_from_application(
        application_detail: dict,
        find_duplicate_users: Callable[
            [str, str, str, str], User] = find_by_first_and_last_names_and_birth_date_or_email
) -> User:
    duplicate_users = find_duplicate_users(
        application_detail['first_name'],
        application_detail['last_name'],
        application_detail['birth_date'],
        application_detail['email']
    )

    if duplicate_users:
        raise DuplicateBeneficiaryError(application_detail['application_id'], duplicate_users)

    beneficiary = User()
    beneficiary.lastName = application_detail['last_name']
    beneficiary.firstName = application_detail['first_name']
    beneficiary.publicName = '%s %s' % (application_detail['first_name'], application_detail['last_name'])
    beneficiary.email = application_detail['email']
    beneficiary.phoneNumber = application_detail['phone']
    beneficiary.departementCode = application_detail['department']
    beneficiary.postalCode = application_detail['postal_code']
    beneficiary.dateOfBirth = application_detail['birth_date']
    beneficiary.canBookFreeOffers = True
    beneficiary.isAdmin = False
    beneficiary.password = random_password()
    generate_reset_token(beneficiary, validity_duration_hours=THIRTY_DAYS_IN_HOURS)

    deposit = Deposit()
    deposit.amount = 500
    deposit.source = 'démarches simplifiées dossier [%s]' % application_detail['application_id']
    beneficiary.deposits = [deposit]

    return beneficiary


def _find_application_ids_to_process(applications: dict, process_applications_updated_after: datetime):
    processable_applications = filter(lambda a: a['state'] == 'closed', applications['dossiers'])
    recent_applications = filter(
        lambda a: _parse_application_date(a) > process_applications_updated_after,
        processable_applications)
    return {a['id'] for a in recent_applications}


def _parse_application_date(application: dict) -> datetime:
    return datetime.strptime(application['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
