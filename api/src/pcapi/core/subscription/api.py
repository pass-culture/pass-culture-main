import datetime
import logging
import typing

from pcapi import settings
from pcapi.analytics.amplitude import events as amplitude_events
from pcapi.core.external import batch
from pcapi.core.external.attributes import api as external_attributes_api
import pcapi.core.finance.api as finance_api
import pcapi.core.finance.conf as finance_conf
import pcapi.core.finance.exceptions as finance_exceptions
import pcapi.core.fraud.api as fraud_api
import pcapi.core.fraud.common.models as common_fraud_models
import pcapi.core.fraud.models as fraud_models
import pcapi.core.fraud.repository as fraud_repository
import pcapi.core.fraud.ubble.constants as ubble_constants
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.subscription.educonnect import api as educonnect_subscription_api
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.core.users import young_status as young_status_module
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
import pcapi.repository as pcapi_repository
import pcapi.utils.postal_code as postal_code_utils
from pcapi.workers import apps_flyer_job

from . import exceptions
from . import models
from . import repository


logger = logging.getLogger(__name__)


def _get_age_at_first_registration(user: users_models.User, eligibility: users_models.EligibilityType) -> int | None:
    if not user.birth_date:
        return None

    first_registration_date = get_first_registration_date(user, user.birth_date, eligibility)
    if not first_registration_date:
        return user.age

    age_at_registration = users_utils.get_age_at_date(user.birth_date, first_registration_date)
    if (
        eligibility == users_models.EligibilityType.UNDERAGE
        and age_at_registration not in users_constants.ELIGIBILITY_UNDERAGE_RANGE
    ):
        return None
    return age_at_registration


def activate_beneficiary_for_eligibility(
    user: users_models.User,
    fraud_check: fraud_models.BeneficiaryFraudCheck,
    eligibility: users_models.EligibilityType,
) -> users_models.User:
    if eligibility == users_models.EligibilityType.UNDERAGE:
        user.add_underage_beneficiary_role()
        age_at_registration = _get_age_at_first_registration(user, users_models.EligibilityType.UNDERAGE)

        if age_at_registration not in users_constants.ELIGIBILITY_UNDERAGE_RANGE:
            raise exceptions.InvalidAgeException(age=age_at_registration)

    elif eligibility == users_models.EligibilityType.AGE18:
        user.add_beneficiary_role()
        age_at_registration = users_constants.ELIGIBILITY_AGE_18
    else:
        raise exceptions.InvalidEligibilityTypeException()

    deposit = finance_api.create_deposit(
        user,
        deposit_source=fraud_check.get_detailed_source(),
        eligibility=eligibility,
        age_at_registration=age_at_registration,
    )

    db.session.add_all((user, deposit))
    db.session.commit()
    logger.info("Activated beneficiary and created deposit", extra={"user": user.id, "source": deposit.source})

    transactional_mails.send_accepted_as_beneficiary_email(user=user)

    external_attributes_api.update_external_user(user)
    batch.track_deposit_activated_event(user.id, deposit)
    amplitude_events.track_deposit_activation_event(user.id, deposit, fraud_check)

    if "apps_flyer" in user.externalIds:
        apps_flyer_job.log_user_becomes_beneficiary_event_job.delay(user.id)

    return user


def _get_filled_dms_fraud_check(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> fraud_models.BeneficiaryFraudCheck | None:
    # If a pending or started DMS fraud check exists, the user has already completed the profile.
    # No need to ask for this information again.
    return next(
        (
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.DMS
            and fraud_check.eligibilityType == eligibility
            and fraud_check.status in (fraud_models.FraudCheckStatus.PENDING, fraud_models.FraudCheckStatus.STARTED)
            and fraud_check.resultContent
            and fraud_check.source_data().city is not None
        ),
        None,
    )


def has_completed_profile_for_given_eligibility(
    user: users_models.User, eligibility: users_models.EligibilityType
) -> bool:
    if repository.get_completed_profile_check(user, eligibility) is not None:
        return True
    if _get_filled_dms_fraud_check(user, eligibility) is not None:
        return True
    return False


def get_declared_names(user: users_models.User) -> tuple[str, str] | None:
    profile_completion_check = repository.get_completed_profile_check(user, user.eligibility)
    if profile_completion_check and profile_completion_check.resultContent:
        profile_data = typing.cast(fraud_models.ProfileCompletionContent, profile_completion_check.source_data())
        return profile_data.first_name, profile_data.last_name

    dms_filled_check = _get_filled_dms_fraud_check(user, user.eligibility)
    if dms_filled_check:
        dms_data = dms_filled_check.source_data()
        return dms_data.first_name, dms_data.last_name

    return None


def is_eligibility_activable(user: users_models.User, eligibility: users_models.EligibilityType | None) -> bool:
    return (
        user.eligibility == eligibility
        and users_api.is_eligible_for_beneficiary_upgrade(user, eligibility)
        and users_api.is_user_age_compatible_with_eligibility(user.age, eligibility)
    )


def get_email_validation_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    if user.isEmailValidated:
        status = models.SubscriptionItemStatus.OK
    else:
        if is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.EMAIL_VALIDATION, status=status)


