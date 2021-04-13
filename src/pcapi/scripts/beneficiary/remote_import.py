from datetime import datetime
import logging
import re
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional

from pcapi import settings
from pcapi.connectors.api_demarches_simplifiees import get_application_details
from pcapi.core.users.api import create_reset_password_token
from pcapi.core.users.constants import RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED
from pcapi.core.users.models import User
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_validator import get_beneficiary_duplicates
from pcapi.domain.demarches_simplifiees import get_closed_application_ids_for_demarche_simplifiee
from pcapi.domain.user_activation import create_beneficiary_from_application
from pcapi.domain.user_emails import send_accepted_as_beneficiary_email
from pcapi.domain.user_emails import send_activation_email
from pcapi.models import ApiErrors
from pcapi.models import ImportStatus
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.repository import repository
from pcapi.repository.beneficiary_import_queries import find_applications_ids_to_retry
from pcapi.repository.beneficiary_import_queries import is_already_imported
from pcapi.repository.beneficiary_import_queries import save_beneficiary_import_with_status
from pcapi.repository.user_queries import find_user_by_email
from pcapi.workers.push_notification_job import update_user_attributes_job


logger = logging.getLogger(__name__)
from pcapi.utils.mailing import MailServiceException


def run(
    process_applications_updated_after: datetime,
    get_all_applications_ids: Callable[..., List[int]] = get_closed_application_ids_for_demarche_simplifiee,
    get_applications_ids_to_retry: Callable[..., List[int]] = find_applications_ids_to_retry,
    get_details: Callable[..., Dict] = get_application_details,
    already_imported: Callable[..., bool] = is_already_imported,
    already_existing_user: Callable[..., User] = find_user_by_email,
) -> None:
    procedure_id = settings.DMS_NEW_ENROLLMENT_PROCEDURE_ID
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Start import from Démarches Simplifiées for "
        "procedure = %s - Procedure %s",
        procedure_id,
        procedure_id,
    )
    error_messages: List[str] = []
    new_beneficiaries: List[User] = []
    applications_ids = get_all_applications_ids(procedure_id, settings.DMS_TOKEN, process_applications_updated_after)
    retry_ids = get_applications_ids_to_retry()

    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] %i new applications to process - Procedure %s",
        len(applications_ids),
        procedure_id,
    )
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] %i previous applications to retry - Procedure %s",
        len(retry_ids),
        procedure_id,
    )

    for application_id in retry_ids + applications_ids:
        details = get_details(application_id, procedure_id, settings.DMS_TOKEN)
        try:
            information = parse_beneficiary_information(details)
        except Exception as exc:  # pylint: disable=broad-except
            logger.info(
                "[BATCH][REMOTE IMPORT BENEFICIARIES] Application %s in procedure %s had errors and was ignored: %s",
                application_id,
                procedure_id,
                exc,
                exc_info=True,
            )
            error = f"Le dossier {application_id} contient des erreurs et a été ignoré - Procedure {procedure_id}"
            error_messages.append(error)
            save_beneficiary_import_with_status(
                ImportStatus.ERROR,
                application_id,
                source=BeneficiaryImportSources.demarches_simplifiees,
                source_id=procedure_id,
                detail=error,
            )
            continue

        user = already_existing_user(information["email"])
        if user and user.isBeneficiary is True:
            _process_rejection(information, procedure_id=procedure_id)
            continue

        if not already_imported(information["application_id"]):
            process_beneficiary_application(
                information=information,
                error_messages=error_messages,
                new_beneficiaries=new_beneficiaries,
                retry_ids=retry_ids,
                procedure_id=procedure_id,
                user=user,
            )

    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] End import from Démarches Simplifiées - Procedure %s", procedure_id
    )


def process_beneficiary_application(
    information: Dict,
    error_messages: List[str],
    new_beneficiaries: List[User],
    retry_ids: List[int],
    procedure_id: int,
    user: Optional[User] = None,
) -> None:
    duplicate_users = get_beneficiary_duplicates(
        first_name=information["first_name"],
        last_name=information["last_name"],
        date_of_birth=information["birth_date"],
    )

    if not duplicate_users or information["application_id"] in retry_ids:
        _process_creation(error_messages, information, new_beneficiaries, procedure_id, user=user)
    else:
        _process_duplication(duplicate_users, error_messages, information, procedure_id)


