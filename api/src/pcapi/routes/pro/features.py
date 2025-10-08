from pcapi.models import db
from pcapi.models.feature import Feature
from pcapi.routes.apis import public_api
from pcapi.routes.serialization import features_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import blueprint


@public_api.route("/features", methods=["GET"])
@atomic()
@spectree_serialize(response_model=features_serialize.ListFeatureResponseModel, api=blueprint.pro_private_schema)
def list_features() -> features_serialize.ListFeatureResponseModel:
    features = db.session.query(Feature).all()
    return features_serialize.ListFeatureResponseModel(
        [features_serialize.FeatureResponseModel.model_validate(feature) for feature in features]
    )
