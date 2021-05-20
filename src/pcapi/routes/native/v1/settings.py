from pcapi.core.bookings import conf
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.serialization.decorator import spectree_serialize
from pcapi.settings import OBJECT_STORAGE_URL

from . import blueprint
from .serialization import settings as serializers


@blueprint.native_v1.route("/settings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.SettingsResponse)
def get_settings() -> serializers.SettingsResponse:
    current_deposit_version = conf.get_current_deposit_version()
    booking_configuration = conf.LIMIT_CONFIGURATIONS[current_deposit_version]

    return serializers.SettingsResponse(
        deposit_amount=booking_configuration.TOTAL_CAP,
        is_recaptcha_enabled=feature_queries.is_active(FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA),
        allow_id_check_registration=feature_queries.is_active(FeatureToggle.ALLOW_IDCHECK_REGISTRATION),
        auto_activate_digital_bookings=feature_queries.is_active(FeatureToggle.AUTO_ACTIVATE_DIGITAL_BOOKINGS),
        enable_native_id_check_version=feature_queries.is_active(FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERSION),
        enable_phone_validation=feature_queries.is_active(FeatureToggle.ENABLE_PHONE_VALIDATION),
        whole_france_opening=feature_queries.is_active(FeatureToggle.WHOLE_FRANCE_OPENING),
        display_dms_redirection=feature_queries.is_active(FeatureToggle.DISPLAY_DMS_REDIRECTION),
        object_storage_url=OBJECT_STORAGE_URL,
    )
