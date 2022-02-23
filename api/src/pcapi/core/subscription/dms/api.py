import logging
import typing

from sqlalchemy import Integer
from sqlalchemy import or_
from sqlalchemy.orm import load_only

from pcapi import settings
from pcapi.connectors.dms import api as dms_connector_api
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.dms import api as fraud_dms_api
from pcapi.core.mails.transactional.users.pre_subscription_dms_error import (
    send_pre_subscription_from_dms_error_email_to_beneficiary,
)
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import repository as subscription_repository
import pcapi.core.subscription.api as subscription_api
import pcapi.core.users.models as users_models
from pcapi.core.users.repository import find_user_by_email
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportStatus
from pcapi.models.beneficiary_import_status import ImportStatus
import pcapi.repository as pcapi_repository


logger = logging.getLogger(__name__)


def handle_dms_state(
    user: users_models.User,
    result_content: fraud_models.DMSContent,
    procedure_id: int,
    application_id: int,
    state: dms_connector_api.GraphQLApplicationStates,
) -> None:

    logs_extra = {"application_id": application_id, "procedure_id": procedure_id, "user_email": user.email}

    current_fraud_check = fraud_dms_api.get_or_create_fraud_check(user, application_id, result_content)

    if state == dms_connector_api.GraphQLApplicationStates.draft:
        subscription_messages.on_dms_application_received(user)
        logger.info("DMS Application started.", extra=logs_extra)

    elif state == dms_connector_api.GraphQLApplicationStates.on_going:
        subscription_messages.on_dms_application_received(user)
        current_fraud_check.status = fraud_models.FraudCheckStatus.PENDING
        logger.info("DMS Application created.", extra=logs_extra)

    elif state == dms_connector_api.GraphQLApplicationStates.accepted:
        process_application(user, result_content)
        return

    elif state == dms_connector_api.GraphQLApplicationStates.refused:
        current_fraud_check.status = fraud_models.FraudCheckStatus.KO
        current_fraud_check.reasonCodes = [fraud_models.FraudReasonCode.REFUSED_BY_OPERATOR]

        subscription_messages.on_dms_application_refused(user)

        logger.info("DMS Application refused.", extra=logs_extra)

    elif state == dms_connector_api.GraphQLApplicationStates.without_continuation:
        current_fraud_check.status = fraud_models.FraudCheckStatus.CANCELED
        logger.info("DMS Application without continuation.", extra=logs_extra)

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
        except KeyError as e:
            logger.error(
                "[BATCH][REMOTE IMPORT BENEFICIARIES] Could not parse user email: %s",
                e,
                extra={"application_id": application_id, "procedure_id": procedure_id},
            )
            _process_user_parsing_error(application_id, procedure_id)
            continue

        user = find_user_by_email(user_email)
        if user is None:
            _process_user_not_found_error(user_email, application_id, procedure_id)
            continue

        try:
            result_content: fraud_models.IdCheckContent = dms_connector_api.parse_beneficiary_information_graphql(
                application_details, procedure_id
            )
        except subscription_exceptions.DMSParsingError as exc:
            _process_parsing_error(exc, user, procedure_id, application_id)
            continue

        except Exception as exc:  # pylint: disable=broad-except
            process_parsing_exception(exc, user, procedure_id, application_id)
            continue

        process_application(user, result_content)

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
        reason_codes=[fraud_models.FraudReasonCode.ERROR_IN_DATA],
        error_details=error_details,
    )


def _process_parsing_error(
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


def _process_user_parsing_error(application_id: int, procedure_id: int) -> None:
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Application %s in procedure %s has no user and was ignored",
        application_id,
        procedure_id,
    )
    subscription_repository.create_orphan_dms_application(application_id=application_id, procedure_id=procedure_id)


def _process_user_not_found_error(email: str, application_id: int, procedure_id: int) -> None:
    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Application %s in procedure %s has no user and was ignored",
        application_id,
        procedure_id,
    )
    subscription_repository.create_orphan_dms_application(
        application_id=application_id, procedure_id=procedure_id, email=email
    )


