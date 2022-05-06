import logging
import typing

from pcapi import settings
from pcapi.connectors.dms import api as dms_connector_api
from pcapi.connectors.dms import models as dms_models
from pcapi.core import logging as core_logging
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.dms import api as fraud_dms_api
from pcapi.core.mails.transactional.users import duplicate_beneficiary
from pcapi.core.mails.transactional.users.pre_subscription_dms_error import (
    send_pre_subscription_from_dms_error_email_to_beneficiary,
)
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
import pcapi.core.subscription.api as subscription_api
import pcapi.core.users.models as users_models
from pcapi.core.users.repository import find_user_by_email
import pcapi.repository as pcapi_repository

from . import constants as dms_constants
from . import repository as dms_repository


logger = logging.getLogger(__name__)


def handle_dms_state(
    user: users_models.User,
    state: dms_models.GraphQLApplicationStates,
    result_content: fraud_models.DMSContent,
    procedure_id: int,
    application_id: int,
    application_scalar_id: str,
) -> fraud_models.BeneficiaryFraudCheck:

    logs_extra = {"application_id": application_id, "procedure_id": procedure_id, "user_email": user.email}

    current_fraud_check = fraud_dms_api.get_or_create_fraud_check(user, application_id, result_content)

    if state == dms_models.GraphQLApplicationStates.draft:
        eligibility_type = current_fraud_check.eligibilityType
        if eligibility_type is None:
            fraud_dms_api.on_dms_eligibility_error(
                user, current_fraud_check, application_scalar_id, extra_data=logs_extra
            )
        else:
            subscription_messages.on_dms_application_received(user)
        current_fraud_check.status = fraud_models.FraudCheckStatus.STARTED  # type: ignore [assignment]
        logger.info("DMS Application started.", extra=logs_extra)

    elif state == dms_models.GraphQLApplicationStates.on_going:
        subscription_messages.on_dms_application_received(user)
        current_fraud_check.status = fraud_models.FraudCheckStatus.PENDING  # type: ignore [assignment]
        logger.info("DMS Application created.", extra=logs_extra)

    elif state == dms_models.GraphQLApplicationStates.accepted:
        process_application(user, result_content)
        return current_fraud_check

    elif state == dms_models.GraphQLApplicationStates.refused:
        current_fraud_check.status = fraud_models.FraudCheckStatus.KO  # type: ignore [assignment]
        current_fraud_check.reasonCodes = [fraud_models.FraudReasonCode.REFUSED_BY_OPERATOR]  # type: ignore [list-item]

        subscription_messages.on_dms_application_refused(user)

        logger.info("DMS Application refused.", extra=logs_extra)

    elif state == dms_models.GraphQLApplicationStates.without_continuation:
        current_fraud_check.status = fraud_models.FraudCheckStatus.CANCELED  # type: ignore [assignment]
        logger.info("DMS Application without continuation.", extra=logs_extra)

    pcapi_repository.repository.save(current_fraud_check)
    return current_fraud_check


