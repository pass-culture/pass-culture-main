from flask import Blueprint
from flask_cors import CORS
from spectree import SecurityScheme

from pcapi import settings
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler
from pcapi.validation.routes import users_authentifications


PRO_PRIVATE_API_BLUEPRINT_NAME = "pro_private_api"


pro_private_api = Blueprint(PRO_PRIVATE_API_BLUEPRINT_NAME, __name__)
CORS(
    pro_private_api,
    origins=settings.CORS_ALLOWED_ORIGINS,
    supports_credentials=True,
)


SECURITY_SCHEMES = [
    SecurityScheme(
        name=users_authentifications.API_KEY_AUTH_NAME,
        data={"type": "http", "scheme": "bearer", "description": "Api key issued by passculture"},  # type: ignore[arg-type]
    ),
    SecurityScheme(
        name=users_authentifications.COOKIE_AUTH_NAME, data={"type": "apiKey", "in": "cookie", "name": "session"}  # type: ignore[arg-type]
    ),
]


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
