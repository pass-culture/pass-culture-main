from pcapi.repository import feature_queries
from pcapi.routes.apis import public_api
from pcapi.routes.serialization import features_serialize
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint


@public_api.route("/features", methods=["GET"])
@spectree_serialize(response_model=features_serialize.ListFeatureResponseModel, api=blueprint.pro_private_schema)
def list_features() -> features_serialize.ListFeatureResponseModel:
    features = feature_queries.find_all()
    # Pydantic manages to convert a list of Feature to a list of FeatureResponseModel, with orm_mode=True
    # This apparently confuses mypy
    return features_serialize.ListFeatureResponseModel(__root__=features)  # type: ignore[arg-type]
