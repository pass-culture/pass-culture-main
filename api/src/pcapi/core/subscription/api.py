import datetime
import logging
import typing

from sqlalchemy import exc as sqlalchemy_exceptions

import pcapi.core.finance.conf as finance_conf
import pcapi.core.finance.exceptions as finance_exceptions
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.common.models as common_fraud_models
import pcapi.core.fraud.models as fraud_models
import pcapi.core.fraud.repository as fraud_repository
import pcapi.core.fraud.ubble.constants as ubble_constants
import pcapi.core.mails.transactional as transactional_mails
import pcapi.utils.postal_code as postal_code_utils
import pcapi.utils.repository as pcapi_repository
from pcapi import settings
from pcapi.core.external import batch
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.finance import deposit_api
from pcapi.core.subscription import machines as subscription_machines
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.subscription.educonnect import api as educonnect_subscription_api
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import eligibility_api
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users import young_status as young_status_module
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.workers import apps_flyer_job

from . import exceptions
from . import models


logger = logging.getLogger(__name__)


FREE_ELIGIBILITY_DEPOSIT_SOURCE = "complétion du profil"


def activate_beneficiary_if_no_missing_step(user: users_models.User) -> bool:
    user_id = user.id  # keep id to avoid PendingRollbackError when falling into IntegrityError

    # ensure the FOR UPDATE lock is freed if anything arises
    with pcapi_repository.transaction():
        user = (
            db.session.query(users_models.User)
            .filter(users_models.User.id == user_id)
            .populate_existing()
            .with_for_update()
            .one()
        )

        subscription_state_machine = subscription_machines.create_state_machine_to_current_state(user)
        if (
            subscription_state_machine.state
            != subscription_machines.SubscriptionStates.SUBSCRIPTION_COMPLETED_BUT_NOT_BENEFICIARY_YET
        ):
            return False

        eligibility_to_activate = eligibility_api.get_pre_decree_or_current_eligibility(user)
        if eligibility_to_activate is None:
            return False

        should_have_checked_identity = subscription_state_machine.eligibility != users_models.EligibilityType.FREE
        if should_have_checked_identity:
            identity_fraud_check = subscription_state_machine.identity_fraud_check
            if not identity_fraud_check or not identity_fraud_check.resultContent:
                return False

            duplicate_beneficiary = fraud_api.get_duplicate_beneficiary(identity_fraud_check)
            if duplicate_beneficiary:
                fraud_api.invalidate_fraud_check_for_duplicate_user(identity_fraud_check, duplicate_beneficiary.id)
                return False

            source_data = typing.cast(common_fraud_models.IdentityCheckContent, identity_fraud_check.source_data())
            try:
                users_api.update_user_information_from_external_source(user, source_data)
            except sqlalchemy_exceptions.IntegrityError as e:
                logger.warning("The user information could not be updated", extra={"exc": str(e), "user": user_id})
                return False

            deposit_source = identity_fraud_check.get_detailed_source()
        else:
            deposit_source = FREE_ELIGIBILITY_DEPOSIT_SOURCE

        try:
            activate_beneficiary_for_eligibility(user, deposit_source, eligibility_to_activate)
        except (finance_exceptions.DepositTypeAlreadyGrantedException, finance_exceptions.UserHasAlreadyActiveDeposit):
            # this error may happen on identity provider concurrent requests
            logger.info("A deposit already exists for user %s", user_id)
            return False

        return True


def activate_beneficiary_for_eligibility(
    user: users_models.User,
    deposit_source: str,
    eligibility: users_models.EligibilityType,
) -> users_models.User:
    eligibility_api.check_eligibility_is_applicable_to_user(eligibility, user)

    with pcapi_repository.transaction():
        deposit = deposit_api.upsert_deposit(
            user,
            deposit_source=deposit_source,
            eligibility=eligibility,
        )
        activated_eligibility = eligibility_api.get_activated_eligibility(deposit.type)
        eligibility_api.add_eligibility_role(user, activated_eligibility)
    logger.info("Activated beneficiary and created deposit", extra={"user": user.id, "source": deposit.source})

    transactional_mails.send_accepted_as_beneficiary_email(user=user)
    external_attributes_api.update_external_user(user)
    batch.track_deposit_activated_event(user.id, deposit)

    if "apps_flyer" in user.externalIds:
        apps_flyer_job.log_user_becomes_beneficiary_event_job.delay(user.id)

    return user