def process_application(
    user: users_models.User,
    result_content: fraud_models.DMSContent,
) -> None:
    try:
        fraud_check = fraud_api.on_dms_fraud_result(user, result_content)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error on dms fraud check result: %s", exc)
        return

    if fraud_check.status != fraud_models.FraudCheckStatus.OK:
        handle_validation_errors(user, fraud_check.reasonCodes, result_content, result_content.procedure_id)
        subscription_api.update_user_birth_date(user, result_content.get_birth_date())
        return

    try:
        fraud_api.create_honor_statement_fraud_check(
            user, "honor statement contained in DMS application", fraud_check.eligibilityType
        )
        subscription_api.on_successful_application(user=user, source_data=result_content)
    except Exception as exception:  # pylint: disable=broad-except
        logger.warning(
            "[BATCH][REMOTE IMPORT BENEFICIARIES] Could not save application %s, because of error: %s - Procedure %s",
            result_content.application_id,
            exception,
            result_content.procedure_id,
        )
        return

    logger.info(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Successfully imported DMS application %s - Procedure %s",
        result_content.application_id,
        result_content.procedure_id,
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


def _process_rejection(
    information: fraud_models.DMSContent, procedure_id: int, reason: str, user: users_models.User = None
) -> None:
    logger.warning(
        "[BATCH][REMOTE IMPORT BENEFICIARIES] Rejected application %s because of '%s' - Procedure %s",
        information.application_id,
        reason,
        procedure_id,
    )


# TODO: get_already_processed_applications_ids_from_beneficiary_imports is temporary.
#       It should be removed when all the current imports are done.
#       Check: 08/03/2022 @lixxday or #skwadak in slack
def get_already_processed_applications_ids(procedure_id: int) -> set[int]:
    return get_already_processed_applications_ids_from_beneficiary_imports(
        procedure_id
    ) | get_already_processed_applications_ids_from_fraud_checks(procedure_id)


def get_already_processed_applications_ids_from_beneficiary_imports(procedure_id: int) -> set[int]:
    return {
        beneficiary_import.applicationId
        for beneficiary_import in BeneficiaryImport.query.join(BeneficiaryImportStatus)
        .filter(
            BeneficiaryImportStatus.status.in_(
                [ImportStatus.CREATED, ImportStatus.REJECTED, ImportStatus.DUPLICATE, ImportStatus.ERROR]
            )
        )
        .options(load_only(BeneficiaryImport.applicationId))
        .filter(BeneficiaryImport.sourceId == procedure_id)
        .all()
    }


def get_already_processed_applications_ids_from_fraud_checks(procedure_id: int) -> set[int]:
    fraud_check_queryset = fraud_models.BeneficiaryFraudCheck.query.filter(
        fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.DMS,
        or_(
            fraud_models.BeneficiaryFraudCheck.resultContent["procedure_id"].astext.cast(Integer) == procedure_id,
            fraud_models.BeneficiaryFraudCheck.resultContent
            == None,  # If there was a parsing error, a fraudCheck exists but no resultContent
        ),
        fraud_models.BeneficiaryFraudCheck.status.notin_(
            [
                fraud_models.FraudCheckStatus.PENDING,
                fraud_models.FraudCheckStatus.STARTED,
            ]
        ),
    )
    fraud_check_ids = {
        int(fraud_check[0])
        for fraud_check in fraud_check_queryset.with_entities(fraud_models.BeneficiaryFraudCheck.thirdPartyId)
    }
    orphans_queryset = fraud_models.OrphanDmsApplication.query.filter(
        fraud_models.OrphanDmsApplication.process_id == procedure_id
    )
    orphans_ids = {
        orphan[0] for orphan in orphans_queryset.with_entities(fraud_models.OrphanDmsApplication.application_id)
    }

    return fraud_check_ids | orphans_ids


def get_dms_subscription_item_status(
    user: users_models.User,
    eligibility: typing.Optional[users_models.EligibilityType],
    dms_fraud_checks: list[fraud_models.BeneficiaryFraudCheck],
) -> subscription_models.SubscriptionItemStatus:
    if any(check.status == fraud_models.FraudCheckStatus.OK for check in dms_fraud_checks):
        return subscription_models.SubscriptionItemStatus.OK
    if any(
        check.status in (fraud_models.FraudCheckStatus.STARTED, fraud_models.FraudCheckStatus.PENDING)
        for check in dms_fraud_checks
    ):
        return subscription_models.SubscriptionItemStatus.PENDING
    if any(check.status == fraud_models.FraudCheckStatus.KO for check in dms_fraud_checks):
        return subscription_models.SubscriptionItemStatus.KO
    if any(check.status == fraud_models.FraudCheckStatus.SUSPICIOUS for check in dms_fraud_checks):
        return subscription_models.SubscriptionItemStatus.SUSPICIOUS

    if subscription_api.is_eligibility_activable(user, eligibility):
        return subscription_models.SubscriptionItemStatus.TODO

    return subscription_models.SubscriptionItemStatus.VOID
