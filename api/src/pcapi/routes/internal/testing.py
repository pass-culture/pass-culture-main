import logging

from pcapi import settings
from pcapi.core.educational.utils import create_adage_jwt_fake_valid_token
from pcapi.models import db
from pcapi.models.api_errors import ResourceNotFoundError
from pcapi.models.feature import Feature
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.apis import public_api
from pcapi.routes.serialization import HttpBodyModel
from pcapi.serialization.decorator import spectree_serialize
from pcapi.utils.transaction_manager import atomic

from . import serializers


logger = logging.getLogger(__name__)


@public_api.route("/testing/features", methods=["PATCH"])
@atomic()
@spectree_serialize(on_success_status=204)
def set_features(body: serializers.FeaturesToggleRequest) -> None:
    if not settings.ENABLE_TEST_ROUTES:
        raise ResourceNotFoundError({"code": "not found"})

    for feature in body.features:
        db.session.query(Feature).filter_by(name=feature.name).update({"isActive": feature.isActive})


class AdageFakeToken(HttpBodyModel):
    token: str


@blueprint.adage_iframe.route("/testing/token", methods=["GET"])
@atomic()
@spectree_serialize(api=blueprint.api, on_error_statuses=[404])
def create_adage_jwt_fake_token() -> AdageFakeToken:
    if not settings.ENABLE_TEST_ROUTES:
        raise ResourceNotFoundError({"code": "not found"})

    try:
        token = create_adage_jwt_fake_valid_token(readonly=False)
    except FileNotFoundError:
        raise ResourceNotFoundError({"code": "not found"})

    return AdageFakeToken(token=token)
