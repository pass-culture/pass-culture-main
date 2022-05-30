import logging
import typing

from pcapi import settings
from pcapi.connectors.dms import api as dms_connector_api
from pcapi.connectors.dms import models as dms_models
from pcapi.connectors.dms import serializer as dms_serializer
from pcapi.core import logging as core_logging
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.fraud.dms import api as fraud_dms_api
from pcapi.core.mails.transactional.users import dms_subscription_emails
from pcapi.core.mails.transactional.users import duplicate_beneficiary
from pcapi.core.subscription import exceptions as subscription_exceptions
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
import pcapi.core.subscription.api as subscription_api
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users.repository import find_user_by_email
import pcapi.repository as pcapi_repository

from . import repository as dms_repository


logger = logging.getLogger(__name__)


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
    application_number = dms_application.number
    user_email = users_utils.sanitize_email(dms_application.profile.email)
    application_scalar_id = dms_application.id
    state = dms_models.GraphQLApplicationStates(dms_application.state)

    log_extra_data = {
        "application_number": application_number,
        "application_scalar_id": application_scalar_id,
        "procedure_id": procedure_id,
        "user_email": user_email,
    }

    user = find_user_by_email(user_email)

    if not user:
        logger.info("[DMS] User not found for application", extra=log_extra_data)
        _process_user_not_found_error(user_email, application_number, procedure_id, state, application_scalar_id)
        return None
    try:
        application_content = dms_serializer.parse_beneficiary_information_graphql(dms_application, procedure_id)
        core_logging.log_for_supervision(
            logger=logger,
            log_level=logging.INFO,
            log_message="Successfully parsed DMS application",
            extra=log_extra_data,
        )
    except subscription_exceptions.DMSParsingError as parsing_error:
        logger.info("[DMS] Parsing error in application", extra=log_extra_data)
        return _process_parsing_error(parsing_error, user, application_number, state, application_scalar_id)

    logger.info("[DMS] Application received with state %s", state, extra=log_extra_data)

    current_fraud_check = fraud_dms_api.get_or_create_fraud_check(user, application_number, application_content)
    current_fraud_check.resultContent = application_content.dict()

    if state == dms_models.GraphQLApplicationStates.draft:
        eligibility_type = current_fraud_check.eligibilityType
        if eligibility_type is None:
            fraud_dms_api.on_dms_eligibility_error(
                user, current_fraud_check, application_scalar_id, extra_data=log_extra_data
            )
        else:
            subscription_messages.on_dms_application_received(user)
        current_fraud_check.status = fraud_models.FraudCheckStatus.STARTED  # type: ignore [assignment]

    elif state == dms_models.GraphQLApplicationStates.on_going:
        subscription_messages.on_dms_application_received(user)
        current_fraud_check.status = fraud_models.FraudCheckStatus.PENDING  # type: ignore [assignment]

    elif state == dms_models.GraphQLApplicationStates.accepted:
        _process_accepted_application(user, application_content)
        return current_fraud_check

    elif state == dms_models.GraphQLApplicationStates.refused:
        current_fraud_check.status = fraud_models.FraudCheckStatus.KO  # type: ignore [assignment]
        current_fraud_check.reasonCodes = [fraud_models.FraudReasonCode.REFUSED_BY_OPERATOR]  # type: ignore [list-item]

        subscription_messages.on_dms_application_refused(user)

    elif state == dms_models.GraphQLApplicationStates.without_continuation:
        current_fraud_check.status = fraud_models.FraudCheckStatus.CANCELED  # type: ignore [assignment]

    pcapi_repository.repository.save(current_fraud_check)
    return current_fraud_check


def _notify_parsing_error(parsing_errors: dict[str, typing.Optional[str]], application_scalar_id: str) -> None:
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
    application_number: int,
    state: dms_models.GraphQLApplicationStates,
    application_scalar_id: str,
) -> fraud_models.BeneficiaryFraudCheck:
    subscription_messages.on_dms_application_parsing_errors(
        user,
        list(parsing_error.errors.keys()),
        is_application_updatable=state
        in (dms_models.GraphQLApplicationStates.draft, dms_models.GraphQLApplicationStates.on_going),
    )

    if state == dms_models.GraphQLApplicationStates.draft:
        _notify_parsing_error(parsing_error.errors, application_scalar_id)
    elif state == dms_models.GraphQLApplicationStates.accepted:
        dms_subscription_emails.send_pre_subscription_from_dms_error_email_to_beneficiary(
            parsing_error.user_email,
            parsing_error.errors.get("postal_code"),
            parsing_error.errors.get("id_piece_number"),
        )

    return _create_parsing_error_fraud_check(user, application_number, state, parsing_error)