def has_completed_profile_for_given_eligibility(
    user: users_models.User, eligibility: users_models.EligibilityType
) -> bool:
    if fraud_repository.get_completed_profile_check(user, eligibility) is not None:
        return True
    if fraud_repository.get_filled_dms_fraud_check(user, eligibility) is not None:
        return True
    return False


def has_completed_underage_profile(user: users_models.User) -> bool:
    if fraud_repository.get_completed_underage_profile_check(user) is not None:
        return True
    if fraud_repository.get_filled_underage_dms_fraud_check(user) is not None:
        return True
    return False


def get_declared_names(user: users_models.User) -> tuple[str, str] | None:
    profile_completion_check = fraud_repository.get_completed_profile_check(user, user.eligibility)
    if profile_completion_check and profile_completion_check.resultContent:
        profile_data = typing.cast(fraud_models.ProfileCompletionContent, profile_completion_check.source_data())
        return profile_data.first_name, profile_data.last_name

    dms_filled_check = fraud_repository.get_filled_dms_fraud_check(user, user.eligibility)
    if dms_filled_check:
        dms_data = dms_filled_check.source_data()
        return dms_data.first_name, dms_data.last_name

    return None


def get_email_validation_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    if user.isEmailValidated:
        status = models.SubscriptionItemStatus.OK
    else:
        if eligibility_api.is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.EMAIL_VALIDATION, status=status)


def get_phone_validation_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    should_fill_phone = eligibility_api.is_18_or_above_eligibility(eligibility, user.age)
    if not should_fill_phone:
        return models.SubscriptionItem(
            type=models.SubscriptionStep.PHONE_VALIDATION, status=models.SubscriptionItemStatus.NOT_APPLICABLE
        )

    if user.is_phone_validated:
        status = models.SubscriptionItemStatus.OK
    elif user.is_phone_validation_skipped:
        status = models.SubscriptionItemStatus.SKIPPED
    elif fraud_repository.has_failed_phone_validation(user):
        status = models.SubscriptionItemStatus.KO
    elif eligibility_api.is_eligibility_activable(user, eligibility):
        has_user_filled_phone = user.phoneNumber is not None
        if not FeatureToggle.ENABLE_PHONE_VALIDATION.is_active() and has_user_filled_phone:
            status = models.SubscriptionItemStatus.OK
        else:
            status = models.SubscriptionItemStatus.TODO
    else:
        status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.PHONE_VALIDATION, status=status)


def get_profile_completion_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType
) -> models.SubscriptionItem:
    if has_completed_profile_for_given_eligibility(user, eligibility):
        status = models.SubscriptionItemStatus.OK
    elif eligibility_api.is_eligibility_activable(user, eligibility):
        status = models.SubscriptionItemStatus.TODO
    else:
        status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.PROFILE_COMPLETION, status=status)


def get_profile_data(user: users_models.User) -> fraud_models.ProfileCompletionContent | None:
    profile_completion_check = fraud_repository.get_latest_completed_profile_check(user)
    if profile_completion_check and profile_completion_check.resultContent:
        return typing.cast(fraud_models.ProfileCompletionContent, profile_completion_check.source_data())

    return None


def get_identity_check_fraud_status(
    user: users_models.User,
    eligibility: users_models.EligibilityType | None,
    fraud_check: fraud_models.BeneficiaryFraudCheck | None,
) -> models.SubscriptionItemStatus:
    """
    eligibility may be the current user.eligibility or a specific eligibility.
    The result relies on the FraudChecks made with the 3 current identity providers (DMS, Ubble and Educonnect)
    and with the legacy provider (Jouve)
    """
    if eligibility is None:
        return models.SubscriptionItemStatus.VOID

    if not fraud_check:
        if eligibility_api.is_eligibility_activable(user, eligibility):
            return models.SubscriptionItemStatus.TODO
        return models.SubscriptionItemStatus.VOID

    if fraud_check.status == fraud_models.FraudCheckStatus.OK:
        return models.SubscriptionItemStatus.OK

    if fraud_check.status == fraud_models.FraudCheckStatus.KO:
        return models.SubscriptionItemStatus.KO

    if fraud_check.status == fraud_models.FraudCheckStatus.SUSPICIOUS:
        return models.SubscriptionItemStatus.SUSPICIOUS

    if fraud_check.status == fraud_models.FraudCheckStatus.PENDING:
        return models.SubscriptionItemStatus.PENDING

    if fraud_check.status == fraud_models.FraudCheckStatus.STARTED:
        if fraud_check.type == fraud_models.FraudCheckType.DMS:
            return models.SubscriptionItemStatus.PENDING
        return models.SubscriptionItemStatus.TODO

    return models.SubscriptionItemStatus.VOID


