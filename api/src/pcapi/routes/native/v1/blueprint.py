from flask import Blueprint
from flask_cors.extension import CORS
from spectree import SecurityScheme

from pcapi import settings
from pcapi.routes.native import utils
from pcapi.routes.utils import tag_with_stream_name
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


native_v1 = Blueprint("native_v1", __name__)
native_v1.before_request(utils.check_client_version)
native_v1.before_request(lambda: tag_with_stream_name("jeunes"))
CORS(
    native_v1,
    origins=settings.CORS_ALLOWED_ORIGINS_NATIVE,
    supports_credentials=True,
)


JWT_AUTH = "JWTAuth"

SECURITY_SCHEMES = [
    SecurityScheme(name=JWT_AUTH, data={"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}),
]


api = ExtendedSpecTree("flask", MODE="strict", before=before_handler, PATH="/", security_schemes=SECURITY_SCHEMES)
api.register(native_v1)
