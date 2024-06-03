from flask import Blueprint
from spectree import SecurityScheme

from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


adage_v1 = Blueprint("adage_v1", __name__)


EAC_API_KEY_AUTH = "ApiKeyAuth"

SECURITY_SCHEMES = [
    SecurityScheme(
        name=EAC_API_KEY_AUTH,
        data={"type": "http", "scheme": "bearer", "description": "API key shared by Adage and pass Culture"},  # type: ignore[arg-type]
    ),
]


api = ExtendedSpecTree("flask", MODE="strict", before=before_handler, PATH="/", security_schemes=SECURITY_SCHEMES)
api.register(adage_v1)
