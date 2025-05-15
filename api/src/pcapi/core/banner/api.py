import decimal

import pcapi.core.finance.conf as finance_conf
import pcapi.core.fraud.models as fraud_models
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.models as subscription_models
import pcapi.core.users.models as users_models
import pcapi.routes.native.v1.serialization.banner as serializers
from pcapi.core.users import eligibility_api
from pcapi.utils.string import u_nbsp


ACTIVATION_BANNER_NEXT_STEPS = [
    subscription_models.SubscriptionStep.PHONE_VALIDATION,
    subscription_models.SubscriptionStep.PROFILE_COMPLETION,
    subscription_models.SubscriptionStep.IDENTITY_CHECK,
    subscription_models.SubscriptionStep.HONOR_STATEMENT,
]

GEOLOCATION_BANNER = serializers.Banner(
    name=serializers.BannerName.GEOLOCATION_BANNER,
    title=serializers.BannerTitle.GEOLOCATION_BANNER.value,
    text=serializers.BannerText.GEOLOCATION_BANNER.value,
)


def get_banner(
    user_subscription_state: subscription_models.UserSubscriptionState,
    user: users_models.User,
    is_geolocated: bool,
) -> serializers.Banner | None:
    banner = None
    should_display_activation_banner = (
        user.eligibility != users_models.EligibilityType.FREE
        and user_subscription_state.next_step in ACTIVATION_BANNER_NEXT_STEPS
    )
    if should_display_activation_banner:
        banner = _get_activation_banner(user, user_subscription_state)
    elif not is_geolocated:
        banner = GEOLOCATION_BANNER

    return banner


def _is_17_18_transition(user: users_models.User) -> bool:
    return (
        users_models.UserRole.UNDERAGE_BENEFICIARY in user.roles and users_models.UserRole.BENEFICIARY not in user.roles
    )


def _has_completed_id_check(user: users_models.User) -> bool:
    return any(
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type in (fraud_models.FraudCheckType.DMS, fraud_models.FraudCheckType.UBBLE)
        and user.eligibility in fraud_check.applicable_eligibilities
        and fraud_check.status == fraud_models.FraudCheckStatus.OK
    )


def _get_17_18_transition_banner_information_text(
    user: users_models.User,
) -> str:
    if _has_completed_id_check(user):
        return serializers.BannerText.TRANSITION_17_18_BANNER_ID_CHECK_DONE.value

    return serializers.BannerText.TRANSITION_17_18_BANNER_ID_CHECK_TODO.value


def _get_17_18_transition_banner_information(
    user: users_models.User,
    amount_to_display: decimal.Decimal,
) -> serializers.Banner | None:
    banner_text = _get_17_18_transition_banner_information_text(user)
    return serializers.Banner(
        name=serializers.BannerName.TRANSITION_17_18_BANNER,
        title=serializers.BannerTitle.TRANSITION_17_18_BANNER.value.format(f"{amount_to_display}{u_nbsp}"),
        text=banner_text,
    )


def _get_activation_banner(
    user: users_models.User, user_subscription_state: subscription_models.UserSubscriptionState
) -> serializers.Banner | None:
    """
    Return the activation banner
    Business rules:
        - if the user is not eligible, return None
        - if the user failed and can retry the id check step, return the retry identity check banner
        - if the user was a 15-17 beneficiary, and is eligible for the 18yo grant, return the birthday activation banner
        - Else, return the default activation banner
    """

    if not user.age:
        return None

    if subscription_api.should_retry_identity_check(user_subscription_state):
        return serializers.Banner(
            name=serializers.BannerName.RETRY_IDENTITY_CHECK_BANNER,
            title=serializers.BannerTitle.RETRY_IDENTITY_CHECK_BANNER.value,
            text=serializers.BannerText.RETRY_IDENTITY_CHECK_BANNER.value,
        )

    eligibility_to_activate = eligibility_api.get_pre_decree_or_current_eligibility(user)
    amount_to_display = finance_conf.get_credit_amount_per_age_and_eligibility(user.age, eligibility_to_activate)
    if amount_to_display is None:
        return None

    if _is_17_18_transition(user):
        return _get_17_18_transition_banner_information(user, amount_to_display)

    return serializers.Banner(
        name=serializers.BannerName.ACTIVATION_BANNER,
        title=serializers.BannerTitle.ACTIVATION_BANNER.value.format(f"{amount_to_display}{u_nbsp}"),
        text=serializers.BannerText.ACTIVATION_BANNER.value,
    )
