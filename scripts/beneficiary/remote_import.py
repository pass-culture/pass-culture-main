import os
import re
from datetime import datetime
from typing import Callable

from connectors.api_demarches_simplifiees import get_all_applications_for_procedure, get_application_details
from models import User
from repository.user_queries import find_by_first_and_last_names_and_email

TOKEN = os.environ.get('DEMARCHES_SIMPLIFIEES_TOKEN', None)
PROCEDURE_ID = os.environ.get('DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID', None)
VALIDATED_APPLICATION = 'closed'


def run(
        get_all_applications: Callable[[str, str], dict] = get_all_applications_for_procedure,
        get_details: Callable[[str, str, str], dict] = get_application_details,
        find_duplicate_users: Callable[[str, str], User] = find_by_first_and_last_names_and_email
):
    applications = get_all_applications(PROCEDURE_ID, TOKEN)
    processable_application = filter(lambda a: _validated_application(a), applications['dossiers'])
    ids_to_process = {a['id'] for a in processable_application}

    for id in ids_to_process:
        details = get_details(id, PROCEDURE_ID, TOKEN)
        information = parse_beneficiary_information(details)
        process_beneficiary_application(information, find_duplicate_users=find_duplicate_users)


def parse_beneficiary_information(application_detail: dict) -> dict:
    dossier = application_detail['dossier']

    information = {
        'last_name': dossier['individual']['nom'],
        'first_name': dossier['individual']['prenom'],
        'email': dossier['email']
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


def process_beneficiary_application(
        application_detail: dict,
        find_duplicate_users: Callable[[str, str], User] = find_by_first_and_last_names_and_email
):
    pass


def _validated_application(application: dict) -> bool:
    return application['state'] == VALIDATED_APPLICATION
