from flask import Blueprint
from flask_cors.extension import CORS
from spectree import SecurityScheme

from pcapi import settings
from pcapi.routes.native import utils
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


native_blueprint = Blueprint("native", __name__)
native_blueprint.before_request(utils.check_client_version)
CORS(
    native_blueprint,
    origins=settings.CORS_ALLOWED_ORIGINS_NATIVE,
    supports_credentials=True,
)

JWT_AUTH = "JWTAuth"
SECURITY_SCHEMES = [
    SecurityScheme(name=JWT_AUTH, data={"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}),  # type: ignore [arg-type]
]

api = ExtendedSpecTree("flask", MODE="strict", before=before_handler, PATH="/", security_schemes=SECURITY_SCHEMES)


native_v1 = Blueprint("native_v1", __name__)
native_v2 = Blueprint("native_v2", __name__)

native_blueprint.register_blueprint(native_v1, url_prefix="/v1")
native_blueprint.register_blueprint(native_v2, url_prefix="/v2")

api.register(native_blueprint)