def import_dms_users(procedure_id: int) -> None:
    logger.info(
        "[DMS][REMOTE IMPORT BENEFICIARIES] Start import from Démarches Simplifiées for "
        "procedure = %s - Procedure %s",
        procedure_id,
        procedure_id,
    )

    already_processed_applications_ids = dms_repository.get_already_processed_applications_ids(procedure_id)
    client = dms_connector_api.DMSGraphQLClient()
    processed_count = 0

    for application_details in client.get_applications_with_details(
        procedure_id, dms_models.GraphQLApplicationStates.accepted
    ):
        application_id = application_details.number
        if application_id in already_processed_applications_ids:
            continue
        processed_count += 1
        try:
            user_email = application_details.profile.email
        except KeyError as e:
            logger.error(
                "[DMS][REMOTE IMPORT BENEFICIARIES] Could not parse user email: %s",
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
            result_content = dms_connector_api.parse_beneficiary_information_graphql(application_details, procedure_id)
        except subscription_exceptions.DMSParsingError as exc:
            logger.info("[DMS] Invalid values (%r) detected in application %s", exc.errors, application_id)
            _process_parsing_error(
                exc, user, application_id, dms_models.GraphQLApplicationStates.accepted, application_details.id
            )
            continue

        except Exception:  # pylint: disable=broad-except
            logger.exception("[DMS] Exception when parsing application %s", application_id)
            _process_parsing_exception(user, application_id)
            continue

        process_application(user, result_content)

    logger.info(
        "[DMS][REMOTE IMPORT BENEFICIARIES] End import from Démarches Simplifiées - Procedure %s - Processed %s applications",
        procedure_id,
        processed_count,
    )


def _notify_parsing_error(parsing_errors: dict[str, str], application_scalar_id: str) -> None:
    client = dms_connector_api.DMSGraphQLClient()
    if "birth_date" in parsing_errors:
        client.send_user_message(
            application_scalar_id, settings.DMS_INSTRUCTOR_ID, subscription_messages.DMS_ERROR_MESSSAGE_BIRTH_DATE
        )
    elif "postal_code" in parsing_errors and "id_piece_number" in parsing_errors:
        client.send_user_message(
            application_scalar_id, settings.DMS_INSTRUCTOR_ID, subscription_messages.DMS_ERROR_MESSAGE_DOUBLE_ERROR
        )
    elif "postal_code" in parsing_errors and "id_piece_number" not in parsing_errors:
        client.send_user_message(
            application_scalar_id,
            settings.DMS_INSTRUCTOR_ID,
            subscription_messages.DMS_ERROR_MESSAGE_ERROR_POSTAL_CODE,
        )
    elif "id_piece_number" in parsing_errors and "postal_code" not in parsing_errors:
        client.send_user_message(
            application_scalar_id,
            settings.DMS_INSTRUCTOR_ID,
            subscription_messages.DMS_ERROR_MESSAGE_ERROR_ID_PIECE,
        )
    elif "first_name" in parsing_errors or "last_name" in parsing_errors:
        client.send_user_message(
            application_scalar_id,
            settings.DMS_INSTRUCTOR_ID,
            subscription_messages.DMS_NAME_INVALID_ERROR_MESSAGE,
        )


def _process_parsing_error(
    parsing_error: subscription_exceptions.DMSParsingError,
    user: users_models.User,
    application_id: int,
    state: dms_models.GraphQLApplicationStates,
    application_scalar_id: str,
) -> fraud_models.BeneficiaryFraudCheck:
    subscription_messages.on_dms_application_parsing_errors(
        user,
        list(parsing_error.errors.keys()),
        is_application_updatable=state == dms_models.GraphQLApplicationStates.draft,
    )

    if state == dms_models.GraphQLApplicationStates.draft:
        _notify_parsing_error(parsing_error.errors, application_scalar_id)
    elif state in dms_constants.FINAL_INSTRUCTOR_DECISION_STATES:
        send_pre_subscription_from_dms_error_email_to_beneficiary(
            parsing_error.user_email,
            parsing_error.errors.get("postal_code"),
            parsing_error.errors.get("id_piece_number"),
        )

    fraud_check = fraud_dms_api.get_or_create_fraud_check(user, application_id)

    if state in dms_constants.FINAL_INSTRUCTOR_DECISION_STATES:
        fraud_check.status = fraud_models.FraudCheckStatus.ERROR  # type: ignore [assignment]

    errors = ",".join([f"'{key}' ({value})" for key, value in sorted(parsing_error.errors.items())])
    fraud_check.reason = f"Erreur dans les données soumises dans le dossier DMS : {errors}"
    fraud_check.reasonCodes = [fraud_models.FraudReasonCode.ERROR_IN_DATA]  # type: ignore [list-item]

    pcapi_repository.repository.save(fraud_check)

    return fraud_check


def _process_parsing_exception(user: users_models.User, application_id: int) -> None:
    _update_or_create_error_fraud_check(user, application_id, "Erreur de lecture du dossier")


def _update_or_create_error_fraud_check(user: users_models.User, application_id: int, reason: str):  # type: ignore [no-untyped-def]
    # Update fraud check for observability and to avoid reimporting the same application
    fraud_check = fraud_dms_api.get_or_create_fraud_check(user, application_id)

    fraud_check.status = fraud_models.FraudCheckStatus.ERROR  # type: ignore [assignment]
    fraud_check.reason = reason
    fraud_check.reasonCodes = [fraud_models.FraudReasonCode.ERROR_IN_DATA]  # type: ignore [list-item]

    pcapi_repository.repository.save(fraud_check)


def _process_user_parsing_error(application_id: int, procedure_id: int) -> None:
    logger.info(
        "[DMS][REMOTE IMPORT BENEFICIARIES] Application %s in procedure %s has no user and was ignored",
        application_id,
        procedure_id,
    )
    dms_repository.create_orphan_dms_application(application_id=application_id, procedure_id=procedure_id)


def _process_user_not_found_error(email: str, application_id: int, procedure_id: int) -> None:
    logger.info(
        "User not found for application %s procedure %s email %s",
        application_id,
        procedure_id,
        email,
    )
    dms_repository.create_orphan_dms_application(application_id=application_id, procedure_id=procedure_id, email=email)


def process_application(user: users_models.User, result_content: fraud_models.DMSContent) -> None:
    try:
        fraud_check = fraud_api.on_dms_fraud_result(user, result_content)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error on dms fraud check result: %s", exc)
        return

    if fraud_check.status != fraud_models.FraudCheckStatus.OK:
        handle_validation_errors(user, fraud_check.reasonCodes, result_content)  # type: ignore [arg-type]
        subscription_api.update_user_birth_date(user, result_content.get_birth_date())
        return

    fraud_api.create_honor_statement_fraud_check(
        user, "honor statement contained in DMS application", fraud_check.eligibilityType  # type: ignore [arg-type]
    )
    try:
        subscription_api.on_successful_application(user=user, source_data=result_content)
    except Exception as exception:  # pylint: disable=broad-except
        logger.exception(
            "[DMS][REMOTE IMPORT BENEFICIARIES] Could not save application %s, because of error: %s - Procedure %s",
            result_content.application_id,
            exception,
            result_content.procedure_id,
        )
        return

    logger.info(
        "[DMS][REMOTE IMPORT BENEFICIARIES] Successfully imported DMS application %s - Procedure %s",
        result_content.application_id,
        result_content.procedure_id,
    )


def handle_validation_errors(
    user: users_models.User,
    reason_codes: list[fraud_models.FraudReasonCode],
    dms_content: fraud_models.DMSContent,
) -> None:
    if fraud_models.FraudReasonCode.DUPLICATE_USER in reason_codes:
        subscription_messages.on_duplicate_user(user)
        duplicate_beneficiary.send_duplicate_beneficiary_email(user, dms_content, False)
    elif fraud_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER in reason_codes:
        subscription_messages.on_duplicate_user(user)
        duplicate_beneficiary.send_duplicate_beneficiary_email(user, dms_content, True)

    reason = ", ".join([code.name for code in reason_codes])

    logger.warning(
        "[DMS][REMOTE IMPORT BENEFICIARIES] Rejected application %s because of '%s' - Procedure %s",
        dms_content.application_id,
        reason,
        dms_content.procedure_id,
        extra={"user_id": user.id},
    )


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


def try_dms_orphan_adoption(user: users_models.User):  # type: ignore [no-untyped-def]
    dms_orphan = fraud_models.OrphanDmsApplication.query.filter_by(email=user.email).first()
    if not dms_orphan:
        return

    dms_application = dms_connector_api.DMSGraphQLClient().get_single_application_details(dms_orphan.application_id)
    fraud_check = handle_dms_application(dms_application, dms_orphan.process_id)

    if fraud_check is not None:
        pcapi_repository.repository.delete(dms_orphan)


def handle_dms_application(
    dms_application: dms_models.DmsApplicationResponse, procedure_id: int
) -> typing.Optional[fraud_models.BeneficiaryFraudCheck]:
    application_id = dms_application.number
    user_email = dms_application.profile.email
    application_scalar_id = dms_application.id

    log_extra_data = {
        "application_id": application_id,
        "application_scalar_id": application_scalar_id,
        "procedure_id": procedure_id,
        "user_email": user_email,
    }

    try:
        state = dms_models.GraphQLApplicationStates(dms_application.state)
    except ValueError:
        logger.exception(
            "Unknown GraphQLApplicationState for application %s procedure %s email %s",
            application_id,
            procedure_id,
            user_email,
            extra=log_extra_data,
        )
        return None

    user = find_user_by_email(user_email)

    if not user:
        _process_user_not_found_error(user_email, application_id, procedure_id)
        if state == dms_models.GraphQLApplicationStates.draft:
            dms_connector_api.DMSGraphQLClient().send_user_message(
                application_scalar_id,
                settings.DMS_INSTRUCTOR_ID,
                subscription_messages.DMS_ERROR_MESSAGE_USER_NOT_FOUND,
            )

        return None
    try:
        application = dms_connector_api.parse_beneficiary_information_graphql(dms_application, procedure_id)
        core_logging.log_for_supervision(
            logger=logger,
            log_level=logging.INFO,
            log_message="Successfully parsed DMS application",
            extra=log_extra_data,
        )
    except subscription_exceptions.DMSParsingError as parsing_error:
        logger.info("[DMS] Parsing error in application", extra=log_extra_data)
        return _process_parsing_error(parsing_error, user, application_id, state, application_scalar_id)

    return handle_dms_state(user, state, application, procedure_id, application_id, application_scalar_id)
