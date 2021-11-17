from datetime import datetime
import logging
import re
from typing import Optional

from dateutil import parser as date_parser

from pcapi import settings
from pcapi.connectors.api_demarches_simplifiees import DMSGraphQLClient
from pcapi.connectors.api_demarches_simplifiees import GraphQLApplicationStates
from pcapi.connectors.api_demarches_simplifiees import get_application_details
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.models as fraud_models
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.messages as subscription_messages
import pcapi.core.users.api as users_api
import pcapi.core.users.external as users_external
import pcapi.core.users.models as users_models
from pcapi.domain import user_emails
from pcapi.domain.demarches_simplifiees import get_closed_application_ids_for_demarche_simplifiee
from pcapi.domain.user_activation import create_beneficiary_from_application
from pcapi.models import ApiErrors
from pcapi.models import ImportStatus
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.repository import repository
from pcapi.repository.beneficiary_import_queries import find_applications_ids_to_retry
from pcapi.repository.beneficiary_import_queries import get_already_processed_applications_ids
from pcapi.repository.beneficiary_import_queries import is_already_imported
from pcapi.repository.beneficiary_import_queries import save_beneficiary_import_with_status
from pcapi.repository.user_queries import beneficiary_by_civility_query
from pcapi.repository.user_queries import find_user_by_email
from pcapi.utils.date import FrenchParserInfo


logger = logging.getLogger(__name__)


class DMSParsingError(ValueError):
    def __init__(self, user_email: str, errors: dict[str, str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = errors
        self.user_email = user_email


def run(procedure_id: int, use_graphql_api: bool = False) -> None:
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Start import from Démarches Simplifiées for "
        "procedure = %s - Procedure %s",
        procedure_id,
        procedure_id,
    )
    retry_ids = find_applications_ids_to_retry()
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] %i previous applications to retry - Procedure %s",
        len(retry_ids),
        procedure_id,
    )

    existing_applications_ids = get_already_processed_applications_ids(procedure_id)
    if use_graphql_api:
        client = DMSGraphQLClient()
        for application_details in client.get_applications_with_details(
            procedure_id, GraphQLApplicationStates.accepted
        ):
            application_id = application_details["number"]
            if application_id in existing_applications_ids:
                continue
            process_application(
                procedure_id,
                application_id,
                application_details,
                retry_ids,
                parsing_function=parse_beneficiary_information_graphql,
            )

    else:
        applications_ids = get_closed_application_ids_for_demarche_simplifiee(procedure_id, settings.DMS_TOKEN)
        logger.info(
            "[BATCH][REMOTE IMPORT BENEFICIARIES] %i new applications to process - Procedure %s",
            len(applications_ids),
            procedure_id,
        )

        for application_id in retry_ids + applications_ids:
            application_details = get_application_details(application_id, procedure_id, settings.DMS_TOKEN)

            process_application(
                procedure_id,
                application_id,
                application_details,
                retry_ids,
                parsing_function=parse_beneficiary_information,
            )

    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] End import from Démarches Simplifiées - Procedure %s", procedure_id
    )


def process_parsing_exception(exception: Exception, procedure_id: int, application_id: int) -> None:
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Application %s in procedure %s had errors and was ignored: %s",
        application_id,
        procedure_id,
        exception,
        exc_info=True,
    )
    error = f"Le dossier {application_id} contient des erreurs et a été ignoré - Procedure {procedure_id}"
    save_beneficiary_import_with_status(
        ImportStatus.ERROR,
        application_id,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        detail=error,
    )


def process_parsing_error(exception: DMSParsingError, procedure_id: int, application_id: int) -> None:
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Invalid values (%r) detected in Application %s in procedure %s",
        exception.errors,
        application_id,
        procedure_id,
    )
    user = find_user_by_email(exception.user_email)
    user_emails.send_dms_wrong_values_emails(
        exception.user_email, exception.errors.get("postal_code"), exception.errors.get("id_piece_number")
    )
    if user:
        subscription_messages.on_dms_application_parsing_errors(user, list(exception.errors.keys()))
    errors = ",".join([f"'{key}' ({value})" for key, value in sorted(exception.errors.items())])
    error_detail = f"Erreur dans les données soumises dans le dossier DMS : {errors}"
    # keep a compatibility with BeneficiaryImport table
    save_beneficiary_import_with_status(
        ImportStatus.ERROR,
        application_id,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        detail=error_detail,
        user=user,
    )


