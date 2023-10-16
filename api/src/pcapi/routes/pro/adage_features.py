from pcapi.repository import feature_queries
from pcapi.routes.pro import adage_blueprint
from pcapi.routes.pro.adage_security import adage_jwt_required
from pcapi.routes.serialization import features_serialize
from pcapi.routes.serialization.adage_authentication import AuthenticatedInformation
from pcapi.serialization.decorator import spectree_serialize


@adage_blueprint.adage_iframe.route("/features", methods=["GET"])
@spectree_serialize(
    response_model=features_serialize.ListFeatureResponseModel, api=adage_blueprint.api, on_error_statuses=[404]
)
@adage_jwt_required
def list_features(authenticated_information: AuthenticatedInformation) -> features_serialize.ListFeatureResponseModel:
    features = feature_queries.find_all()
    # Pydantic manages to convert a list of Feature to a list of FeatureResponseModel, with orm_mode=True
    # This apparently confuses mypy
    return features_serialize.ListFeatureResponseModel(__root__=features)  # type: ignore [arg-type]
