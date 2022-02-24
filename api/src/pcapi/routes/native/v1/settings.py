from pcapi.core.users import constants
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

    features = _get_features(
        FeatureToggle.AUTO_ACTIVATE_DIGITAL_BOOKINGS,
        FeatureToggle.DISPLAY_DMS_REDIRECTION,
        FeatureToggle.ENABLE_ID_CHECK_RETENTION,
        FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA,
        FeatureToggle.ENABLE_NATIVE_EAC_INDIVIDUAL,
        FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING,
        FeatureToggle.ENABLE_PHONE_VALIDATION,
        FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION,
    )

    return serializers.SettingsResponse(
        account_creation_minimum_age=constants.ACCOUNT_CREATION_MINIMUM_AGE,
        auto_activate_digital_bookings=features[FeatureToggle.AUTO_ACTIVATE_DIGITAL_BOOKINGS],
        display_dms_redirection=features[FeatureToggle.DISPLAY_DMS_REDIRECTION],
        enable_id_check_retention=features[FeatureToggle.ENABLE_ID_CHECK_RETENTION],
        enable_native_eac_individual=features[FeatureToggle.ENABLE_NATIVE_EAC_INDIVIDUAL],
        enable_native_id_check_verbose_debugging=features[FeatureToggle.ENABLE_NATIVE_ID_CHECK_VERBOSE_DEBUGGING],
        enable_phone_validation=features[FeatureToggle.ENABLE_PHONE_VALIDATION],
        # TODO: lixxday: remove after the next forced app release (last forced release: 1.176.0)
        enable_underage_generalisation=True,
        id_check_address_autocompletion=features[FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION],
        is_recaptcha_enabled=features[FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA],
        # TODO(antoinewg): remove this after next forced release (> v1.166.3)
        # the last forced release v1.166.3 was not future proof enough to delete yet in this PR.
        is_webapp_v2_enabled=True,
        object_storage_url=OBJECT_STORAGE_URL,
    )