def process_application(
    procedure_id: int, application_id: int, application_details: dict, retry_ids: list[int], parsing_function
) -> None:

    try:
        information = parsing_function(application_details, procedure_id)
    except DMSParsingError as exc:
        process_parsing_error(exc, procedure_id, application_id)
        return

    except Exception as exc:  # pylint: disable=broad-except
        process_parsing_exception(exc, procedure_id, application_id)
        return

    user = find_user_by_email(information.email)
    if not user:
        save_beneficiary_import_with_status(
            ImportStatus.ERROR,
            application_id,
            source=BeneficiaryImportSources.demarches_simplifiees,
            source_id=procedure_id,
            detail=f"Aucun utilisateur trouvé pour l'email {information.email}",
        )
        return
    try:
        fraud_api.on_dms_fraud_check(user, information)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error on dms fraud check result: %s", exc)
    if user.has_beneficiary_role:
        _process_rejection(information, procedure_id=procedure_id, reason="Compte existant avec cet email")
        return

    if information.id_piece_number:
        _duplicated_user = users_models.User.query.filter(
            users_models.User.idPieceNumber == information.id_piece_number
        ).first()
        if _duplicated_user:
            subscription_messages.on_duplicate_user(user)
            _process_rejection(
                information,
                procedure_id=procedure_id,
                reason=f"Nr de piece déjà utilisé par {_duplicated_user.id}",
                user=user,
            )
            return

    if not is_already_imported(information.application_id):
        duplicate_users = beneficiary_by_civility_query(
            first_name=information.first_name,
            last_name=information.last_name,
            date_of_birth=information.birth_date,
            exclude_email=information.email,
        ).all()
        if duplicate_users and information.application_id not in retry_ids:
            _process_duplication(duplicate_users, information, procedure_id)
            subscription_messages.on_duplicate_user(user)

        else:
            process_beneficiary_application(
                information=information,
                procedure_id=procedure_id,
                preexisting_account=user,
            )


def parse_beneficiary_information(application_detail: dict, procedure_id: int) -> fraud_models.DMSContent:
    dossier = application_detail["dossier"]
    email = dossier["email"]

    information = {
        "last_name": dossier["individual"]["nom"],
        "first_name": dossier["individual"]["prenom"],
        "civility": dossier["individual"]["civilite"],
        "email": email,
        "application_id": dossier["id"],
        "procedure_id": procedure_id,
    }
    parsing_errors = {}

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
            try:
                information["postal_code"] = re.search("^[0-9]{5}", space_free).group(0)
            except Exception:  # pylint: disable=broad-except
                parsing_errors["postal_code"] = value

        if label == "Veuillez indiquer votre statut":
            information["activity"] = value
        if label == "Quelle est votre adresse de résidence":
            information["address"] = value
        if label == "Quel est le numéro de la pièce que vous venez de saisir ?":
            value = value.strip()
            if not fraud_api.validate_id_piece_number_format_fraud_item(value):
                parsing_errors["id_piece_number"] = value
            else:
                information["id_piece_number"] = value

    if parsing_errors:
        raise DMSParsingError(email, parsing_errors, "Error validating")
    return fraud_models.DMSContent(**information)