def get_phone_validation_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    if eligibility != users_models.EligibilityType.AGE18:
        status = models.SubscriptionItemStatus.NOT_APPLICABLE
    else:
        if user.is_phone_validated:
            status = models.SubscriptionItemStatus.OK
        elif user.is_phone_validation_skipped:
            status = models.SubscriptionItemStatus.SKIPPED
        elif not FeatureToggle.ENABLE_PHONE_VALIDATION.is_active():
            status = models.SubscriptionItemStatus.NOT_ENABLED
        elif fraud_repository.has_failed_phone_validation(user):
            status = models.SubscriptionItemStatus.KO
        elif is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.PHONE_VALIDATION, status=status)


def get_profile_completion_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType
) -> models.SubscriptionItem:
    if has_completed_profile_for_given_eligibility(user, eligibility):
        status = models.SubscriptionItemStatus.OK
    elif is_eligibility_activable(user, eligibility):
        status = models.SubscriptionItemStatus.TODO
    else:
        status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.PROFILE_COMPLETION, status=status)


def get_profile_data(user: users_models.User) -> fraud_models.ProfileCompletionContent | None:
    profile_completion_check = repository.get_latest_completed_profile_check(user)
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
        if is_eligibility_activable(user, eligibility):
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


def get_relevant_identity_fraud_check(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> fraud_models.BeneficiaryFraudCheck | None:
    identity_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if eligibility in fraud_check.applicable_eligibilities and fraud_check.type in fraud_models.IDENTITY_CHECK_TYPES
    ]
    identity_fraud_checks.sort(key=lambda fraud_check: fraud_check.dateCreated, reverse=True)

    if not identity_fraud_checks:
        return None

    for status in (  # order matters here
        fraud_models.FraudCheckStatus.OK,
        fraud_models.FraudCheckStatus.PENDING,
        fraud_models.FraudCheckStatus.STARTED,
        fraud_models.FraudCheckStatus.SUSPICIOUS,
        fraud_models.FraudCheckStatus.KO,
    ):
        relevant_fraud_check = next(
            (fraud_check for fraud_check in identity_fraud_checks if fraud_check.status == status), None
        )
        if relevant_fraud_check:
            return relevant_fraud_check

    return None


def get_identity_check_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    id_check = get_relevant_identity_fraud_check(user, eligibility)
    status = get_identity_check_fraud_status(user, eligibility, id_check)
    return models.SubscriptionItem(type=models.SubscriptionStep.IDENTITY_CHECK, status=status)


def get_honor_statement_subscription_item(
    user: users_models.User, eligibility: users_models.EligibilityType | None
) -> models.SubscriptionItem:
    if fraud_api.has_performed_honor_statement(user, eligibility):  # type: ignore[arg-type]
        status = models.SubscriptionItemStatus.OK
    else:
        if is_eligibility_activable(user, eligibility):
            status = models.SubscriptionItemStatus.TODO
        else:
            status = models.SubscriptionItemStatus.VOID

    return models.SubscriptionItem(type=models.SubscriptionStep.HONOR_STATEMENT, status=status)


