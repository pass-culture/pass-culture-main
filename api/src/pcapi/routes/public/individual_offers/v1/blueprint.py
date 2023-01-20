from flask import Blueprint
from flask_cors import CORS
from spectree import SecurityScheme

from pcapi.models import api_errors
from pcapi.models import feature
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler
from pcapi.validation.routes import users_authentifications


def check_api_is_enabled() -> None:
    if not feature.FeatureToggle.WIP_ENABLE_OFFER_CREATION_API_V1.is_active():
        raise api_errors.ApiErrors({"global": ["This API is not enabled"]}, status_code=400)


v1_blueprint = Blueprint("v1_blueprint", __name__, url_prefix="/v1")
v1_blueprint.before_request(check_api_is_enabled)
CORS(
    v1_blueprint,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)


v1_schema = ExtendedSpecTree(
    "flask",
    title="Offers creation API",
    MODE="strict",
    before=before_handler,
    security_schemes=[
        SecurityScheme(
            name=users_authentifications.API_KEY_AUTH_NAME,
            data={"type": "http", "scheme": "bearer", "description": "Api key issued on passculture.pro"},
        )
    ],
    PATH="/",
    version="1.0",
)
v1_schema.register(v1_blueprint)