def can_retry_identity_fraud_check(identity_fraud_check: fraud_models.BeneficiaryFraudCheck) -> bool:
    match identity_fraud_check.type:
        case fraud_models.FraudCheckType.EDUCONNECT:
            return True

        case fraud_models.FraudCheckType.UBBLE:
            if not identity_fraud_check.reasonCodes or not all(
                code in ubble_constants.RESTARTABLE_FRAUD_CHECK_REASON_CODES
                for code in identity_fraud_check.reasonCodes
            ):
                return False
            # user.beneficiaryFraudChecks may have been joinedloaded before to reduce the number of db requests
            ubble_attempts_count = len(
                [
                    fraud_check
                    for fraud_check in identity_fraud_check.user.beneficiaryFraudChecks
                    if fraud_check.type == fraud_models.FraudCheckType.UBBLE
                    and fraud_check.eligibilityType == identity_fraud_check.eligibilityType
                    and fraud_check.status
                    not in (fraud_models.FraudCheckStatus.CANCELED, fraud_models.FraudCheckStatus.STARTED)
                ]
            )

            return ubble_attempts_count < ubble_constants.MAX_UBBLE_RETRIES
    return False


def should_retry_identity_check(user_subscription_state: models.UserSubscriptionState) -> bool:
    fraud_check = user_subscription_state.identity_fraud_check
    if not fraud_check:
        return False

    if (
        user_subscription_state.next_step == models.SubscriptionStep.IDENTITY_CHECK
        and _has_subscription_issues(user_subscription_state)
        and can_retry_identity_fraud_check(fraud_check)
    ):
        return True
    return False


def get_identity_check_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    id_check = fraud_repository.get_relevant_identity_fraud_check(user, eligibility)
    status = get_identity_check_fraud_status(user, eligibility, id_check)
    return models.SubscriptionItem(type=models.SubscriptionStep.IDENTITY_CHECK, status=status)


def get_honor_statement_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    if fraud_repository.get_completed_honor_statement(user, eligibility):  # type: ignore[arg-type]
        status = models.SubscriptionItemStatus.OK
    else:
        if eligibility_api.is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.HONOR_STATEMENT, status=status)