def parse_beneficiary_information(application_detail: Dict) -> Dict:
    dossier = application_detail["dossier"]

    information = {
        "last_name": dossier["individual"]["nom"],
        "first_name": dossier["individual"]["prenom"],
        "civility": dossier["individual"]["civilite"],
        "email": dossier["email"],
        "application_id": dossier["id"],
    }

    for field in dossier["champs"]:
        label = field["type_de_champ"]["libelle"]
        value = field["value"]

        if "Veuillez indiquer votre département" in label:
            information["department"] = re.search("^[0-9]{2,3}|[2BbAa]{2}", value).group(0)
        if label == "Quelle est votre date de naissance":
            information["birth_date"] = datetime.strptime(value, "%Y-%m-%d")
        if label == "Quel est votre numéro de téléphone":
            information["phone"] = value
        if label == "Quel est le code postal de votre commune de résidence ?":
            space_free = str(value).strip().replace(" ", "")
            information["postal_code"] = re.search("^[0-9]{5}", space_free).group(0)
        if label == "Veuillez indiquer votre statut":
            information["activity"] = value

    return information


def _process_creation(
    error_messages: List[str],
    information: Dict,
    new_beneficiaries: List[User],
    procedure_id: int,
    user: Optional[User] = None,
) -> None:
    new_beneficiary = create_beneficiary_from_application(information, user=user)
    try:
        repository.save(new_beneficiary)
    except ApiErrors as api_errors:
        logger.warning(
            "[BATCH][REMOTE IMPORT BENEFICIARIES] Could not save application %s, because of error: %s - Procedure %s",
            information["application_id"],
            api_errors,
            procedure_id,
        )
        error_messages.append(str(api_errors))
    else:
        logger.info(
            "[BATCH][REMOTE IMPORT BENEFICIARIES] Successfully created user for application %s - Procedure %s",
            information["application_id"],
            procedure_id,
        )
        save_beneficiary_import_with_status(
            ImportStatus.CREATED,
            information["application_id"],
            source=BeneficiaryImportSources.demarches_simplifiees,
            source_id=procedure_id,
            user=new_beneficiary,
        )
        new_beneficiaries.append(new_beneficiary)
        update_user_attributes_job.delay(new_beneficiary.id)
        try:
            if user is None:
                token = create_reset_password_token(
                    new_beneficiary, token_life_time=RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED
                )
                send_activation_email(new_beneficiary, token=token)
            else:
                send_accepted_as_beneficiary_email(new_beneficiary)
        except MailServiceException as mail_service_exception:
            logger.exception(
                "Email send_activation_email failure for application %s - Procedure %s : %s",
                information["application_id"],
                procedure_id,
                mail_service_exception,
            )


def _process_duplication(
    duplicate_users: List[User], error_messages: List[str], information: Dict, procedure_id: int
) -> None:
    number_of_beneficiaries = len(duplicate_users)
    duplicate_ids = ", ".join([str(u.id) for u in duplicate_users])
    message = f"{number_of_beneficiaries} utilisateur(s) en doublon {duplicate_ids} pour le dossier {information['application_id']} - Procedure {procedure_id}"
    logger.warning("[BATCH][REMOTE IMPORT BENEFICIARIES] Duplicate beneficiaries found : %s", message)
    error_messages.append(message)
    save_beneficiary_import_with_status(
        ImportStatus.DUPLICATE,
        information["application_id"],
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        detail=f"Utilisateur en doublon : {duplicate_ids}",
    )


def _process_rejection(information: Dict, procedure_id: int) -> None:
    save_beneficiary_import_with_status(
        ImportStatus.REJECTED,
        information["application_id"],
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        detail="Compte existant avec cet email",
    )
    logger.warning(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Rejected application %s because of already existing email - Procedure %s",
        information["application_id"],
        procedure_id,
    )