def parse_beneficiary_information_graphql(application_detail: dict, procedure_id: int) -> fraud_models.DMSContent:
    email = application_detail["usager"]["email"]

    information = {
        "last_name": application_detail["demandeur"]["nom"],
        "first_name": application_detail["demandeur"]["prenom"],
        "civility": application_detail["demandeur"]["civilite"],
        "email": email,
        "application_id": application_detail["number"],
        "procedure_id": procedure_id,
    }
    parsing_errors = {}

    for field in application_detail["champs"]:
        label = field["label"]
        value = field["stringValue"]

        if "Veuillez indiquer votre département" in label:
            information["department"] = re.search("^[0-9]{2,3}|[2BbAa]{2}", value).group(0)
        if label in ("Quelle est votre date de naissance", "Quelle est ta date de naissance ?"):
            information["birth_date"] = date_parser.parse(value, FrenchParserInfo())
        if label in (
            "Quel est votre numéro de téléphone",
            "Quel est ton numéro de téléphone ?",
        ):
            information["phone"] = value.replace(" ", "")
        if label in (
            "Quel est le code postal de votre commune de résidence ?",
            "Quel est le code postal de votre commune de résidence ? (ex : 25370)",
            "Quel est le code postal de ta commune de résidence ? (ex : 25370)",
            "Quel est le code postal de ta commune de résidence ?",
        ):
            space_free = str(value).strip().replace(" ", "")
            try:
                information["postal_code"] = re.search("^[0-9]{5}", space_free).group(0)
            except Exception:  # pylint: disable=broad-except
                parsing_errors["postal_code"] = value

        if label in ("Veuillez indiquer votre statut", "Merci d'indiquer ton statut", "Merci d' indiquer ton statut"):
            information["activity"] = value
        if label in (
            "Quelle est votre adresse de résidence",
            "Quelle est ton adresse de résidence",
            "Quelle est ton adresse de résidence ?",
        ):
            information["address"] = value
        if label in (
            "Quel est le numéro de la pièce que vous venez de saisir ?",
            "Quel est le numéro de la pièce que tu viens de saisir ?",
        ):
            value = value.strip()
            if not fraud_api.validate_id_piece_number_format_fraud_item(value):
                parsing_errors["id_piece_number"] = value
            else:
                information["id_piece_number"] = value

    if parsing_errors:
        raise DMSParsingError(email, parsing_errors, "Error validating")
    return fraud_models.DMSContent(**information)


def process_beneficiary_application(
    information: fraud_models.DMSContent,
    procedure_id: int,
    preexisting_account: Optional[users_models.User] = None,
) -> None:
    """
    Create/update a user account and complete the import process.
    Note that a 'user' is not always a beneficiary.
    """
    user = create_beneficiary_from_application(information, user=preexisting_account)
    user.hasCompletedIdCheck = True
    try:
        repository.save(user)
    except ApiErrors as api_errors:
        logger.warning(
            "[BATCH][REMOTE IMPORT BENEFICIARIES] Could not save application %s, because of error: %s - Procedure %s",
            information.application_id,
            api_errors,
            procedure_id,
        )
        return

    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Successfully created user for application %s - Procedure %s",
        information.application_id,
        procedure_id,
    )

    beneficiary_import = save_beneficiary_import_with_status(
        ImportStatus.CREATED,
        information.application_id,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        user=user,
    )

    if not users_api.steps_to_become_beneficiary(user):
        deposit_source = beneficiary_import.get_detailed_source()
        subscription_api.activate_beneficiary(user, deposit_source)
    else:
        users_external.update_external_user(user)


def _process_duplication(
    duplicate_users: list[users_models.User], information: fraud_models.DMSContent, procedure_id: int
) -> None:
    number_of_beneficiaries = len(duplicate_users)
    duplicate_ids = ", ".join([str(u.id) for u in duplicate_users])
    message = f"{number_of_beneficiaries} utilisateur(s) en doublon {duplicate_ids} pour le dossier {information.application_id} - Procedure {procedure_id}"
    logger.warning("[BATCH][REMOTE IMPORT BENEFICIARIES] Duplicate beneficiaries found : %s", message)
    save_beneficiary_import_with_status(
        ImportStatus.DUPLICATE,
        information.application_id,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        detail=f"Utilisateur en doublon : {duplicate_ids}",
    )


def _process_rejection(
    information: fraud_models.DMSContent, procedure_id: int, reason: str, user: users_models.User = None
) -> None:
    save_beneficiary_import_with_status(
        ImportStatus.REJECTED,
        information.application_id,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        detail=reason,
        user=user,
    )
    logger.warning(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Rejected application %s because of '%s' - Procedure %s",
        information.application_id,
        reason,
        procedure_id,
    )