def get_user_subscription_state(user: users_models.User) -> subscription_models.UserSubscriptionState:
    subscription_state_machine = subscription_machines.create_state_machine_to_current_state(user)
    subscription_state = subscription_state_machine.state
    match subscription_state:
        case subscription_machines.SubscriptionStates.EMAIL_VALIDATION:
            return subscription_models.UserSubscriptionState(
                fraud_status=models.SubscriptionItemStatus.TODO,
                next_step=models.SubscriptionStep.EMAIL_VALIDATION,
                young_status=young_status_module.Eligible(
                    subscription_status=young_status_module.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION
                ),
            )
        case subscription_machines.SubscriptionStates.BENEFICIARY:
            return subscription_models.UserSubscriptionState(
                fraud_status=models.SubscriptionItemStatus.OK,
                next_step=None,
                young_status=young_status_module.Beneficiary(),
            )
        case subscription_machines.SubscriptionStates.EX_BENEFICIARY:
            return subscription_models.UserSubscriptionState(
                fraud_status=models.SubscriptionItemStatus.OK,
                next_step=None,
                young_status=young_status_module.ExBeneficiary(),
            )
        case subscription_machines.SubscriptionStates.ADMIN_KO_REVIEW:
            return subscription_models.UserSubscriptionState(
                fraud_status=models.SubscriptionItemStatus.KO,
                next_step=None,
                young_status=young_status_module.NonEligible(),
                subscription_message=subscription_messages.get_generic_ko_message(user.id),
            )
        case subscription_machines.SubscriptionStates.NOT_ELIGIBLE:
            return subscription_models.UserSubscriptionState(
                fraud_status=models.SubscriptionItemStatus.VOID,
                next_step=None,
                young_status=young_status_module.NonEligible(),
            )
        case subscription_machines.SubscriptionStates.FAILED_PHONE_VALIDATION:
            return subscription_models.UserSubscriptionState(
                fraud_status=models.SubscriptionItemStatus.KO,
                next_step=models.SubscriptionStep.PHONE_VALIDATION,
                young_status=young_status_module.Eligible(
                    subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_ISSUES
                ),
            )
        case subscription_machines.SubscriptionStates.PHONE_VALIDATION:
            return subscription_models.UserSubscriptionState(
                fraud_status=models.SubscriptionItemStatus.TODO,
                next_step=models.SubscriptionStep.PHONE_VALIDATION,
                young_status=young_status_module.Eligible(
                    subscription_status=young_status_module.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION
                ),
            )
        case subscription_machines.SubscriptionStates.PROFILE_COMPLETION:
            return subscription_models.UserSubscriptionState(
                fraud_status=models.SubscriptionItemStatus.TODO,
                next_step=models.SubscriptionStep.PROFILE_COMPLETION,
                young_status=young_status_module.Eligible(
                    subscription_status=young_status_module.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION
                ),
            )
        case subscription_machines.SubscriptionStates.FAILED_IDENTITY_CHECK:
            identity_check_fraud_status, _, subscription_message = _get_identity_check_status(
                subscription_state_machine.identity_fraud_check, user
            )
            return subscription_models.UserSubscriptionState(
                identity_fraud_check=subscription_state_machine.identity_fraud_check,
                fraud_status=identity_check_fraud_status,
                subscription_message=subscription_message,
                next_step=None,
                young_status=young_status_module.Eligible(
                    subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_ISSUES
                ),
            )
        case subscription_machines.SubscriptionStates.IDENTITY_CHECK_RETRY:
            _, next_step, subscription_message = _get_identity_check_status(
                subscription_state_machine.identity_fraud_check, user
            )
            return subscription_models.UserSubscriptionState(
                identity_fraud_check=subscription_state_machine.identity_fraud_check,
                fraud_status=models.SubscriptionItemStatus.TODO,
                subscription_message=subscription_message,
                next_step=next_step,
                young_status=young_status_module.Eligible(
                    subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_ISSUES
                ),
            )
        case subscription_machines.SubscriptionStates.IDENTITY_CHECK:
            _, next_step, subscription_message = _get_identity_check_status(
                subscription_state_machine.identity_fraud_check, user
            )
            return subscription_models.UserSubscriptionState(
                identity_fraud_check=subscription_state_machine.identity_fraud_check,
                fraud_status=models.SubscriptionItemStatus.TODO,
                subscription_message=subscription_message,
                next_step=next_step,
                young_status=young_status_module.Eligible(
                    subscription_status=young_status_module.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION
                ),
            )
        case subscription_machines.SubscriptionStates.HONOR_STATEMENT:
            if not subscription_state_machine.identity_fraud_check_status:
                raise ValueError(
                    f"Identity fraud check status should not be None for {user = } at {subscription_state = }"
                )
            return subscription_models.UserSubscriptionState(
                identity_fraud_check=subscription_state_machine.identity_fraud_check,
                next_step=models.SubscriptionStep.HONOR_STATEMENT,
                fraud_status=subscription_state_machine.identity_fraud_check_status,
                subscription_message=None,  # The user needs no message to complete honor statement
                young_status=young_status_module.Eligible(
                    subscription_status=young_status_module.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION
                ),
            )
        case subscription_machines.SubscriptionStates.WAITING_FOR_IDENTITY_CHECK:
            _, _, subscription_message = _get_identity_check_status(
                subscription_state_machine.identity_fraud_check, user
            )
            return subscription_models.UserSubscriptionState(
                identity_fraud_check=subscription_state_machine.identity_fraud_check,
                fraud_status=models.SubscriptionItemStatus.PENDING,
                subscription_message=subscription_message,
                next_step=None,
                young_status=young_status_module.Eligible(
                    subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_PENDING
                ),
            )
        case subscription_machines.SubscriptionStates.WAITING_FOR_MANUAL_REVIEW:
            if not subscription_state_machine.identity_fraud_check_status:
                raise ValueError(
                    f"Identity fraud check status should not be None for {user = } at {subscription_state = }"
                )
            return subscription_models.UserSubscriptionState(
                identity_fraud_check=subscription_state_machine.identity_fraud_check,
                is_activable=False,
                fraud_status=subscription_state_machine.identity_fraud_check_status,
                subscription_message=None,
                next_step=None,
                young_status=young_status_module.Eligible(
                    subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_PENDING
                ),
            )
        case subscription_machines.SubscriptionStates.SUBSCRIPTION_COMPLETED_BUT_NOT_BENEFICIARY_YET:
            return subscription_models.UserSubscriptionState(
                identity_fraud_check=subscription_state_machine.identity_fraud_check,
                is_activable=True,
                fraud_status=models.SubscriptionItemStatus.OK,
                subscription_message=None,
                next_step=None,
                young_status=young_status_module.Eligible(
                    subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_PENDING
                ),
            )
        case _:
            raise ValueError(f"{user = } has an unhandled {subscription_state_machine.state = }")


