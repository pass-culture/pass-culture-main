import logging

from pcapi import settings
from pcapi.core.educational.utils import create_adage_jwt_fake_valid_token
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import Feature
from pcapi.repository.session_management import atomic
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.apis import public_api
from pcapi.routes.serialization import BaseModel
from pcapi.serialization.decorator import spectree_serialize

from . import serializers


logger = logging.getLogger(__name__)


@public_api.route("/testing/features", methods=["PATCH"])
@atomic()
@spectree_serialize(on_success_status=204)
def set_features(body: serializers.FeaturesToggleRequest) -> None:
    if not settings.ENABLE_TEST_ROUTES:
        raise ApiErrors({"code": "not found"}, status_code=404)

    for feature in body.features:
        db.session.query(Feature).filter_by(name=feature.name).update({"isActive": feature.isActive})


class AdageFakeToken(BaseModel):
    token: str


@blueprint.adage_iframe.route("/testing/token", methods=["GET"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404])
def create_adage_jwt_fake_token() -> AdageFakeToken:
    if not settings.ENABLE_TEST_ROUTES:
        raise ApiErrors({"code": "not found"}, status_code=404)
    return AdageFakeToken(token=create_adage_jwt_fake_valid_token(False))
