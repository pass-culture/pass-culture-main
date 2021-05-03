from pcapi.core.bookings import conf
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import settings as serializers


@blueprint.native_v1.route("/settings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.SettingsResponse)
def get_settings() -> serializers.SettingsResponse:
    current_deposit_version = conf.get_current_deposit_version()
    booking_configuration = conf.LIMIT_CONFIGURATIONS[current_deposit_version]

    is_recaptcha_enabled = False
    if feature_queries.is_active(FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA):
        is_recaptcha_enabled = True

    return serializers.SettingsResponse(
        deposit_amount=booking_configuration.TOTAL_CAP,
        is_recaptcha_enabled=is_recaptcha_enabled,
    )