def _get_identity_check_status(
    identity_fraud_check: fraud_models.BeneficiaryFraudCheck | None, user: users_models.User
) -> tuple[models.SubscriptionItemStatus, models.SubscriptionStep, models.SubscriptionMessage | None]:
    identity_check_fraud_status = get_identity_check_fraud_status(user, user.eligibility, identity_fraud_check)
    allowed_identity_check_methods = get_allowed_identity_check_methods(user)
    next_step = (
        models.SubscriptionStep.IDENTITY_CHECK
        if len(allowed_identity_check_methods) > 0
        else models.SubscriptionStep.MAINTENANCE
    )
    subscription_message = (
        _get_subscription_message(identity_fraud_check)
        if len(allowed_identity_check_methods) > 0
        else subscription_messages.MAINTENANCE_PAGE_MESSAGE
    )
    return identity_check_fraud_status, next_step, subscription_message


def requires_manual_review_before_activation(
    user: users_models.User, identity_fraud_check: fraud_models.BeneficiaryFraudCheck
) -> bool:
    return (
        identity_fraud_check.type == fraud_models.FraudCheckType.DMS
        and identity_fraud_check.status == fraud_models.FraudCheckStatus.OK
        and not eligibility_api.get_eligibility_at_date(
            user.birth_date, identity_fraud_check.get_min_date_between_creation_and_registration(), user.departementCode
        )
    )


def complete_profile(
    user: users_models.User,
    *,
    address: str,
    city: str,
    postal_code: str,
    activity: users_models.ActivityEnum,
    first_name: str,
    last_name: str,
    school_type: users_models.SchoolTypeEnum | None = None,
) -> None:
    if postal_code in postal_code_utils.INELIGIBLE_POSTAL_CODES:
        raise exceptions.IneligiblePostalCodeException()

    update_payload: dict = {
        "address": address,
        "city": city,
        "postalCode": postal_code,
        "departementCode": postal_code_utils.PostalCode(postal_code).get_departement_code(),
        "activity": activity.value,
        "schoolType": school_type,
    }

    if not user.firstName:
        update_payload["firstName"] = first_name

    if not user.lastName:
        update_payload["lastName"] = last_name

    with pcapi_repository.transaction():
        db.session.query(users_models.User).filter(users_models.User.id == user.id).update(update_payload)

    fraud_api.create_profile_completion_fraud_check(
        user,
        user.eligibility,
        fraud_models.ProfileCompletionContent(
            activity=activity,
            address=address,
            city=city,
            first_name=first_name,
            last_name=last_name,
            origin="Completed in application step",
            postal_code=postal_code,
            school_type=school_type,
        ),
    )
    logger.info("User completed profile step", extra={"user": user.id})


def get_allowed_identity_check_methods(user: users_models.User) -> list[models.IdentityCheckMethod]:
    allowed_methods = []

    is_educonnect_allowed = user.is_underage_eligible
    if is_educonnect_allowed and FeatureToggle.ENABLE_EDUCONNECT_AUTHENTICATION.is_active():
        allowed_methods.append(models.IdentityCheckMethod.EDUCONNECT)

    if FeatureToggle.ENABLE_UBBLE.is_active() and _is_ubble_allowed_if_subscription_overflow(user):
        allowed_methods.append(models.IdentityCheckMethod.UBBLE)

    return allowed_methods


