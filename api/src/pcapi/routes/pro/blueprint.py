from flask import Blueprint
from flask_cors import CORS
from spectree import SecurityScheme

from pcapi import settings
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


pro_public_api_v1 = Blueprint("pro_public_api_v1", __name__)
CORS(
    pro_public_api_v1,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)


pro_public_api_v2 = Blueprint("pro_public_api_v2", __name__)
CORS(
    pro_public_api_v2,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)


pro_private_api = Blueprint("pro_private_api", __name__)
CORS(
    pro_private_api,
    origins=settings.CORS_ALLOWED_ORIGINS,
    supports_credentials=True,
)


API_KEY_AUTH = "ApiKeyAuth"
COOKIE_AUTH = "SessionAuth"


SECURITY_SCHEMES = [
    SecurityScheme(
        name=API_KEY_AUTH, data={"type": "http", "scheme": "bearer", "description": "Api key issued by passculture"}
    ),
    SecurityScheme(name=COOKIE_AUTH, data={"type": "apiKey", "in": "cookie", "name": "session"}),
]


pro_public_schema_v2 = ExtendedSpecTree(
    "flask",
    title="pass Culture pro public API v2",
    MODE="strict",
    before=before_handler,
    PATH="/",
    security_schemes=SECURITY_SCHEMES,
    humanize_operation_id=True,
    version=2,
)
pro_public_schema_v2.register(pro_public_api_v2)


pro_private_schema = ExtendedSpecTree(
    "flask",
    title="pass Culture pro private API",
    MODE="strict",
    before=before_handler,
    PATH="pro",
    security_schemes=SECURITY_SCHEMES,
    humanize_operation_id=True,
    version=1,
)
pro_private_schema.register(pro_private_api)
