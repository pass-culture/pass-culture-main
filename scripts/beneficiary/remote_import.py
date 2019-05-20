import os
import re
from datetime import datetime
from typing import Callable, List

from connectors.api_demarches_simplifiees import get_all_applications_for_procedure, get_application_details
from domain.password import generate_reset_token, random_password
from domain.user_emails import send_activation_notification_email
from models import User, PcObject, Deposit
from repository.user_queries import find_by_first_and_last_names_and_birth_date
from scripts.beneficiary import THIRTY_DAYS_IN_HOURS
from utils.mailing import send_raw_email

TOKEN = os.environ.get('DEMARCHES_SIMPLIFIEES_TOKEN', None)
PROCEDURE_ID = os.environ.get('DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID', None)
VALIDATED_APPLICATION = 'closed'


def run(
        get_all_applications: Callable[[str, str], dict] = get_all_applications_for_procedure,
        get_details: Callable[[str, str, str], dict] = get_application_details,
        find_duplicate_users: Callable[[str, str, str], User] = find_by_first_and_last_names_and_birth_date
):
    applications = get_all_applications(PROCEDURE_ID, TOKEN)
    processable_application = filter(lambda a: a['state'] == 'closed', applications['dossiers'])
    ids_to_process = {a['id'] for a in processable_application}
    error_messages = []

    for id in ids_to_process:
        details = get_details(id, PROCEDURE_ID, TOKEN)
        information = parse_beneficiary_information(details)
        process_beneficiary_application(information, error_messages, find_duplicate_users=find_duplicate_users)


class DuplicateBeneficiaryError(Exception):
    def __init__(self, application_id: int, duplicate_beneficiaries: List[User]):
        number_of_beneficiaries = len(duplicate_beneficiaries)
        duplicate_ids = ", ".join([str(u.id) for u in duplicate_beneficiaries])
        self.message = '%s utilisateur(s) en doublons (%s) pour le dossier %s' % (
            number_of_beneficiaries, duplicate_ids, application_id
        )


def process_beneficiary_application(
        information: dict, error_messages: List[str],
        find_duplicate_users: Callable[[str, str, str], User] = find_by_first_and_last_names_and_birth_date
):
    try:
        new_beneficiary = create_beneficiary_from_application(information, find_duplicate_users=find_duplicate_users)
    except DuplicateBeneficiaryError as e:
        error_messages.append(e.message)
    else:
        PcObject.check_and_save(new_beneficiary)
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
            information['department'] = re.search('^[0-9]{2}', value).group(0)
        if label == 'Date de naissance':
            information['birth_date'] = datetime.strptime(value, '%Y-%m-%d')
        if label == 'Numéro de téléphone':
            information['phone'] = value
        if label == 'Code postal':
            information['postal_code'] = value

    return information


def create_beneficiary_from_application(
        application_detail: dict,
        find_duplicate_users: Callable[[str, str, str], User] = find_by_first_and_last_names_and_birth_date
) -> User:
    duplicate_users = find_duplicate_users(
        application_detail['first_name'],
        application_detail['last_name'],
        application_detail['birth_date']
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
    deposit.source = 'activation'
    beneficiary.deposits = [deposit]

    return beneficiary