def _is_ubble_allowed_if_subscription_overflow(user: users_models.User) -> bool:
    if not FeatureToggle.ENABLE_UBBLE_SUBSCRIPTION_LIMITATION.is_active():
        return True

    if not user.birth_date:
        return False

    future_age = users_utils.get_age_at_date(
        user.birth_date,
        datetime.datetime.utcnow() + datetime.timedelta(days=settings.UBBLE_SUBSCRIPTION_LIMITATION_DAYS),  # type: ignore[arg-type]
        user.departementCode,
    )
    eligibility_ranges = users_constants.ELIGIBILITY_UNDERAGE_RANGE + [users_constants.ELIGIBILITY_AGE_18]
    eligibility_ranges = [age + 1 for age in eligibility_ranges]
    if future_age > user.age and future_age in eligibility_ranges:  # type: ignore[operator]
        return True

    return False


def get_maintenance_page_type(user: users_models.User) -> models.MaintenancePageType | None:
    allowed_identity_check_methods = get_allowed_identity_check_methods(user)
    if allowed_identity_check_methods or not user.age:
        return None

    if user.is_18_or_above_eligible and FeatureToggle.ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18.is_active():
        return models.MaintenancePageType.WITH_DMS

    if user.is_underage_eligible and FeatureToggle.ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE.is_active():
        return models.MaintenancePageType.WITH_DMS

    return models.MaintenancePageType.WITHOUT_DMS


DEPRECATED_UBBLE_PREFIX = "deprecated-"


def _update_fraud_check_eligibility_with_history(
    fraud_check: fraud_models.BeneficiaryFraudCheck, eligibility: users_models.EligibilityType
) -> fraud_models.BeneficiaryFraudCheck:
    # Update fraud check by creating a new one with the correct eligibility
    new_fraud_check = fraud_models.BeneficiaryFraudCheck(
        user=fraud_check.user,
        type=fraud_check.type,
        thirdPartyId=fraud_check.thirdPartyId,
        resultContent=fraud_check.resultContent,
        status=fraud_check.status,
        reason=fraud_check.reason,
        reasonCodes=fraud_check.reasonCodes,
        eligibilityType=eligibility,
    )
    # Cancel the old fraud check
    fraud_check.status = fraud_models.FraudCheckStatus.CANCELED
    reason_message = "Eligibility type changed by the identity provider"
    fraud_check.reason = (
        f"{fraud_check.reason} {fraud_api.FRAUD_RESULT_REASON_SEPARATOR} {reason_message}"
        if fraud_check.reason
        else reason_message
    )
    if fraud_check.reasonCodes is None:
        fraud_check.reasonCodes = []
    fraud_check.reasonCodes.append(fraud_models.FraudReasonCode.ELIGIBILITY_CHANGED)
    fraud_check.thirdPartyId = f"{DEPRECATED_UBBLE_PREFIX}{fraud_check.thirdPartyId}"

    pcapi_repository.save(fraud_check, new_fraud_check)

    return new_fraud_check


def get_id_provider_detected_eligibility(
    user: users_models.User, identity_content: common_fraud_models.IdentityCheckContent
) -> users_models.EligibilityType | None:
    return eligibility_api.decide_eligibility(
        user, identity_content.get_birth_date(), identity_content.get_registration_datetime()
    )


