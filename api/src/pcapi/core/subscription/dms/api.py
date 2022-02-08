import logging

from pcapi import settings
from pcapi.connectors.dms import api as dms_connector_api
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import repository as fraud_repository
from pcapi.core.fraud.dms import api as fraud_dms_api
import pcapi.core.fraud.models as fraud_models
from pcapi.core.mails.transactional.users.pre_subscription_dms_error import (
    send_pre_subscription_from_dms_error_email_to_beneficiary,
)
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.core.subscription import messages as subscription_messages
import pcapi.core.subscription.api as subscription_api
import pcapi.core.users.models as users_models
from pcapi.core.users.repository import find_user_by_email
from pcapi.models.api_errors import ApiErrors
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
import pcapi.repository as pcapi_repository
from pcapi.repository.beneficiary_import_queries import get_already_processed_applications_ids
from pcapi.repository.beneficiary_import_queries import save_beneficiary_import_with_status


logger = logging.getLogger(__name__)


def handle_dms_state(
    user: users_models.User,
    application: fraud_models.DMSContent,
    procedure_id: int,
    application_id: int,
    state: dms_connector_api.GraphQLApplicationStates,
) -> None:

    logs_extra = {"application_id": application_id, "procedure_id": procedure_id, "user_email": user.email}

    current_fraud_check = fraud_dms_api.get_fraud_check(user, application_id)
    if current_fraud_check is None:
        # create a fraud_check whatever the status is because we may have missed a webhook event
        current_fraud_check = fraud_dms_api.create_fraud_check(user, application)
        user.submit_user_identity()

    if state == dms_connector_api.GraphQLApplicationStates.draft:
        subscription_messages.on_dms_application_received(user)
        logger.info("DMS Application started.", extra=logs_extra)

    elif state == dms_connector_api.GraphQLApplicationStates.on_going:
        subscription_messages.on_dms_application_received(user)
        current_fraud_check.status = fraud_models.FraudCheckStatus.PENDING
        logger.info("DMS Application created.", extra=logs_extra)

    elif state == dms_connector_api.GraphQLApplicationStates.accepted:
        logger.info("DMS Application accepted. User will be validated in the cron job.", extra=logs_extra)

    elif state == dms_connector_api.GraphQLApplicationStates.refused:
        fraud_api.update_or_create_fraud_check_failed(
            user,
            str(application_id),
            current_fraud_check.source_data(),
            [fraud_models.FraudReasonCode.REFUSED_BY_OPERATOR],
        )
        subscription_messages.on_dms_application_refused(user)

        logger.info("DMS Application refused.", extra=logs_extra)

    pcapi_repository.repository.save(current_fraud_check)


def import_dms_users(procedure_id: int) -> None:
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Start import from Démarches Simplifiées for "
        "procedure = %s - Procedure %s",
        procedure_id,
        procedure_id,
    )

    existing_applications_ids = get_already_processed_applications_ids(procedure_id)
    client = dms_connector_api.DMSGraphQLClient()
    for application_details in client.get_applications_with_details(
        procedure_id, dms_connector_api.GraphQLApplicationStates.accepted
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
            information: fraud_models.IdCheckContent = dms_connector_api.parse_beneficiary_information_graphql(
                application_details, procedure_id
            )
        except subscription_exceptions.DMSParsingError as exc:
            process_parsing_error(exc, user, procedure_id, application_id)
            continue

        except Exception as exc:  # pylint: disable=broad-except
            process_parsing_exception(exc, user, procedure_id, application_id)
            continue

        process_application(user, procedure_id, application_id, information)

    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] End import from Démarches Simplifiées - Procedure %s", procedure_id
    )


def notify_parsing_exception(parsing_error: subscription_exceptions.DMSParsingError, application_techid: str, client):
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
    exception: subscription_exceptions.DMSParsingError, user: users_models.User, procedure_id: int, application_id: int
) -> None:
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Invalid values (%r) detected in Application %s in procedure %s",
        exception.errors,
        application_id,
        procedure_id,
    )
    send_pre_subscription_from_dms_error_email_to_beneficiary(
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

    fraud_repository.create_orphan_dms_application(application_id=application_id, procedure_id=procedure_id)

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
    fraud_repository.create_orphan_dms_application(
        application_id=application_id, procedure_id=procedure_id, email=email
    )

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
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error on dms fraud check result: %s", exc)
        return

    if fraud_check.status != fraud_models.FraudCheckStatus.OK:
        handle_validation_errors(user, fraud_check.reasonCodes, information, procedure_id)
        subscription_api.update_user_birth_date(user, information.get_birth_date())
        return

    try:
        eligibility_type = fraud_api.decide_eligibility(user, information)

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
        return

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

    eligibility_type = fraud_api.decide_eligibility(user, information)
    # keeps the creation of a beneficiaryImport to avoid reprocess the same application
    # forever, it's mandatory to make get_already_processed_applications_ids work
    save_beneficiary_import_with_status(
        ImportStatus.REJECTED,
        application_id=information.application_id,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        user=user,
        detail="Voir les details dans la page support",
        eligibility_type=eligibility_type,
    )


def _process_rejection(
    information: fraud_models.DMSContent, procedure_id: int, reason: str, user: users_models.User = None
) -> None:
    eligibility_type = fraud_api.decide_eligibility(user, information)

    # TODO: remove when we use fraud checks
    save_beneficiary_import_with_status(
        ImportStatus.REJECTED,
        information.application_id,
        source=BeneficiaryImportSources.demarches_simplifiees,
        source_id=procedure_id,
        detail=reason,
        user=user,
        eligibility_type=eligibility_type,
    )
    logger.warning(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Rejected application %s because of '%s' - Procedure %s",
        information.application_id,
        reason,
        procedure_id,
    )
