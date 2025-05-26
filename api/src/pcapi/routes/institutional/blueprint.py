from flask import Blueprint
from spectree import SecurityScheme

from pcapi.routes.institutional.security import INSTITUTIONAL_API_KEY_AUTH
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


institutional = Blueprint("institutional", __name__)

SECURITY_SCHEMES = [
    SecurityScheme(
        name=INSTITUTIONAL_API_KEY_AUTH,
        data={"type": "http", "scheme": "bearer", "description": "API key for institutional routes"},  # type: ignore[arg-type]
    ),
]

api = ExtendedSpecTree(
    "flask",
    MODE="strict",
    before=before_handler,
    PATH="/institutional",
    security_schemes=SECURITY_SCHEMES,
)

api.register(institutional)