# TODO (Lixxday): use a proper BeneficiaryFraudCheck History model to track these kind of updates
def handle_eligibility_difference_between_declaration_and_identity_provider(
    user: users_models.User,
    fraud_check: fraud_models.BeneficiaryFraudCheck,
    identity_content: common_fraud_models.IdentityCheckContent | None = None,
) -> fraud_models.BeneficiaryFraudCheck:
    if identity_content is None:
        identity_content = fraud_check.source_data()

    declared_eligibility = fraud_check.eligibilityType
    id_provider_detected_eligibility = get_id_provider_detected_eligibility(user, identity_content)

    if declared_eligibility == id_provider_detected_eligibility or id_provider_detected_eligibility is None:
        return fraud_check

    new_fraud_check = _update_fraud_check_eligibility_with_history(fraud_check, id_provider_detected_eligibility)

    # Handle eligibility update for PROFILE_COMPLETION fraud check, if it exists
    profile_completion_fraud_check = (
        db.session.query(fraud_models.BeneficiaryFraudCheck)
        .filter(
            fraud_models.BeneficiaryFraudCheck.userId == user.id,
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.PROFILE_COMPLETION,
            fraud_models.BeneficiaryFraudCheck.eligibilityType == declared_eligibility,
        )
        .first()
    )
    if profile_completion_fraud_check:
        _update_fraud_check_eligibility_with_history(profile_completion_fraud_check, id_provider_detected_eligibility)

    # Handle eligibility update for HONOR_STATEMENT fraud check, if it exists
    honor_statement_fraud_check = (
        db.session.query(fraud_models.BeneficiaryFraudCheck)
        .filter(
            fraud_models.BeneficiaryFraudCheck.userId == user.id,
            fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.HONOR_STATEMENT,
            fraud_models.BeneficiaryFraudCheck.eligibilityType == declared_eligibility,
        )
        .first()
    )
    if honor_statement_fraud_check:
        _update_fraud_check_eligibility_with_history(honor_statement_fraud_check, id_provider_detected_eligibility)

    return new_fraud_check


def update_user_birth_date_if_not_beneficiary(user: users_models.User, birth_date: datetime.date | None) -> None:
    """Updates the user validated birth date based on data received from the identity provider
    so that the user is correctly redirected for the rest of the process.
    """
    if (
        birth_date
        and user.validatedBirthDate != birth_date
        and (eligibility_api.is_eligible_for_next_recredit_activation_steps(user) or not user.validatedBirthDate)
    ):
        user.validatedBirthDate = birth_date
        pcapi_repository.save(user)


def _get_subscription_message(
    fraud_check: fraud_models.BeneficiaryFraudCheck | None,
) -> models.SubscriptionMessage | None:
    """The subscription message is meant to help the user have information about the subscription status."""
    if not fraud_check:
        return None

    match fraud_check.type:
        case fraud_models.FraudCheckType.DMS:
            return dms_subscription_api.get_dms_subscription_message(fraud_check)
        case fraud_models.FraudCheckType.UBBLE:
            return ubble_subscription_api.get_ubble_subscription_message(fraud_check)
        case fraud_models.FraudCheckType.EDUCONNECT:
            return educonnect_subscription_api.get_educonnect_subscription_message(fraud_check)
        case _:
            return subscription_messages.get_generic_ko_message(fraud_check.user.id)


def initialize_identity_fraud_check(
    eligibility_type: users_models.EligibilityType | None,
    fraud_check_type: fraud_models.FraudCheckType,
    identity_content: common_fraud_models.IdentityCheckContent,
    third_party_id: str,
    user: users_models.User,
) -> fraud_models.BeneficiaryFraudCheck:
    """Create a fraud check for the user, with the identity information provided by the identity provider."""
    fraud_check = fraud_models.BeneficiaryFraudCheck(
        user=user,
        type=fraud_check_type,
        thirdPartyId=third_party_id,
        resultContent=identity_content.dict() if identity_content else None,
        status=fraud_models.FraudCheckStatus.STARTED,
        eligibilityType=eligibility_type,
    )
    pcapi_repository.save(fraud_check)
    batch.track_identity_check_started_event(user.id, fraud_check.type)
    return fraud_check


def get_subscription_steps_to_display(
    user: users_models.User, user_subscription_state: models.UserSubscriptionState
) -> list[models.SubscriptionStepDetails]:
    """
    return the list of steps to complete to subscribe to the pass Culture
    the steps are ordered
    """
    ordered_steps = _get_ordered_steps(user)
    return _get_steps_details(user, ordered_steps, user_subscription_state)


def _get_ordered_steps(user: users_models.User) -> list[models.SubscriptionStep]:
    ordered_steps = []
    should_fill_phone = user.is_18_or_above_eligible
    if should_fill_phone:
        ordered_steps.append(models.SubscriptionStep.PHONE_VALIDATION)
    ordered_steps.append(models.SubscriptionStep.PROFILE_COMPLETION)
    if requires_identity_check_step(user):
        ordered_steps.append(models.SubscriptionStep.IDENTITY_CHECK)
    ordered_steps.append(models.SubscriptionStep.HONOR_STATEMENT)
    return ordered_steps