def get_user_subscription_state(user: users_models.User) -> subscription_models.UserSubscriptionState:
    # Step 1: email validation
    if not user.isEmailValidated:
        return subscription_models.UserSubscriptionState(
            fraud_status=models.SubscriptionItemStatus.TODO,
            next_step=models.SubscriptionStep.EMAIL_VALIDATION,
            young_status=young_status_module.Eligible(
                subscription_status=young_status_module.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION
            ),
        )

    # Early return if user is beneficiary
    if user.is_beneficiary and not users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility):
        if user.has_active_deposit:
            return subscription_models.UserSubscriptionState(
                fraud_status=models.SubscriptionItemStatus.OK,
                next_step=None,
                young_status=young_status_module.Beneficiary(),
            )
        return subscription_models.UserSubscriptionState(
            fraud_status=models.SubscriptionItemStatus.OK,
            next_step=None,
            young_status=young_status_module.ExBeneficiary(),
        )

    # Early return if there is an admin manual review
    if fraud_repository.has_admin_ko_review(user):
        return subscription_models.UserSubscriptionState(
            fraud_status=models.SubscriptionItemStatus.KO,
            next_step=None,
            young_status=young_status_module.NonEligible(),
            subscription_message=subscription_messages.get_generic_ko_message(user.id),
        )

    # Early return if user is not eligible
    if user.eligibility is None:
        return subscription_models.UserSubscriptionState(
            fraud_status=models.SubscriptionItemStatus.VOID,
            next_step=None,
            young_status=young_status_module.NonEligible(),
        )

    # Step 2: phone validation
    phone_subscription_item = get_phone_validation_subscription_item(user, user.eligibility)
    if phone_subscription_item.status == models.SubscriptionItemStatus.KO:
        return subscription_models.UserSubscriptionState(
            fraud_status=models.SubscriptionItemStatus.KO,
            next_step=models.SubscriptionStep.PHONE_VALIDATION,
            young_status=young_status_module.Eligible(
                subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_ISSUES
            ),
        )
    if phone_subscription_item.status == models.SubscriptionItemStatus.TODO:
        return subscription_models.UserSubscriptionState(
            fraud_status=models.SubscriptionItemStatus.TODO,
            next_step=models.SubscriptionStep.PHONE_VALIDATION,
            young_status=young_status_module.Eligible(
                subscription_status=young_status_module.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION
            ),
        )

    # Step 4: profile completion
    if not has_completed_profile_for_given_eligibility(user, user.eligibility):
        return subscription_models.UserSubscriptionState(
            fraud_status=models.SubscriptionItemStatus.TODO,
            next_step=models.SubscriptionStep.PROFILE_COMPLETION,
            young_status=young_status_module.Eligible(
                subscription_status=young_status_module.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION
            ),
        )

    # Step 5: identity check
    relevant_identity_fraud_check = get_relevant_identity_fraud_check(user, user.eligibility)
    identity_check_fraud_status = get_identity_check_fraud_status(user, user.eligibility, relevant_identity_fraud_check)
    allowed_identity_check_methods = get_allowed_identity_check_methods(user)
    next_step: models.SubscriptionStep | None = (
        models.SubscriptionStep.IDENTITY_CHECK
        if len(allowed_identity_check_methods) > 0
        else models.SubscriptionStep.MAINTENANCE
    )
    subscription_message = (
        _get_subscription_message(relevant_identity_fraud_check)
        if len(allowed_identity_check_methods) > 0
        else subscription_messages.MAINTENANCE_PAGE_MESSAGE
    )

    if identity_check_fraud_status in [models.SubscriptionItemStatus.KO, models.SubscriptionItemStatus.SUSPICIOUS]:
        assert (
            relevant_identity_fraud_check is not None
        )  # mypy. This is not None if identity_check_fraud_status is KO or SUSPICIOUS (see get_identity_check_fraud_status)
        if can_retry_identity_fraud_check(relevant_identity_fraud_check):
            identity_check_fraud_status = models.SubscriptionItemStatus.TODO
        else:
            next_step = None

        return subscription_models.UserSubscriptionState(
            identity_fraud_check=relevant_identity_fraud_check,
            fraud_status=identity_check_fraud_status,
            subscription_message=subscription_message,
            next_step=next_step,
            young_status=young_status_module.Eligible(
                subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_ISSUES
            ),
        )

    if identity_check_fraud_status == models.SubscriptionItemStatus.TODO:
        return subscription_models.UserSubscriptionState(
            identity_fraud_check=relevant_identity_fraud_check,
            fraud_status=identity_check_fraud_status,
            subscription_message=subscription_message,
            next_step=next_step,
            young_status=young_status_module.Eligible(
                subscription_status=young_status_module.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION
            ),
        )

    if identity_check_fraud_status in [models.SubscriptionItemStatus.OK, models.SubscriptionItemStatus.PENDING]:
        pass  # Continue to honor statement

    else:
        logger.error("Unknown fraud status %s", identity_check_fraud_status)
        return subscription_models.UserSubscriptionState(
            identity_fraud_check=relevant_identity_fraud_check,
            fraud_status=identity_check_fraud_status,
            next_step=None,
            young_status=young_status_module.Eligible(
                subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_ISSUES
            ),
            subscription_message=subscription_messages.get_generic_ko_message(user.id),
        )

    # Step 6: honor statement
    if not fraud_api.has_performed_honor_statement(user, user.eligibility):
        return subscription_models.UserSubscriptionState(
            identity_fraud_check=relevant_identity_fraud_check,
            next_step=models.SubscriptionStep.HONOR_STATEMENT,
            fraud_status=identity_check_fraud_status,
            subscription_message=None,  # The user needs no message to complete honor statement
            young_status=young_status_module.Eligible(
                subscription_status=young_status_module.SubscriptionStatus.HAS_TO_COMPLETE_SUBSCRIPTION
            ),
        )

    if identity_check_fraud_status == models.SubscriptionItemStatus.OK:
        is_activable = True
        assert relevant_identity_fraud_check  # mypy
        if requires_manual_review_before_activation(user, relevant_identity_fraud_check):
            is_activable = False
        return subscription_models.UserSubscriptionState(
            identity_fraud_check=relevant_identity_fraud_check,
            is_activable=is_activable,
            fraud_status=identity_check_fraud_status,
            subscription_message=None,
            next_step=None,
            young_status=young_status_module.Eligible(
                subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_PENDING
            ),
        )

    return subscription_models.UserSubscriptionState(
        identity_fraud_check=relevant_identity_fraud_check,
        fraud_status=identity_check_fraud_status,
        subscription_message=subscription_message,
        next_step=None,
        young_status=young_status_module.Eligible(
            subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_PENDING
        ),
    )