def _create_parsing_error_fraud_check(
    user: users_models.User,
    application_number: int,
    state: dms_models.GraphQLApplicationStates,
    parsing_error: subscription_exceptions.DMSParsingError,
) -> fraud_models.BeneficiaryFraudCheck:
    fraud_check = fraud_dms_api.get_or_create_fraud_check(user, application_number)

    errors = ",".join([f"'{key}' ({value})" for key, value in sorted(parsing_error.errors.items())])
    fraud_check.reason = f"Erreur dans les données soumises dans le dossier DMS : {errors}"
    fraud_check.reasonCodes = [fraud_models.FraudReasonCode.ERROR_IN_DATA]  # type: ignore [list-item]
    fraud_check.resultContent = parsing_error.result_content.dict()

    if state == dms_models.GraphQLApplicationStates.draft:
        status = fraud_models.FraudCheckStatus.STARTED
    elif state == dms_models.GraphQLApplicationStates.on_going:
        status = fraud_models.FraudCheckStatus.PENDING
    elif state == dms_models.GraphQLApplicationStates.accepted:
        status = fraud_models.FraudCheckStatus.ERROR
    elif state == dms_models.GraphQLApplicationStates.refused:
        status = fraud_models.FraudCheckStatus.KO
    elif state == dms_models.GraphQLApplicationStates.without_continuation:
        status = fraud_models.FraudCheckStatus.CANCELED
    else:
        status = fraud_models.FraudCheckStatus.ERROR

    fraud_check.status = status  # type: ignore [assignment]

    pcapi_repository.repository.save(fraud_check)

    return fraud_check


def _process_user_not_found_error(
    email: str,
    application_number: int,
    procedure_id: int,
    state: dms_models.GraphQLApplicationStates,
    application_scalar_id: str,
) -> None:
    dms_repository.create_orphan_dms_application_if_not_exists(
        application_number=application_number, procedure_id=procedure_id, email=email
    )
    if state == dms_models.GraphQLApplicationStates.draft:
        dms_connector_api.DMSGraphQLClient().send_user_message(
            application_scalar_id,
            settings.DMS_INSTRUCTOR_ID,
            subscription_messages.DMS_ERROR_MESSAGE_USER_NOT_FOUND,
        )
    elif state == dms_models.GraphQLApplicationStates.accepted:
        dms_subscription_emails.send_create_account_after_dms_email(email)


def _process_accepted_application(user: users_models.User, result_content: fraud_models.DMSContent) -> None:
    try:
        fraud_check = fraud_api.on_dms_fraud_result(user, result_content)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error on dms fraud check result: %s", exc)
        return

    if fraud_check.status != fraud_models.FraudCheckStatus.OK:
        _handle_validation_errors(user, fraud_check.reasonCodes, result_content)  # type: ignore [arg-type]
        subscription_api.update_user_birth_date(user, result_content.get_birth_date())
        return

    fraud_api.create_honor_statement_fraud_check(
        user, "honor statement contained in DMS application", fraud_check.eligibilityType  # type: ignore [arg-type]
    )
    try:
        has_completed_all_steps = subscription_api.on_successful_application(user=user, source_data=result_content)
    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "[DMS] Could not save application %s - Procedure %s",
            result_content.application_number,
            result_content.procedure_id,
        )
        return

    logger.info(
        "[DMS] Successfully imported accepted DMS application %s - Procedure %s",
        result_content.application_number,
        result_content.procedure_id,
    )

    if not has_completed_all_steps:
        dms_subscription_emails.send_complete_subscription_after_dms_email(user.email)


def _handle_validation_errors(
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
        "[DMS] Rejected application %s because of '%s' - Procedure %s",
        dms_content.application_number,
        reason,
        dms_content.procedure_id,
        extra={"user_id": user.id},
    )
