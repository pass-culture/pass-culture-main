import logging

from pcapi import settings
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import Feature
from pcapi.serialization.decorator import spectree_serialize

from . import blueprint
from .serialization import features_toggle as serializers


logger = logging.getLogger(__name__)


@blueprint.native_v1.route("/features", methods=["PATCH"])
@spectree_serialize(
    on_success_status=204,
    api=blueprint.api,
)
def toggle_feature_toggles(body: serializers.FeaturesToggleRequest) -> None:
    if not (settings.IS_DEV or settings.IS_RUNNING_TESTS):
        raise ApiErrors({"code": "not found"}, status_code=404)
    for feature in body.features:
        Feature.query.filter_by(name=feature.name).update({"isActive": feature.isActive})
        db.session.commit()
