from flask import Blueprint
from flask_cors.extension import CORS
from spectree import SecurityScheme
from spectree import SpecTree

from pcapi import settings
from pcapi.routes.utils import tag_with_stream_name
from pcapi.serialization.utils import before_handler


adage_iframe = Blueprint("adage_iframe", __name__)
adage_iframe.before_request(lambda: tag_with_stream_name("adage"))
CORS(
    adage_iframe,
    origins=settings.CORS_ALLOWED_ORIGINS_ADAGE_IFRAME,
)

JWT_AUTH = "JWTAuth"

SECURITY_SCHEMES = [
    SecurityScheme(name=JWT_AUTH, data={"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}),
]


api = SpecTree(
    "flask",
    title="Pass Culture API accessed through iframe from adage clients",
    MODE="strict",
    before=before_handler,
    PATH="/",
    security_schemes=SECURITY_SCHEMES,
)
api.register(adage_iframe)
