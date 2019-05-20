import os
import re
from datetime import datetime, timedelta
from typing import Callable

from connectors.api_demarches_simplifiees import get_all_applications_for_procedure, get_application_details

TOKEN = os.environ.get('DEMARCHES_SIMPLIFIEES_TOKEN', None)
PROCEDURE_ID = os.environ.get('DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID', None)
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
VALIDATED_APPLICATION = 'closed'


def run(
        get_all_applications: Callable[[str, str], dict] = get_all_applications_for_procedure,
        get_details: Callable[[str, str, str], dict] = get_application_details
):
    applications = get_all_applications(PROCEDURE_ID, TOKEN)
    processable_application = filter(lambda a: _processable_application(a), applications['dossiers'])
    ids_to_process = {a['id'] for a in processable_application}

    for id in ids_to_process:
        details = get_details(id, PROCEDURE_ID, TOKEN)
        information = parse_beneficiary_information(details)
        process_beneficiary_application(information)


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


def process_beneficiary_application(application_detail: dict):
    pass


def _processable_application(application: dict) -> bool:
    return _validated_application(application) and _updated_in_last_24_hours(application)


def _validated_application(application: dict) -> bool:
    return application['state'] == VALIDATED_APPLICATION


def _updated_in_last_24_hours(application: dict) -> bool:
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    return datetime.strptime(application['updated_at'], DATETIME_FORMAT) > twenty_four_hours_ago
