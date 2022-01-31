import logging
import re

from dateutil import parser as date_parser

from pcapi import settings
from pcapi.connectors.dms import api as api_dms
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.exceptions as fraud_exceptions
import pcapi.core.fraud.models as fraud_models
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.messages as subscription_messages
import pcapi.core.users.models as users_models
from pcapi.core.users.repository import find_user_by_email
from pcapi.domain import user_emails
from pcapi.models.api_errors import ApiErrors
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.repository.beneficiary_import_queries import get_already_processed_applications_ids
from pcapi.repository.beneficiary_import_queries import save_beneficiary_import_with_status
from pcapi.utils.date import FrenchParserInfo


logger = logging.getLogger(__name__)


class DMSParsingError(ValueError):
    def __init__(self, user_email: str, errors: dict[str, str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = errors
        self.user_email = user_email


def run(procedure_id: int) -> None:
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Start import from Démarches Simplifiées for "
        "procedure = %s - Procedure %s",
        procedure_id,
        procedure_id,
    )

    existing_applications_ids = get_already_processed_applications_ids(procedure_id)
    client = api_dms.DMSGraphQLClient()
    for application_details in client.get_applications_with_details(
        procedure_id, api_dms.GraphQLApplicationStates.accepted
    ):
        application_id = application_details["number"]
        if application_id in existing_applications_ids:
            continue
        try:
            user_email = application_details["usager"]["email"]
        except KeyError:
            process_user_parsing_error(application_id, procedure_id)
            continue

        user = find_user_by_email(user_email)
        if user is None:
            process_user_not_found_error(user_email, application_id, procedure_id)
            continue

        try:
            information: fraud_models.IdCheckContent = parse_beneficiary_information_graphql(
                application_details, procedure_id
            )
        except DMSParsingError as exc:
            process_parsing_error(exc, user, procedure_id, application_id)
            continue

        except Exception as exc:  # pylint: disable=broad-except
            process_parsing_exception(exc, user, procedure_id, application_id)
            continue

        process_application(user, procedure_id, application_id, information)

    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] End import from Démarches Simplifiées - Procedure %s", procedure_id
    )


def notify_parsing_exception(parsing_error: DMSParsingError, application_techid: str, client):
    if "birth_date" in parsing_error:
        client.send_user_message(
            application_techid, settings.DMS_INSTRUCTOR_ID, subscription_messages.DMS_ERROR_MESSSAGE_BIRTH_DATE
        )
    elif "postal_code" in parsing_error and "id_piece_number" in parsing_error:
        client.send_user_message(
            application_techid, settings.DMS_INSTRUCTOR_ID, subscription_messages.DMS_ERROR_MESSAGE_DOUBLE_ERROR
        )
    elif "postal_code" in parsing_error and "id_piece_number" not in parsing_error:
        client.send_user_message(
            application_techid,
            settings.DMS_INSTRUCTOR_ID,
            subscription_messages.DMS_ERROR_MESSAGE_ERROR_POSTAL_CODE,
        )
    elif "id_piece_number" in parsing_error and "postal_code" not in parsing_error:
        client.send_user_message(
            application_techid,
            settings.DMS_INSTRUCTOR_ID,
            subscription_messages.DMS_ERROR_MESSAGE_ERROR_ID_PIECE,
        )


def process_parsing_exception(
    exception: Exception, user: users_models.User, procedure_id: int, application_id: int
) -> None:
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Application %s in procedure %s had errors and was ignored: %s",
        application_id,
        procedure_id,
        exception,
        exc_info=True,
    )
    error_details = f"Le dossier {application_id} contient des erreurs et a été ignoré - Procedure {procedure_id}"
    # Create fraud check for observability
    fraud_api.create_dms_fraud_check_error(
        user,
        application_id,
        reason_codes=[fraud_models.FraudReasonCode.REFUSED_BY_OPERATOR],
        error_details=error_details,
    )

    # TODO: remove when the fraud check is the only object used to check for DMS applications
    save_beneficiary_import_with_status(
        ImportStatus.ERROR,
        application_id,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        detail=error_details,
        eligibility_type=None,
    )


def process_parsing_error(
    exception: DMSParsingError, user: users_models.User, procedure_id: int, application_id: int
) -> None:
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Invalid values (%r) detected in Application %s in procedure %s",
        exception.errors,
        application_id,
        procedure_id,
    )
    user_emails.send_dms_wrong_values_emails(
        exception.user_email, exception.errors.get("postal_code"), exception.errors.get("id_piece_number")
    )
    errors = ",".join([f"'{key}' ({value})" for key, value in sorted(exception.errors.items())])
    error_details = f"Erreur dans les données soumises dans le dossier DMS : {errors}"
    subscription_messages.on_dms_application_parsing_errors(user, list(exception.errors.keys()))
    # Create fraud check for observability, and to avoid reimporting the same application
    fraud_api.create_dms_fraud_check_error(
        user,
        application_id,
        reason_codes=[fraud_models.FraudReasonCode.ERROR_IN_DATA],
        error_details=error_details,
    )

    # TODO: remove this line when the fraud check is the only object used for DMS applications
    save_beneficiary_import_with_status(
        ImportStatus.ERROR,
        application_id,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        detail=error_details,
        user=user,
        eligibility_type=None,
    )


def process_user_parsing_error(application_id: int, procedure_id: int) -> None:
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Application %s in procedure %s has no user and was ignored",
        application_id,
        procedure_id,
    )
    error_details = (
        f"Erreur lors de l'analyse des données du dossier {application_id}. "
        f"Impossible de récupérer l'email de l'utilisateur - Procedure {procedure_id}"
    )
    # TODO: Create fraud check for observability.
    # Else find a way to remove the application from DMS.

    # TODO: remove this line when the fraud check is the only object used for DMS applications
    # keep a compatibility with BeneficiaryImport table
    save_beneficiary_import_with_status(
        ImportStatus.ERROR,
        application_id,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        detail=error_details,
        eligibility_type=None,
    )


