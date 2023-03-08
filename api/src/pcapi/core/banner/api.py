import pcapi.core.finance.conf as finance_conf
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


def get_activation_banner(user_age: int | None) -> serializers.Banner | None:
    if not user_age:
        return None

    amount_to_display = finance_conf.get_amount_to_display(user_age)

    if amount_to_display is None:
        return None

    return serializers.Banner(
        name=serializers.BannerName.ACTIVATION_BANNER,
        title=serializers.BannerTitle.ACTIVATION_BANNER.value.format(amount_to_display),
        text=serializers.BannerText.ACTIVATION_BANNER.value,
    )
