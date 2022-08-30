import datetime
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
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
import pcapi.core.subscription.api as subscription_api
from pcapi.core.subscription.dms import models as dms_types
from pcapi.core.users import external as users_external
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users.repository import find_user_by_email
import pcapi.repository as pcapi_repository
from pcapi.repository import repository

from . import repository as dms_repository


logger = logging.getLogger(__name__)


def get_dms_subscription_item_status(
    user: users_models.User,
    eligibility: users_models.EligibilityType | None,
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


def try_dms_orphan_adoption(user: users_models.User) -> None:
    dms_orphan = fraud_models.OrphanDmsApplication.query.filter_by(email=user.email).first()
    if not dms_orphan:
        return

    dms_application = dms_connector_api.DMSGraphQLClient().get_single_application_details(dms_orphan.application_id)
    fraud_check = handle_dms_application(dms_application)

    if fraud_check is not None:
        pcapi_repository.repository.delete(dms_orphan)


def _is_fraud_check_up_to_date(
    fraud_check: fraud_models.BeneficiaryFraudCheck, new_content: fraud_models.DMSContent
) -> bool:
    if not fraud_check.resultContent:
        return False

    fraud_check_content = typing.cast(fraud_models.DMSContent, fraud_check.source_data())
    return new_content.latest_modification_datetime == fraud_check_content.get_latest_modification_datetime()


def _update_fraud_check_with_new_content(
    fraud_check: fraud_models.BeneficiaryFraudCheck, new_content: fraud_models.DMSContent
) -> None:
    fraud_check.resultContent = new_content.dict()
    new_eligibility = fraud_api.decide_eligibility(
        fraud_check.user, new_content.get_birth_date(), new_content.get_registration_datetime()
    )
    if new_eligibility != fraud_check.eligibilityType:
        logger.warning("[DMS] User changed the eligibility in application %s", fraud_check.thirdPartyId)
        fraud_check.eligibilityType = new_eligibility


def _compute_birth_date_error_details(
    fraud_check: fraud_models.BeneficiaryFraudCheck, application_content: fraud_models.DMSContent
) -> dms_types.DmsFieldErrorDetails | None:
    if fraud_check.eligibilityType is not None:
        return None

    birth_date = application_content.get_birth_date()

    return dms_types.DmsFieldErrorDetails(
        key=dms_types.DmsFieldErrorKeyEnum.birth_date,
        value=birth_date.isoformat() if birth_date else None,
    )


def handle_dms_application(
    dms_application: dms_models.DmsApplicationResponse,
) -> fraud_models.BeneficiaryFraudCheck | None:
    application_number = dms_application.number
    user_email = users_utils.sanitize_email(dms_application.profile.email)
    application_scalar_id = dms_application.id
    state = dms_application.state
    procedure_number = dms_application.procedure.number

    log_extra_data = {
        "application_number": application_number,
        "application_scalar_id": application_scalar_id,
        "procedure_number": procedure_number,
        "user_email": user_email,
        "dms_state": state,
    }

    user = find_user_by_email(user_email)
    if not user:
        logger.info("[DMS] User not found for application", extra=log_extra_data)
        _process_user_not_found_error(
            user_email,
            application_number,
            procedure_number,
            state,
            application_scalar_id,
            latest_modification_datetime=dms_application.latest_modification_datetime,
        )
        return None

    application_content, field_errors = dms_serializer.parse_beneficiary_information_graphql(dms_application)
    if not field_errors:
        core_logging.log_for_supervision(
            logger=logger,
            log_level=logging.INFO,
            log_message="Successfully parsed DMS application",
            extra=log_extra_data,
        )
    logger.info("[DMS] Application received with state %s", state, extra=log_extra_data)

    fraud_check = fraud_dms_api.get_fraud_check(user, application_number)
    if fraud_check is None:
        fraud_check = fraud_dms_api.create_fraud_check(user, application_number, application_content)
    else:
        if _is_fraud_check_up_to_date(fraud_check, application_content):
            logger.info("[DMS] FraudCheck already up to date", extra=log_extra_data)
            return fraud_check

        if fraud_check.status == fraud_models.FraudCheckStatus.OK:
            logger.warning("[DMS] Skipping because FraudCheck already has OK status", extra=log_extra_data)
            return fraud_check

        _update_fraud_check_with_new_content(fraud_check, application_content)

    birth_date_error = _compute_birth_date_error_details(fraud_check, application_content)

    if state == dms_models.GraphQLApplicationStates.draft:
        _process_in_progress_application(
            user,
            fraud_check,
            fraud_models.FraudCheckStatus.STARTED,
            application_scalar_id,
            field_errors,
            birth_date_error,
            is_application_updatable=True,
        )

    elif state == dms_models.GraphQLApplicationStates.on_going:
        _process_in_progress_application(
            user,
            fraud_check,
            fraud_models.FraudCheckStatus.PENDING,
            application_scalar_id,
            field_errors,
            birth_date_error,
            is_application_updatable=False,
        )

    elif state == dms_models.GraphQLApplicationStates.accepted:
        _process_accepted_application(user, fraud_check, field_errors)

    elif state == dms_models.GraphQLApplicationStates.refused:
        fraud_check.status = fraud_models.FraudCheckStatus.KO
        fraud_check.reasonCodes = [fraud_models.FraudReasonCode.REFUSED_BY_OPERATOR]  # type: ignore [list-item]
        subscription_messages.on_dms_application_refused(user)

    elif state == dms_models.GraphQLApplicationStates.without_continuation:
        fraud_check.status = fraud_models.FraudCheckStatus.CANCELED

    pcapi_repository.repository.save(fraud_check)
    return fraud_check


def _send_field_error_dms_email(field_errors: list[dms_types.DmsFieldErrorDetails], application_scalar_id: str) -> None:
    client = dms_connector_api.DMSGraphQLClient()
    client.send_user_message(
        application_scalar_id,
        settings.DMS_INSTRUCTOR_ID,
        subscription_messages.build_field_errors_user_message(field_errors),
    )


def _send_eligibility_error_dms_email(
    formatted_birth_date: str | None,
    application_scalar_id: str,
    third_party_id: str,
) -> None:
    if not formatted_birth_date:
        logger.warning(
            "[DMS] No birth date found when trying to notify eligibility error",
            extra={"third_party_id": third_party_id},
        )
        return
    client = dms_connector_api.DMSGraphQLClient()
    client.send_user_message(
        application_scalar_id,
        settings.DMS_INSTRUCTOR_ID,
        subscription_messages.build_dms_error_message_user_not_eligible(formatted_birth_date),
    )


def _process_in_progress_application(
    user: users_models.User,
    fraud_check: fraud_models.BeneficiaryFraudCheck,
    fraud_check_status: fraud_models.FraudCheckStatus,
    application_scalar_id: str,
    field_errors: list[dms_types.DmsFieldErrorDetails],
    birth_date_error: dms_types.DmsFieldErrorDetails | None,
    is_application_updatable: bool,
) -> None:
    if not field_errors and birth_date_error is None:
        subscription_messages.on_dms_application_received(user)
        fraud_check.status = fraud_check_status
        return

    errors = []
    reason_codes = []

    if birth_date_error is not None:
        if is_application_updatable:
            _send_eligibility_error_dms_email(birth_date_error.value, application_scalar_id, fraud_check.thirdPartyId)  # type: ignore [arg-type]
        reason_codes.append(fraud_models.FraudReasonCode.AGE_NOT_VALID)
        errors.append(birth_date_error)

    if field_errors:
        if is_application_updatable:
            _send_field_error_dms_email(field_errors, application_scalar_id)
        reason_codes.append(fraud_models.FraudReasonCode.ERROR_IN_DATA)
        errors.extend(field_errors)

    logger.warning(
        "[DMS] Errors found in DMS application",
        extra={"third_party_id": fraud_check.thirdPartyId, "errors": errors, "status": fraud_check_status},
    )
    subscription_messages.on_dms_application_field_errors(
        user, errors, is_application_updatable=is_application_updatable
    )
    _update_fraud_check_with_field_errors(
        fraud_check, errors, fraud_check_status=fraud_check_status, reason_codes=reason_codes
    )


def _update_fraud_check_with_field_errors(
    fraud_check: fraud_models.BeneficiaryFraudCheck,
    field_errors: list[dms_types.DmsFieldErrorDetails],
    fraud_check_status: fraud_models.FraudCheckStatus,
    reason_codes: list[fraud_models.FraudReasonCode],
) -> None:
    errors = ",".join([f"'{field_error.key.value}' ({field_error.value})" for field_error in field_errors])
    fraud_check.reason = f"Erreur dans les données soumises dans le dossier DMS : {errors}"
    fraud_check.reasonCodes = reason_codes  # type: ignore [assignment]
    fraud_check.status = fraud_check_status

    pcapi_repository.repository.save(fraud_check)


def _create_profile_completion_fraud_check_from_dms(
    user: users_models.User,
    eligibility: users_models.EligibilityType | None,
    content: fraud_models.DMSContent,
    application_id: str,
) -> None:
    """Creates a PROFILE_COMPLETION fraud check from a DMS content, provided that all necessary fields are filled."""
    activity = content.get_activity()
    city = content.get_city()
    first_name = content.get_first_name()
    last_name = content.get_last_name()
    postal_code = content.get_postal_code()
    if all(elem is not None for elem in [activity, city, first_name, last_name, postal_code]):
        fraud_api.create_profile_completion_fraud_check(
            user,
            eligibility,
            fraud_models.ProfileCompletionContent(
                activity=activity,
                city=city,
                first_name=first_name,
                last_name=last_name,
                origin=f"Completed in DMS application {application_id}",
                postalCode=content.postal_code,
            ),
        )


def _process_user_not_found_error(
    email: str,
    application_number: int,
    procedure_number: int,
    state: dms_models.GraphQLApplicationStates,
    application_scalar_id: str,
    latest_modification_datetime: datetime.datetime,
) -> None:
    orphan = dms_repository.get_orphan_dms_application_by_application_id(application_number)
    if orphan:
        if (
            not orphan.latest_modification_datetime
            or orphan.latest_modification_datetime < latest_modification_datetime
        ):
            orphan.latest_modification_datetime = latest_modification_datetime
            repository.save(orphan)
        else:
            # Application was already processed
            return
    else:
        # Create new orphan
        dms_repository.create_orphan_dms_application(
            application_number=application_number,
            procedure_number=procedure_number,
            latest_modification_datetime=latest_modification_datetime,
            email=email,
        )

    if state == dms_models.GraphQLApplicationStates.draft:
        dms_connector_api.DMSGraphQLClient().send_user_message(
            application_scalar_id,
            settings.DMS_INSTRUCTOR_ID,
            subscription_messages.DMS_ERROR_MESSAGE_USER_NOT_FOUND,
        )
    elif state == dms_models.GraphQLApplicationStates.accepted:
        dms_subscription_emails.send_create_account_after_dms_email(email)


def _process_accepted_application(
    user: users_models.User,
    fraud_check: fraud_models.BeneficiaryFraudCheck,
    field_errors: list[dms_types.DmsFieldErrorDetails],
) -> None:
    if field_errors:
        subscription_messages.on_dms_application_field_errors(user, field_errors, is_application_updatable=False)
        dms_subscription_emails.send_pre_subscription_from_dms_error_email_to_beneficiary(
            user.email,
            field_errors,
        )
        _update_fraud_check_with_field_errors(
            fraud_check, field_errors, fraud_models.FraudCheckStatus.ERROR, [fraud_models.FraudReasonCode.ERROR_IN_DATA]
        )
        return

    dms_content: fraud_models.DMSContent = fraud_check.source_data()  # type: ignore [assignment]

    try:
        fraud_api.on_dms_fraud_result(user, fraud_check)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Error on dms fraud check result: %s", exc)
        return

    subscription_api.update_user_birth_date_if_not_beneficiary(user, dms_content.get_birth_date())

    if fraud_check.status != fraud_models.FraudCheckStatus.OK:
        _handle_validation_errors(user, fraud_check.reasonCodes, dms_content)  # type: ignore [arg-type]
        return

    fraud_api.create_honor_statement_fraud_check(
        user, "honor statement contained in DMS application", fraud_check.eligibilityType
    )
    _create_profile_completion_fraud_check_from_dms(
        user, fraud_check.eligibilityType, dms_content, application_id=fraud_check.thirdPartyId  # type: ignore [arg-type]
    )

    try:
        has_completed_all_steps = subscription_api.activate_beneficiary_if_no_missing_step(user=user)
    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "[DMS] Could not save application %s - Procedure %s",
            dms_content.application_number,
            dms_content.procedure_number,
        )
        return

    logger.info(
        "[DMS] Successfully imported accepted DMS application %s - Procedure %s",
        dms_content.application_number,
        dms_content.procedure_number,
    )

    if not has_completed_all_steps:
        dms_subscription_emails.send_complete_subscription_after_dms_email(user.email)
        users_external.update_external_user(user)


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
        dms_content.procedure_number,
        extra={"user_id": user.id},
    )
