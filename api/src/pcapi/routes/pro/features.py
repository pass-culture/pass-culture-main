from pcapi.models import db
from pcapi.models.feature import Feature
from pcapi.models.feature import FeatureToggle
from pcapi.routes.apis import public_api
from pcapi.routes.serialization import features_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


PRO_FEATURES = (
    FeatureToggle.API_SIRENE_AVAILABLE,
    FeatureToggle.ENABLE_BEAMER,
    FeatureToggle.ENABLE_MARSEILLE,
    FeatureToggle.ENABLE_PRO_ACCOUNT_CREATION,
    FeatureToggle.ENABLE_PRO_FEEDBACK,
    FeatureToggle.WIP_PRO_AUTONOMOUS_ANONYMIZATION,
    FeatureToggle.WIP_RESTRICT_VENUE_CREATION_TO_COLLECTIVITY,
    FeatureToggle.WIP_SWITCH_VENUE,
    FeatureToggle.WIP_ENABLE_OHO,
    FeatureToggle.WIP_VENUE_CULTURAL_DOMAINS,
    FeatureToggle.WIP_ENABLE_NEW_PRO_HOME,
)


@public_api.route("/features", methods=["GET"])
@atomic()
@spectree_serialize(response_model=features_serialize.ListFeatureResponseModel, api=blueprint.pro_private_schema)
def list_features() -> features_serialize.ListFeatureResponseModel:
    all_features = db.session.query(Feature)
    requested_features = {feature.name for feature in PRO_FEATURES}

    features = [
        features_serialize.FeatureResponseModel.model_validate(db_feature)
        for db_feature in all_features
        if db_feature.name in requested_features
    ]

    return features_serialize.ListFeatureResponseModel(features)
