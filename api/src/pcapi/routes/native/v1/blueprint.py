from flask import Blueprint
from flask_cors.extension import CORS
from spectree import SecurityScheme
from spectree import SpecTree

from pcapi import settings
from pcapi.routes.native import utils
from pcapi.serialization.utils import before_handler


native_v1 = Blueprint("native_v1", __name__)
native_v1.before_request(utils.check_client_version)
CORS(
    native_v1,
    origins=settings.CORS_ALLOWED_ORIGINS_NATIVE,
    supports_credentials=True,
)


JWT_AUTH = "JWTAuth"

SECURITY_SCHEMES = [
    SecurityScheme(name=JWT_AUTH, data={"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}),
]


api = SpecTree("flask", MODE="strict", before=before_handler, PATH="/", security_schemes=SECURITY_SCHEMES)
api.register(native_v1)
