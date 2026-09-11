from flask import Blueprint
from flask_cors import CORS
from spectree import SecurityScheme
from spectree import SecuritySchemeData

from pcapi import settings
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


pro_blueprint = Blueprint("pro", __name__)
CORS(
    pro_blueprint,
    origins=settings.CORS_ALLOWED_ORIGINS,
    supports_credentials=True,
)

COOKIE_AUTH_NAME = "SessionAuth"

SECURITY_SCHEMES = [
    SecurityScheme(
        name=COOKIE_AUTH_NAME,
        data=SecuritySchemeData.parse_obj({"type": "apiKey", "in": "cookie", "name": "session"}),
    ),
]


pro_schema = ExtendedSpecTree(
    "flask",
    title="pass Culture pro private API",
    MODE="strict",
    before=before_handler,
    PATH="pro",
    security_schemes=SECURITY_SCHEMES,
    humanize_operation_id=True,
    version=1,
)
pro_schema.register(pro_blueprint)
