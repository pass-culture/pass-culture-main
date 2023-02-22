import decimal

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
    title="Géolocalise-toi",
    text="pour trouver des offres autour de toi",
)


def get_activation_banner(user_age: int | None) -> serializers.Banner | None:
    if not user_age:
        return None

    if user_age == 18:
        amount_to_display: decimal.Decimal | None = finance_conf.GRANTED_DEPOSIT_AMOUNT_18_v2
    else:
        amount_to_display = finance_conf.GRANTED_DEPOSIT_AMOUNTS_FOR_UNDERAGE_BY_AGE.get(user_age)

    if amount_to_display is None:
        return None

    title = f"Débloque tes {amount_to_display}€"

    return serializers.Banner(
        name=serializers.BannerName.ACTIVATION_BANNER,
        title=title,
        text="a dépenser sur l'application",
    )
