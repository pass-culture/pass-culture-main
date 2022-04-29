from pcapi.repository import feature_queries
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.serialization import features_serialize
from pcapi.serialization.decorator import spectree_serialize


@blueprint.adage_iframe.route("/features", methods=["GET"])
@adage_jwt_required
@spectree_serialize(
    response_model=features_serialize.ListFeatureResponseModel, api=blueprint.api, on_error_statuses=[404]
)
def list_features(authenticated_information: AuthenticatedInformation) -> features_serialize.ListFeatureResponseModel:
    features = feature_queries.find_all()
    return features_serialize.ListFeatureResponseModel(__root__=features)
