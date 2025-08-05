from pcapi.models import db
from pcapi.models.feature import Feature
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.serialization import features_serialize
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic


@blueprint.adage_iframe.route("/features", methods=["GET"])
@atomic()
@spectree_serialize(
    response_model=features_serialize.ListFeatureResponseModel, api=blueprint.api, on_error_statuses=[404]
)
@adage_jwt_required
def list_features(authenticated_information: AuthenticatedInformation) -> features_serialize.ListFeatureResponseModel:
    features = db.session.query(Feature).all()
    # Pydantic manages to convert a list of Feature to a list of FeatureResponseModel, with orm_mode=True
    # This apparently confuses mypy
    return features_serialize.ListFeatureResponseModel(__root__=features)
