from pcapi.models import db
from pcapi.models.feature import Feature
from pcapi.models.feature import FeatureToggle
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.serialization import features_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic


ADAGE_FEATURES = (FeatureToggle.ENABLE_MARSEILLE,)


@blueprint.adage_iframe.route("/features", methods=["GET"])
@atomic()
@spectree_serialize(
    response_model=features_serialize.ListFeatureResponseModel, api=blueprint.api, on_error_statuses=[404]
)
@adage_jwt_required
def list_features(authenticated_information: AuthenticatedInformation) -> features_serialize.ListFeatureResponseModel:
    all_features = db.session.query(Feature)
    requested_features = {feature.name for feature in ADAGE_FEATURES}

    features = [
        features_serialize.FeatureResponseModel.model_validate(db_feature)
        for db_feature in all_features
        if db_feature.name in requested_features
    ]

    return features_serialize.ListFeatureResponseModel(features)
