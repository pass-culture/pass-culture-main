import os
import re
from datetime import datetime
from typing import Callable, Dict, List, Set

from connectors.api_demarches_simplifiees import get_application_details
from domain.demarches_simplifiees import \
    get_closed_application_ids_for_demarche_simplifiee
from domain.user_activation import create_beneficiary_from_application
from domain.user_emails import send_activation_email
from models import ApiErrors, ImportStatus, UserSQLEntity
from models.beneficiary_import import BeneficiaryImportSources
from repository import repository
from repository.beneficiary_import_queries import (
    find_applications_ids_to_retry, is_already_imported,
    save_beneficiary_import_with_status)
from repository.user_queries import find_by_civility, find_user_by_email
from utils.logger import logger
from utils.mailing import MailServiceException, send_raw_email

TOKEN = os.environ.get('DEMARCHES_SIMPLIFIEES_TOKEN', None)
VALIDATED_APPLICATION = 'closed'


def run(
        process_applications_updated_after: datetime,
        get_all_applications_ids: Callable[..., List[int]] = get_closed_application_ids_for_demarche_simplifiee,
        get_applications_ids_to_retry: Callable[..., List[int]] = find_applications_ids_to_retry,
        get_details: Callable[..., Dict] = get_application_details,
        already_imported: Callable[..., bool] = is_already_imported,
        already_existing_user: Callable[..., UserSQLEntity] = find_user_by_email
) -> None:
    procedure_id = int(os.environ.get(
        'DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID', None))
    logger.info(
        f'[BATCH][REMOTE IMPORT BENEFICIARIES] Start import from Démarches Simplifiées - Procedure {procedure_id}')
    error_messages: List[str] = []
    new_beneficiaries: List[UserSQLEntity] = []
    applications_ids = get_all_applications_ids(
        procedure_id, TOKEN, process_applications_updated_after)
    retry_ids = get_applications_ids_to_retry()

    logger.info(
        f'[BATCH][REMOTE IMPORT BENEFICIARIES] {len(applications_ids)} new applications to process - Procedure {procedure_id}')
    logger.info(
        f'[BATCH][REMOTE IMPORT BENEFICIARIES] {len(retry_ids)} previous applications to retry - Procedure {procedure_id}')

    for application_id in (retry_ids + applications_ids):
        details = get_details(application_id, procedure_id, TOKEN)
        try:
            information = parse_beneficiary_information(details)
        except Exception:
            _process_error(error_messages, application_id, procedure_id)
            continue

        if already_existing_user(information['email']):
            _process_rejection(information, procedure_id)
            continue

        if not already_imported(information['application_id']):
            process_beneficiary_application(
                information=information,
                error_messages=error_messages,
                new_beneficiaries=new_beneficiaries,
                retry_ids=retry_ids,
                procedure_id=procedure_id
            )

    logger.info(
        f'[BATCH][REMOTE IMPORT BENEFICIARIES] End import from Démarches Simplifiées - Procedure {procedure_id}')


def process_beneficiary_application(
        information: Dict,
        error_messages: List[str],
        new_beneficiaries: List[UserSQLEntity],
        retry_ids: List[int],
        procedure_id: int,
        find_duplicate_users: Callable[..., List[UserSQLEntity]] = find_by_civility
) -> None:
    duplicate_users = find_duplicate_users(
        information['first_name'],
        information['last_name'],
        information['birth_date']
    )

    if not duplicate_users or information['application_id'] in retry_ids:
        _process_creation(error_messages, information,
                          new_beneficiaries, procedure_id)
    else:
        _process_duplication(duplicate_users, error_messages,
                             information, procedure_id)


