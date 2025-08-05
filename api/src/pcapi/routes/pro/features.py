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
    # Pydantic manages to convert a list of Feature to a list of FeatureResponseModel, with orm_mode=True
    # This apparently confuses mypy
    return features_serialize.ListFeatureResponseModel(__root__=features)
