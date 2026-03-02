import logging

import pcapi.core.finance.conf as finance_conf
from pcapi import settings
from pcapi.core.subscription import fraud_check_api as fraud_api
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import repository as subscription_repository
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.dms import api as dms_subscription_api
from pcapi.core.subscription.educonnect import api as educonnect_subscription_api
from pcapi.core.subscription.ubble import api as ubble_subscription_api
from pcapi.core.users import eligibility_api
from pcapi.core.users import models as users_models
from pcapi.core.users import young_status as young_status_module


logger = logging.getLogger(__name__)


SUBSCRIPTION_SUPPORT_FORM_URL = "https://aide.passculture.app/hc/fr/requests/new?ticket_form_id=20669662761500"

MAINTENANCE_PAGE_MESSAGE = subscription_schemas.SubscriptionMessage(
    user_message="La vérification d'identité est momentanément indisponible. L'équipe du pass Culture met tout en oeuvre pour la rétablir au plus vite.",
    call_to_action=None,
    pop_over_icon=subscription_schemas.PopOverIcon.CLOCK,
)

REDIRECT_TO_DMS_CALL_TO_ACTION = subscription_schemas.CallToActionMessage(
    title="Accéder au site Démarche Numérique",
    link=f"{settings.WEBAPP_V2_URL}/verification-identite/demarches-simplifiees",
    icon=subscription_schemas.CallToActionIcon.EXTERNAL,
)

REDIRECT_TO_IDENTIFICATION_CHOICE = subscription_schemas.CallToActionMessage(
    title="Réessayer la vérification de mon identité",
    link=f"{settings.WEBAPP_V2_URL}/verification-identite",
    icon=subscription_schemas.CallToActionIcon.RETRY,
)


def compute_support_call_to_action(user_id: int) -> subscription_schemas.CallToActionMessage:
    return subscription_schemas.CallToActionMessage(
        title="Contacter le support",
        link=SUBSCRIPTION_SUPPORT_FORM_URL,
        icon=subscription_schemas.CallToActionIcon.EXTERNAL,
    )


def get_generic_ko_message(user_id: int) -> subscription_schemas.SubscriptionMessage:
    return subscription_schemas.SubscriptionMessage(
        user_message="Ton inscription n'a pas pu aboutir. Contacte le support pour plus d'informations",
        call_to_action=compute_support_call_to_action(user_id),
        pop_over_icon=None,
    )


def build_duplicate_error_message(
    user: users_models.User,
    reason_code: subscription_models.FraudReasonCode,
    application_content: subscription_schemas.IdentityCheckContent | None,
) -> str:
    match reason_code:
        case subscription_models.FraudReasonCode.DUPLICATE_INE:
            message_start = "Ton dossier a été refusé car il y a déjà un compte bénéficiaire associé aux identifiants ÉduConnect que tu as fournis."
        case subscription_models.FraudReasonCode.DUPLICATE_USER:
            message_start = "Ton dossier a été refusé car il y a déjà un compte bénéficiaire à ton nom."
        case subscription_models.FraudReasonCode.DUPLICATE_ID_PIECE_NUMBER:
            message_start = "Ton dossier a été refusé car il y a déjà un compte bénéficiaire associé à ce numéro de pièce d’identité."
        case _:
            logger.error("Duplicate error with no matching body message %s", reason_code)
            message_start = "Ton dossier a été refusé car tu as déjà un compte bénéficiaire"

    contact_support_message = "Contacte le support si tu penses qu’il s’agit d’une erreur."
    message_end = "Si tu n’as plus ton mot de passe, tu peux effectuer une demande de réinitialisation."

    default_message = f"{message_start} {contact_support_message} {message_end}"

    if not application_content:
        return default_message

    anonymized_email = fraud_api.get_duplicate_beneficiary_anonymized_email(user, application_content, reason_code)
    if anonymized_email is None:
        return default_message

    return f"{message_start} Connecte-toi avec l’adresse mail {anonymized_email} ou {contact_support_message.lower()} {message_end}"


def get_subscription_message(
    fraud_check: subscription_models.BeneficiaryFraudCheck | None,
) -> subscription_schemas.SubscriptionMessage | None:
    """The subscription message is meant to help the user have information about the subscription status."""
    if not fraud_check:
        return None

    match fraud_check.type:
        case subscription_models.FraudCheckType.DMS:
            return dms_subscription_api.get_dms_subscription_message(fraud_check)
        case subscription_models.FraudCheckType.UBBLE:
            return ubble_subscription_api.get_ubble_subscription_message(fraud_check)
        case subscription_models.FraudCheckType.EDUCONNECT:
            return educonnect_subscription_api.get_educonnect_subscription_message(fraud_check)
        case _:
            return get_generic_ko_message(fraud_check.user.id)


def get_subscription_steps_to_display(
    user: users_models.User, user_subscription_state: subscription_schemas.UserSubscriptionState
) -> list[subscription_schemas.SubscriptionStepDetails]:
    """
    return the list of steps to complete to subscribe to the pass Culture
    the steps are ordered
    """
    ordered_steps = _get_ordered_steps(user)
    return _get_steps_details(user, ordered_steps, user_subscription_state)


