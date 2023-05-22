import logging

from pcapi import settings
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import Feature
from pcapi.routes import apis
from pcapi.serialization.decorator import spectree_serialize

from . import serializers


logger = logging.getLogger(__name__)


@apis.public_api.route("/testing/features", methods=["PATCH"])
@spectree_serialize(on_success_status=204, api=apis.api)
def set_features(body: serializers.FeaturesToggleRequest) -> None:
    if not (settings.IS_DEV or settings.IS_RUNNING_TESTS):
        raise ApiErrors({"code": "not found"}, status_code=404)
    for feature in body.features:
        Feature.query.filter_by(name=feature.name).update({"isActive": feature.isActive})
        db.session.commit()
