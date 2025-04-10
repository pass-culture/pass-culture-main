from pcapi.core.users import constants
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.serialization.decorator import spectree_serialize
from pcapi.settings import OBJECT_STORAGE_URL
from pcapi.utils import postal_code

from .. import blueprint
from .serialization import settings as serializers


def _get_features(*requested_features: FeatureToggle) -> dict[FeatureToggle, bool]:
    requested_features_by_name = {feature.name: feature for feature in requested_features}
    return {
        requested_features_by_name[db_feature.name]: db_feature.isActive
        for db_feature in feature_queries.find_all()
        if db_feature.name in requested_features_by_name
    }


@blueprint.native_route("/settings", methods=["GET"])
@spectree_serialize(api=blueprint.api, response_model=serializers.SettingsResponse)
def get_settings() -> serializers.SettingsResponse:
    features = _get_features(
        FeatureToggle.DISPLAY_DMS_REDIRECTION,
        FeatureToggle.ENABLE_FRONT_IMAGE_RESIZING,
        FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA,
        FeatureToggle.ENABLE_NATIVE_CULTURAL_SURVEY,
        FeatureToggle.ENABLE_PHONE_VALIDATION,
        FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION,
        FeatureToggle.APP_ENABLE_AUTOCOMPLETE,
    )

    return serializers.SettingsResponse(
        account_creation_minimum_age=constants.ACCOUNT_CREATION_MINIMUM_AGE,
        account_unsuspension_limit=constants.ACCOUNT_UNSUSPENSION_DELAY,
        app_enable_autocomplete=features[FeatureToggle.APP_ENABLE_AUTOCOMPLETE],
        display_dms_redirection=features[FeatureToggle.DISPLAY_DMS_REDIRECTION],
        enable_front_image_resizing=features[FeatureToggle.ENABLE_FRONT_IMAGE_RESIZING],
        enable_native_cultural_survey=features[FeatureToggle.ENABLE_NATIVE_CULTURAL_SURVEY],
        enable_phone_validation=features[FeatureToggle.ENABLE_PHONE_VALIDATION],
        id_check_address_autocompletion=features[FeatureToggle.ID_CHECK_ADDRESS_AUTOCOMPLETION],
        ineligible_postal_codes=postal_code.INELIGIBLE_POSTAL_CODES,
        is_recaptcha_enabled=features[FeatureToggle.ENABLE_NATIVE_APP_RECAPTCHA],
        object_storage_url=OBJECT_STORAGE_URL,
        # TODO: remove when the app does not use the feature flag anymore PC-35597
        wip_enable_credit_v3=True,
        deposit_amounts_by_age=serializers.get_deposit_amounts_by_age(),
    )