def requires_manual_review_before_activation(
    user: users_models.User, identity_fraud_check: fraud_models.BeneficiaryFraudCheck
) -> bool:
    return (
        identity_fraud_check.type == fraud_models.FraudCheckType.DMS
        and identity_fraud_check.status == fraud_models.FraudCheckStatus.OK
        and not users_api.get_eligibility_at_date(
            user.birth_date, identity_fraud_check.get_min_date_between_creation_and_registration()
        )
    )


def complete_profile(
    user: users_models.User,
    address: str,
    city: str,
    postal_code: str,
    activity: users_models.ActivityEnum,
    first_name: str,
    last_name: str,
    school_type: users_models.SchoolTypeEnum | None = None,
) -> None:
    update_payload = {
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
        users_models.User.query.filter(users_models.User.id == user.id).update(update_payload)

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

    if (
        user.eligibility == users_models.EligibilityType.UNDERAGE
        and FeatureToggle.ENABLE_EDUCONNECT_AUTHENTICATION.is_active()
    ):
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
    )
    eligibility_ranges = users_constants.ELIGIBILITY_UNDERAGE_RANGE + [users_constants.ELIGIBILITY_AGE_18]
    eligibility_ranges = [age + 1 for age in eligibility_ranges]
    if future_age > user.age and future_age in eligibility_ranges:  # type: ignore[operator]
        return True

    return False


def get_maintenance_page_type(user: users_models.User) -> models.MaintenancePageType | None:
    allowed_identity_check_methods = get_allowed_identity_check_methods(user)
    if allowed_identity_check_methods:
        return None

    if (
        user.eligibility == users_models.EligibilityType.AGE18
        and FeatureToggle.ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_AGE_18.is_active()
    ):
        return models.MaintenancePageType.WITH_DMS
    if (
        user.eligibility == users_models.EligibilityType.UNDERAGE
        and FeatureToggle.ENABLE_DMS_LINK_ON_MAINTENANCE_PAGE_FOR_UNDERAGE.is_active()
    ):
        return models.MaintenancePageType.WITH_DMS

    return models.MaintenancePageType.WITHOUT_DMS


def activate_beneficiary_if_no_missing_step(user: users_models.User) -> bool:
    subscription_state = get_user_subscription_state(user)

    if not subscription_state.is_activable:
        return False
    if not subscription_state.identity_fraud_check:
        return False
    if subscription_state.identity_fraud_check.resultContent is None:
        return False
    if user.eligibility is None:
        return False

    duplicate_beneficiary = fraud_api.get_duplicate_beneficiary(subscription_state.identity_fraud_check)
    if duplicate_beneficiary:
        fraud_api.invalidate_fraud_check_for_duplicate_user(
            subscription_state.identity_fraud_check, duplicate_beneficiary.id
        )
        return False

    source_data = typing.cast(
        common_fraud_models.IdentityCheckContent, subscription_state.identity_fraud_check.source_data()
    )
    users_api.update_user_information_from_external_source(user, source_data, commit=False)

    try:
        activate_beneficiary_for_eligibility(user, subscription_state.identity_fraud_check, user.eligibility)
    except (finance_exceptions.DepositTypeAlreadyGrantedException, finance_exceptions.UserHasAlreadyActiveDeposit):
        # this error may happen on identity provider concurrent requests
        logger.info("A deposit already exists for user %s", user.id)
        return False

    return True


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

    pcapi_repository.repository.save(fraud_check, new_fraud_check)

    return new_fraud_check


