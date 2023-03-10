import pcapi.core.finance.conf as finance_conf
import pcapi.core.subscription.api as subscription_api
import pcapi.core.subscription.models as subscription_models
import pcapi.routes.native.v1.serialization.banner as serializers


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
    user_subscription_state: subscription_models.UserSubscriptionState, user_age: int | None, is_geolocated: bool
) -> serializers.Banner | None:
    banner = None
    if user_subscription_state.next_step in ACTIVATION_BANNER_NEXT_STEPS:
        banner = _get_activation_banner(user_age, user_subscription_state)
    elif not is_geolocated:
        banner = GEOLOCATION_BANNER

    return banner


def _get_activation_banner(
    user_age: int | None, user_subscription_state: subscription_models.UserSubscriptionState
) -> serializers.Banner | None:
    if not user_age:
        return None

    if subscription_api.should_retry_identity_check(user_subscription_state):
        return serializers.Banner(
            name=serializers.BannerName.RETRY_IDENTITY_CHECK_BANNER,
            title=serializers.BannerTitle.RETRY_IDENTITY_CHECK_BANNER.value,
            text=serializers.BannerText.RETRY_IDENTITY_CHECK_BANNER.value,
        )

    amount_to_display = finance_conf.get_amount_to_display(user_age)

    if amount_to_display is None:
        return None

    return serializers.Banner(
        name=serializers.BannerName.ACTIVATION_BANNER,
        title=serializers.BannerTitle.ACTIVATION_BANNER.value.format(amount_to_display),
        text=serializers.BannerText.ACTIVATION_BANNER.value,
    )