def _get_ordered_steps(user: users_models.User) -> list[subscription_schemas.SubscriptionStep]:
    from pcapi.core.subscription.api import requires_identity_check_step

    ordered_steps = []
    should_fill_phone = user.is_18_or_above_eligible
    if should_fill_phone:
        ordered_steps.append(subscription_schemas.SubscriptionStep.PHONE_VALIDATION)
    ordered_steps.append(subscription_schemas.SubscriptionStep.PROFILE_COMPLETION)
    if requires_identity_check_step(user):
        ordered_steps.append(subscription_schemas.SubscriptionStep.IDENTITY_CHECK)
    ordered_steps.append(subscription_schemas.SubscriptionStep.HONOR_STATEMENT)
    return ordered_steps


def _get_steps_details(
    user: users_models.User,
    ordered_steps: list[subscription_schemas.SubscriptionStep],
    user_subscription_state: subscription_schemas.UserSubscriptionState,
) -> list[subscription_schemas.SubscriptionStepDetails]:
    steps: list[subscription_schemas.SubscriptionStepDetails] = []
    is_before_current_step = True

    for step in ordered_steps:
        subtitle = _get_step_subtitle(user, user_subscription_state, step)
        if step == user_subscription_state.next_step:
            is_before_current_step = False
            completion_step = (
                subscription_schemas.SubscriptionStepCompletionState.RETRY
                if _has_subscription_issues(user_subscription_state)
                else subscription_schemas.SubscriptionStepCompletionState.CURRENT
            )
            steps.append(
                subscription_schemas.SubscriptionStepDetails(
                    name=step,
                    title=subscription_schemas.SubscriptionStepTitle[step.name],
                    completion_state=completion_step,
                    subtitle=subtitle,
                )
            )
            continue
        steps.append(
            subscription_schemas.SubscriptionStepDetails(
                name=step,
                title=subscription_schemas.SubscriptionStepTitle[step.name],
                subtitle=subtitle,
                completion_state=(
                    subscription_schemas.SubscriptionStepCompletionState.COMPLETED
                    if is_before_current_step
                    else subscription_schemas.SubscriptionStepCompletionState.DISABLED
                ),
            )
        )

    return steps


def _get_step_subtitle(
    user: users_models.User,
    user_subscription_state: subscription_schemas.UserSubscriptionState,
    step: subscription_schemas.SubscriptionStep,
) -> str | None:
    if step == subscription_schemas.SubscriptionStep.IDENTITY_CHECK and _has_subscription_issues(
        user_subscription_state
    ):
        return (
            user_subscription_state.subscription_message.action_hint
            if user_subscription_state.subscription_message
            else None
        )

    if (
        step == subscription_schemas.SubscriptionStep.PROFILE_COMPLETION
        and _has_completed_profile_for_previous_eligibility_only(user)
    ):
        return subscription_schemas.PROFILE_COMPLETION_STEP_EXISTING_DATA_SUBTITLE

    return None


def get_stepper_title_and_subtitle(
    user: users_models.User, user_subscription_state: subscription_schemas.UserSubscriptionState
) -> subscription_schemas.SubscriptionStepperDetails:
    """Return the titles of the steps to display in the subscription stepper."""

    has_subscription_issues = user_subscription_state.young_status == young_status_module.Eligible(
        subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_ISSUES
    )
    if has_subscription_issues:
        return subscription_schemas.SubscriptionStepperDetails(title=subscription_schemas.STEPPER_HAS_ISSUES_TITLE)

    if not user.age:
        logger.error("Eligible user has no age", extra={"user": user.id})
        return subscription_schemas.SubscriptionStepperDetails(title=subscription_schemas.STEPPER_DEFAULT_TITLE)

    eligibility_to_activate = eligibility_api.get_pre_decree_or_current_eligibility(user)
    amount_to_display = finance_conf.get_credit_amount_per_age_and_eligibility(user.age, eligibility_to_activate)
    subtitle = subscription_schemas.STEPPER_DEFAULT_SUBTITLE.format(amount_to_display)

    return subscription_schemas.SubscriptionStepperDetails(
        title=subscription_schemas.STEPPER_DEFAULT_TITLE, subtitle=subtitle
    )


def _has_completed_profile_for_previous_eligibility_only(user: users_models.User) -> bool:
    from pcapi.core.subscription.api import has_completed_profile_for_given_eligibility

    if not user.is_18_or_above_eligible:
        return False

    if user.eligibility == users_models.EligibilityType.AGE18:
        return has_completed_profile_for_given_eligibility(
            user, users_models.EligibilityType.UNDERAGE
        ) and not has_completed_profile_for_given_eligibility(user, users_models.EligibilityType.AGE18)

    return has_completed_underage_profile(user) and not has_completed_profile_for_given_eligibility(
        user, users_models.EligibilityType.AGE17_18
    )


def has_completed_underage_profile(user: users_models.User) -> bool:
    if subscription_repository.get_completed_underage_profile_check(user) is not None:
        return True
    if subscription_repository.get_filled_underage_dms_fraud_check(user) is not None:
        return True
    return False


def _has_subscription_issues(user_subscription_state: subscription_schemas.UserSubscriptionState) -> bool:
    return user_subscription_state.young_status == young_status_module.Eligible(
        subscription_status=young_status_module.SubscriptionStatus.HAS_SUBSCRIPTION_ISSUES
    )
