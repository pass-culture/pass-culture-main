from pcapi.core.bookings import conf
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.serialization.decorator import spectree_serialize
from pcapi.settings import OBJECT_STORAGE_URL

from . import blueprint
from .serialization import settings as serializers


def _get_features(*requested_features: FeatureToggle):
    requested_features = {feature.name: feature for feature in requested_features}
    return {
        requested_features[db_feature.name]: db_feature.isActive
        for db_feature in feature_queries.find_all()
        if db_feature.name in requested_features
    }


@blueprint.native_v1.route("/settings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.SettingsResponse)
def get_settings() -> serializers.SettingsResponse:
    current_deposit_version = conf.get_current_deposit_version()
    booking_configuration = conf.LIMIT_CONFIGURATIONS[current_deposit_version]

    features = _get_features(
        FeatureToggle.ALLOW_IDCHECK_REGISTRATION,
        FeatureToggle.AUTO_ACTIVATE_DIGITAL_BOOKINGS,
        FeatureToggle.DISPLAY_DMS_REDIRECTION,
        FeatureToggle.ENABLE_ID_CHECK_RETENTION,
        FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA,
        FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING,
        FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERSION,
        FeatureToggle.ENABLE_PHONE_VALIDATION,
        FeatureToggle.USE_APP_SEARCH_ON_NATIVE_APP,
        FeatureToggle.WHOLE_FRANCE_OPENING,
        FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION,
        FeatureToggle.WEBAPP_V2_ENABLED,
        FeatureToggle.ENABLE_NATIVE_EAC_INDIVIDUAL,
    )

    return serializers.SettingsResponse(
        deposit_amount=booking_configuration.TOTAL_CAP,
        is_recaptcha_enabled=features[FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA],
        allow_id_check_registration=features[FeatureToggle.ALLOW_IDCHECK_REGISTRATION],
        auto_activate_digital_bookings=features[FeatureToggle.AUTO_ACTIVATE_DIGITAL_BOOKINGS],
        enable_native_id_check_version=features[FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERSION],
        enable_native_id_check_verbose_debugging=features[FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING],
        enable_id_check_retention=features[FeatureToggle.ENABLE_ID_CHECK_RETENTION],
        enable_phone_validation=features[FeatureToggle.ENABLE_PHONE_VALIDATION],
        whole_france_opening=features[FeatureToggle.WHOLE_FRANCE_OPENING],
        display_dms_redirection=features[FeatureToggle.DISPLAY_DMS_REDIRECTION],
        object_storage_url=OBJECT_STORAGE_URL,
        use_app_search=features[FeatureToggle.USE_APP_SEARCH_ON_NATIVE_APP],
        id_check_address_autocompletion=features[FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION],
        is_webapp_v2_enabled=features[FeatureToggle.WEBAPP_V2_ENABLED],
        enable_native_eac_individual=features[FeatureToggle.ENABLE_NATIVE_EAC_INDIVIDUAL],
    )