def process_user_not_found_error(email: str, application_id: int, procedure_id: int) -> None:
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Application %s in procedure %s has no user and was ignored",
        application_id,
        procedure_id,
    )
    # TODO: Create fraud check and find a way to remove the application from DMS.

    # TODO: remove when the fraud check is the only object used for DMS applications
    save_beneficiary_import_with_status(
        ImportStatus.ERROR,
        application_id,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        detail=f"Aucun utilisateur trouvé pour l'email {email}",
        eligibility_type=None,
    )


def process_application(
    user: users_models.User,
    procedure_id: int,
    application_id: int,
    information: fraud_models.DMSContent,
) -> None:
    try:
        fraud_check = fraud_api.on_dms_fraud_result(user, information)
    except fraud_exceptions.BeneficiaryFraudResultCannotBeDowngraded:
        logger.warning("Trying to downgrade a BeneficiaryFraudResult status already OK", extra={"user_id": user.id})
        reason = "Compte existant avec cet email"
        fraud_models.BeneficiaryFraudCheck(
            user=user,
            type=fraud_models.FraudCheckType.DMS,
            thirdPartyId=information.application_id,
            resultContent=information,
            status=fraud_models.FraudCheckStatus.ERROR,
            reason=reason,
            reasonCodes=[fraud_models.FraudReasonCode.ALREADY_BENEFICIARY],
            eligibilityType=None,
        )
        _process_rejection(information, procedure_id, reason, user)

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error on dms fraud check result: %s", exc)

    else:
        if fraud_check.status != fraud_models.FraudCheckStatus.OK:
            handle_validation_errors(user, fraud_check.reasonCodes, information, procedure_id)
            subscription_api.update_user_birth_date(user, information.get_birth_date())
            return

        try:
            eligibility_type = information.get_eligibility_type()

            fraud_api.create_honor_statement_fraud_check(
                user, "honor statement contained in DMS application", eligibility_type
            )
            subscription_api.on_successful_application(
                user=user,
                source_data=information,
                eligibility_type=eligibility_type,
                application_id=application_id,
                source_id=procedure_id,
                source=BeneficiaryImportSources.demarches_simplifiees,
            )
        except ApiErrors as api_errors:
            logger.warning(
                "[BATCH][REMOTE IMPORT BENEFICIARIES] Could not save application %s, because of error: %s - Procedure %s",
                application_id,
                api_errors,
                procedure_id,
            )
        else:
            logger.info(
                "[BATCH][REMOTE IMPORT BENEFICIARIES] Successfully created user for application %s - Procedure %s",
                information.application_id,
                procedure_id,
            )


def handle_validation_errors(
    user: users_models.User,
    reason_codes: list[fraud_models.FraudReasonCode],
    information: fraud_models.DMSContent,
    procedure_id: int,
) -> None:
    for item in reason_codes:
        if item == fraud_models.FraudReasonCode.ALREADY_BENEFICIARY:
            _process_rejection(information, procedure_id=procedure_id, reason="Compte existant avec cet email")
        if item == fraud_models.FraudReasonCode.NOT_ELIGIBLE:
            _process_rejection(information, procedure_id=procedure_id, reason="L'utilisateur n'est pas éligible")
        if item == fraud_models.FraudReasonCode.DUPLICATE_USER:
            subscription_messages.on_duplicate_user(user)
        if item == fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER:
            subscription_messages.on_duplicate_user(user)

    # keeps the creation of a beneficiaryImport to avoid reprocess the same application
    # forever, it's mandatory to make get_already_processed_applications_ids work
    save_beneficiary_import_with_status(
        ImportStatus.REJECTED,
        application_id=information.application_id,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        user=user,
        detail="Voir les details dans la page support",
        eligibility_type=information.get_eligibility_type(),
    )


def parse_beneficiary_information_graphql(application_detail: dict, procedure_id: int) -> fraud_models.DMSContent:
    email = application_detail["usager"]["email"]

    information = {
        "last_name": application_detail["demandeur"]["nom"],
        "first_name": application_detail["demandeur"]["prenom"],
        "civility": application_detail["demandeur"]["civilite"],
        "email": email,
        "application_id": application_detail["number"],
        "procedure_id": procedure_id,
        "registration_datetime": application_detail[
            "datePassageEnConstruction"
        ],  # parse with format  "2021-09-15T15:19:20+02:00"
    }
    parsing_errors = {}

    for field in application_detail["champs"]:
        label = field["label"]
        value = field["stringValue"]

        if "Veuillez indiquer votre département" in label:
            information["department"] = re.search("^[0-9]{2,3}|[2BbAa]{2}", value).group(0)
        if label in ("Quelle est votre date de naissance", "Quelle est ta date de naissance ?"):
            try:
                information["birth_date"] = date_parser.parse(value, FrenchParserInfo())
            except Exception:  # pylint: disable=broad-except
                parsing_errors["birth_date"] = value

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


def _process_rejection(
    information: fraud_models.DMSContent, procedure_id: int, reason: str, user: users_models.User = None
) -> None:
    # TODO: remove when we use fraud checks
    save_beneficiary_import_with_status(
        ImportStatus.REJECTED,
        information.application_id,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        detail=reason,
        user=user,
        eligibility_type=information.get_eligibility_type(),
    )
    logger.warning(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Rejected application %s because of '%s' - Procedure %s",
        information.application_id,
        reason,
        procedure_id,
    )