def get_id_provider_detected_eligibility(
    user: users_models.User, identity_content: common_fraud_models.IdentityCheckContent
) -> users_models.EligibilityType | None:
    return fraud_api.decide_eligibility(
        user, identity_content.get_birth_date(), identity_content.get_registration_datetime()
    )


# TODO (Lixxday): use a proper BeneficiaryFraudCheck History model to track these kind of updates
def handle_eligibility_difference_between_declaration_and_identity_provider(
    user: users_models.User,
    fraud_check: fraud_models.BeneficiaryFraudCheck,
) -> fraud_models.BeneficiaryFraudCheck:
    identity_content: common_fraud_models.IdentityCheckContent = fraud_check.source_data()

    declared_eligibility = fraud_check.eligibilityType
    id_provider_detected_eligibility = get_id_provider_detected_eligibility(user, identity_content)

    if declared_eligibility == id_provider_detected_eligibility or id_provider_detected_eligibility is None:
        return fraud_check

    new_fraud_check = _update_fraud_check_eligibility_with_history(fraud_check, id_provider_detected_eligibility)

    # Handle eligibility update for PROFILE_COMPLETION fraud check, if it exists
    profile_completion_fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter(
        fraud_models.BeneficiaryFraudCheck.user == user,
        fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.PROFILE_COMPLETION,
        fraud_models.BeneficiaryFraudCheck.eligibilityType == declared_eligibility,
    ).first()
    if profile_completion_fraud_check:
        _update_fraud_check_eligibility_with_history(profile_completion_fraud_check, id_provider_detected_eligibility)

    # Handle eligibility update for HONOR_STATEMENT fraud check, if it exists
    honor_statement_fraud_check = fraud_models.BeneficiaryFraudCheck.query.filter(
        fraud_models.BeneficiaryFraudCheck.user == user,
        fraud_models.BeneficiaryFraudCheck.type == fraud_models.FraudCheckType.HONOR_STATEMENT,
        fraud_models.BeneficiaryFraudCheck.eligibilityType == declared_eligibility,
    ).first()
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
        and (users_api.is_eligible_for_beneficiary_upgrade(user, user.eligibility) or not user.validatedBirthDate)
    ):
        user.validatedBirthDate = birth_date
        pcapi_repository.repository.save(user)


def get_first_registration_date(
    user: users_models.User,
    birth_date: datetime.date | None,
    eligibility: users_models.EligibilityType,
) -> datetime.datetime | None:
    fraud_checks = user.beneficiaryFraudChecks
    if not fraud_checks or not birth_date:
        return None

    registration_dates_when_eligible = [
        fraud_check.get_min_date_between_creation_and_registration()
        for fraud_check in fraud_checks
        if fraud_check.eligibilityType == eligibility
        and users_api.is_user_age_compatible_with_eligibility(
            users_utils.get_age_at_date(birth_date, fraud_check.get_min_date_between_creation_and_registration()),
            eligibility,
        )
    ]

    return min(registration_dates_when_eligible) if registration_dates_when_eligible else None


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
    pcapi_repository.repository.save(fraud_check)
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
    if user.eligibility == users_models.EligibilityType.AGE18 and FeatureToggle.ENABLE_PHONE_VALIDATION.is_active():
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
    if not user.has_underage_beneficiary_role:
        return True

    fraud_check = get_relevant_identity_fraud_check(user, users_models.EligibilityType.AGE18)
    if not fraud_check:
        return True

    if (
        fraud_check.status == fraud_models.FraudCheckStatus.OK
        and fraud_check.type in models.VALID_IDENTITY_CHECK_TYPES_AFTER_UNDERAGE_DEPOSIT_EXPIRATION
    ):
        return False
    return True


def _has_completed_profile_for_previous_eligibility_only(user: users_models.User) -> bool:
    if user.eligibility == users_models.EligibilityType.AGE18:
        return has_completed_profile_for_given_eligibility(
            user, users_models.EligibilityType.UNDERAGE
        ) and not has_completed_profile_for_given_eligibility(user, users_models.EligibilityType.AGE18)

    return False


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

    amount_to_display = finance_conf.get_amount_to_display(user.age)
    subtitle = models.STEPPER_DEFAULT_SUBTITLE.format(amount_to_display)

    return models.SubscriptionStepperDetails(title=models.STEPPER_DEFAULT_TITLE, subtitle=subtitle)


def _has_subscription_issues(user_subscription_state: models.UserSubscriptionState) -> bool:
    return user_subscription_state.young_status == young_status_module.Eligible(
        subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_ISSUES
    )
