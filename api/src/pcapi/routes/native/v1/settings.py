from pcapi.core.users import constants
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.serialization.decorator import spectree_serialize
from pcapi.settings import OBJECT_STORAGE_URL

from . import blueprint
from .serialization import settings as serializers


def _get_features(*requested_features: FeatureToggle):  # type: ignore [no-untyped-def]
    requested_features = {feature.name: feature for feature in requested_features}  # type: ignore [assignment]
    return {
        requested_features[db_feature.name]: db_feature.isActive
        for db_feature in feature_queries.find_all()
        if db_feature.name in requested_features
    }


@blueprint.native_v1.route("/settings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.SettingsResponse)
def get_settings() -> serializers.SettingsResponse:

    features = _get_features(
        FeatureToggle.DISPLAY_DMS_REDIRECTION,
        FeatureToggle.ENABLE_FRONT_IMAGE_RESIZING,
        FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA,
        FeatureToggle.ENABLE_NATIVE_CULTURAL_SURVEY,
        FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING,
        FeatureToggle.ENABLE_NEW_IDENTIFICATION_FLOW,
        FeatureToggle.ENABLE_PHONE_VALIDATION,
        FeatureToggle.ENABLE_USER_PROFILING,
        FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION,
        FeatureToggle.PRO_DISABLE_EVENTS_QRCODE,
        FeatureToggle.APP_ENABLE_AUTOCOMPLETE,
        FeatureToggle.APP_ENABLE_CATEGORY_FILTER_PAGE,
        FeatureToggle.APP_ENABLE_COOKIES_V2,
    )

    return serializers.SettingsResponse(
        account_creation_minimum_age=constants.ACCOUNT_CREATION_MINIMUM_AGE,
        # FIXME (ahello, 2022-02-16): remove `auto_activate_digital_bookings`
        # once all alive versions of the app works without this setting.
        auto_activate_digital_bookings=True,
        app_enable_autocomplete=features[FeatureToggle.APP_ENABLE_AUTOCOMPLETE],
        app_enable_category_filter_page=features[FeatureToggle.APP_ENABLE_CATEGORY_FILTER_PAGE],
        display_dms_redirection=features[FeatureToggle.DISPLAY_DMS_REDIRECTION],
        enable_front_image_resizing=features[FeatureToggle.ENABLE_FRONT_IMAGE_RESIZING],
        # TODO: lixxday: remove after the next forced app release (forced release > 1.176.0)
        enable_native_eac_individual=True,
        enable_native_cultural_survey=features[FeatureToggle.ENABLE_NATIVE_CULTURAL_SURVEY],
        enable_native_id_check_verbose_debugging=features[FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING],
        # TODO(anoukhello): remove enable_new_identification_flow when the flow is adopted by all users (PC-17223)
        enable_new_identification_flow=features[FeatureToggle.ENABLE_NEW_IDENTIFICATION_FLOW],
        enable_phone_validation=features[FeatureToggle.ENABLE_PHONE_VALIDATION],
        # TODO: lixxday: remove after the next forced app release (forced release > 1.176.0)
        enable_underage_generalisation=True,
        enable_user_profiling=features[FeatureToggle.ENABLE_USER_PROFILING],
        id_check_address_autocompletion=features[FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION],
        is_recaptcha_enabled=features[FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA],
        # TODO(antoinewg): remove this after next forced release (> v1.166.3)
        # the last forced release v1.166.3 was not future proof enough to delete yet in this PR.
        is_webapp_v2_enabled=True,
        object_storage_url=OBJECT_STORAGE_URL,
        pro_disable_events_qrcode=features[FeatureToggle.PRO_DISABLE_EVENTS_QRCODE],
        account_unsuspension_limit=constants.ACCOUNT_UNSUSPENSION_DELAY,
        app_enable_cookies_v2=features[FeatureToggle.APP_ENABLE_COOKIES_V2],
    )