def parse_beneficiary_information(application_detail: Dict) -> Dict:
    dossier = application_detail['dossier']

    information = {
        'last_name': dossier['individual']['nom'],
        'first_name': dossier['individual']['prenom'],
        'civility': dossier['individual']['civilite'],
        'email': dossier['email'],
        'application_id': dossier['id']
    }

    for field in dossier['champs']:
        label = field['type_de_champ']['libelle']
        value = field['value']

        if 'Veuillez indiquer votre département' in label:
            information['department'] = re.search(
                '^[0-9]{2,3}|[2BbAa]{2}', value).group(0)
        if label == 'Date de naissance':
            information['birth_date'] = datetime.strptime(value, '%Y-%m-%d')
        if label == 'Numéro de téléphone':
            information['phone'] = value
        if label == 'Code postal de votre adresse de résidence':
            space_free = value.strip().replace(' ', '')
            information['postal_code'] = re.search(
                '^[0-9]{5}', space_free).group(0)
        if label == 'Veuillez indiquer votre statut':
            information['activity'] = value

    return information


def _process_creation(error_messages: List[str], information: Dict, new_beneficiaries: List[UserSQLEntity],
                      procedure_id: int) -> None:
    new_beneficiary = create_beneficiary_from_application(information)
    try:
        repository.save(new_beneficiary)
    except ApiErrors as api_errors:
        logger.warning(f"[BATCH][REMOTE IMPORT BENEFICIARIES] Could not save application "
                       f"{information['application_id']}, because of error: {str(api_errors)} - Procedure {procedure_id}")
        error_messages.append(str(api_errors))
    else:
        logger.info(f"[BATCH][REMOTE IMPORT BENEFICIARIES] Successfully created user for application "
                    f"{information['application_id']} - Procedure {procedure_id}")
        save_beneficiary_import_with_status(
            ImportStatus.CREATED,
            information['application_id'],
            source=BeneficiaryImportSources.demarches_simplifiees,
            source_id=procedure_id,
            user=new_beneficiary)
        new_beneficiaries.append(new_beneficiary)
        try:
            send_activation_email(new_beneficiary, send_raw_email)
        except MailServiceException as mail_service_exception:
            logger.error(f"Email send_activation_email failure for application {information['application_id']} - Procedure {procedure_id}",
                         mail_service_exception)


def _process_duplication(duplicate_users: List[UserSQLEntity], error_messages: List[str], information: Dict,
                         procedure_id: int) -> None:
    number_of_beneficiaries = len(duplicate_users)
    duplicate_ids = ", ".join([str(u.id) for u in duplicate_users])
    message = f"{number_of_beneficiaries} utilisateur(s) en doublon {duplicate_ids} pour le dossier {information['application_id']}"
    logger.warning(
        f'[BATCH][REMOTE IMPORT BENEFICIARIES] Duplicate beneficiaries found : {message} - Procedure {procedure_id}')
    error_messages.append(message)
    save_beneficiary_import_with_status(ImportStatus.DUPLICATE, information['application_id'], source=BeneficiaryImportSources.demarches_simplifiees, source_id=procedure_id,
                                        detail=f"Utilisateur en doublon : {duplicate_ids}")


def _process_rejection(information: Dict, procedure_id: int) -> None:
    save_beneficiary_import_with_status(ImportStatus.REJECTED, information['application_id'], source=BeneficiaryImportSources.demarches_simplifiees, source_id=procedure_id,
                                        detail='Compte existant avec cet email')
    logger.warning(
        f"[BATCH][REMOTE IMPORT BENEFICIARIES] Rejected application {information['application_id']} because of already existing email - Procedure {procedure_id}")


def _process_error(error_messages: List[str], application_id: int, procedure_id: int) -> None:
    error = f"Le dossier {application_id} contient des erreurs et a été ignoré - Procedure {procedure_id}"
    logger.error(f'[BATCH][REMOTE IMPORT BENEFICIARIES] {error}')
    error_messages.append(error)
    save_beneficiary_import_with_status(
        ImportStatus.ERROR, application_id, source=BeneficiaryImportSources.demarches_simplifiees, source_id=procedure_id, detail=error)


def _find_application_ids_to_process(applications: Dict, process_applications_updated_after: datetime) -> Set:
    processable_applications = filter(
        lambda a: a['state'] == 'closed', applications['dossiers'])
    recent_applications = filter(
        lambda a: _parse_application_date(
            a) > process_applications_updated_after,
        processable_applications)
    return {application['id'] for application in recent_applications}


def _parse_application_date(application: Dict) -> datetime:
    return datetime.strptime(application['updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