def _get_steps_details(
    user: users_models.User,
    ordered_steps: list[models.SubscriptionStep],
    user_subscription_state: models.UserSubscriptionState,
) -> list[models.SubscriptionStepDetails]:
    steps: list[models.SubscriptionStepDetails] = []
    is_before_current_step = True

    for step in ordered_steps:
        subtitle = _get_step_subtitle(user, user_subscription_state, step)
        if step == user_subscription_state.next_step:
            is_before_current_step = False
            completion_step = (
                models.SubscriptionStepCompletionState.RETRY
                if _has_subscription_issues(user_subscription_state)
                else models.SubscriptionStepCompletionState.CURRENT
            )
            steps.append(
                models.SubscriptionStepDetails(
                    name=step,
                    title=models.SubscriptionStepTitle[step.name],
                    completion_state=completion_step,
                    subtitle=subtitle,
                )
            )
            continue
        steps.append(
            models.SubscriptionStepDetails(
                name=step,
                title=models.SubscriptionStepTitle[step.name],
                subtitle=subtitle,
                completion_state=(
                    models.SubscriptionStepCompletionState.COMPLETED
                    if is_before_current_step
                    else models.SubscriptionStepCompletionState.DISABLED
                ),
            )
        )

    return steps


def requires_identity_check_step(user: users_models.User) -> bool:
    if user.eligibility == users_models.EligibilityType.FREE:
        return False

    if not user.has_underage_beneficiary_role:
        return True

    fraud_check = fraud_repository.get_relevant_identity_fraud_check(user, users_models.EligibilityType.AGE18)
    if not fraud_check:
        return True

    if (
        fraud_check.status == fraud_models.FraudCheckStatus.OK
        and fraud_check.type in models.VALID_IDENTITY_CHECK_TYPES_AFTER_UNDERAGE_DEPOSIT_EXPIRATION
    ):
        return False
    return True


def _has_completed_profile_for_previous_eligibility_only(user: users_models.User) -> bool:
    if not user.is_18_or_above_eligible:
        return False

    if user.eligibility == users_models.EligibilityType.AGE18:
        return has_completed_profile_for_given_eligibility(
            user, users_models.EligibilityType.UNDERAGE
        ) and not has_completed_profile_for_given_eligibility(user, users_models.EligibilityType.AGE18)

    return has_completed_underage_profile(user) and not has_completed_profile_for_given_eligibility(
        user, users_models.EligibilityType.AGE17_18
    )


def _get_step_subtitle(
    user: users_models.User, user_subscription_state: models.UserSubscriptionState, step: models.SubscriptionStep
) -> str | None:
    if step == models.SubscriptionStep.IDENTITY_CHECK and _has_subscription_issues(user_subscription_state):
        return (
            user_subscription_state.subscription_message.action_hint
            if user_subscription_state.subscription_message
            else None
        )

    if step == models.SubscriptionStep.PROFILE_COMPLETION and _has_completed_profile_for_previous_eligibility_only(
        user
    ):
        return subscription_models.PROFILE_COMPLETION_STEP_EXISTING_DATA_SUBTITLE

    return None


def get_stepper_title_and_subtitle(
    user: users_models.User, user_subscription_state: models.UserSubscriptionState
) -> models.SubscriptionStepperDetails:
    """Return the titles of the steps to display in the subscription stepper."""

    if _has_subscription_issues(user_subscription_state):
        return models.SubscriptionStepperDetails(title=models.STEPPER_HAS_ISSUES_TITLE)

    if not user.age:
        logger.error("Eligible user has no age", extra={"user": user.id})
        return models.SubscriptionStepperDetails(title=models.STEPPER_DEFAULT_TITLE)

    eligibility_to_activate = eligibility_api.get_pre_decree_or_current_eligibility(user)
    amount_to_display = finance_conf.get_credit_amount_per_age_and_eligibility(user.age, eligibility_to_activate)
    subtitle = models.STEPPER_DEFAULT_SUBTITLE.format(amount_to_display)

    return models.SubscriptionStepperDetails(title=models.STEPPER_DEFAULT_TITLE, subtitle=subtitle)


def _has_subscription_issues(user_subscription_state: models.UserSubscriptionState) -> bool:
    return user_subscription_state.young_status == young_status_module.Eligible(
        subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_ISSUES
    )
