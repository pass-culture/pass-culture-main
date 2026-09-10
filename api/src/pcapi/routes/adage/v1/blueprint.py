from flask import Blueprint
from spectree import SecurityScheme
from spectree import SecuritySchemeData

from pcapi.routes.adage.blueprint import adage_blueprint
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


adage_v1 = Blueprint("adage_v1", __name__, url_prefix="/v1")
adage_blueprint.register_blueprint(adage_v1)


EAC_API_KEY_AUTH = "ApiKeyAuth"

SECURITY_SCHEMES = [
    SecurityScheme(
        name=EAC_API_KEY_AUTH,
        data=SecuritySchemeData.parse_obj(
            {"type": "http", "scheme": "bearer", "description": "API key shared by Adage and pass Culture"}
        ),
    ),
]


api = ExtendedSpecTree("flask", MODE="strict", before=before_handler, PATH="/", security_schemes=SECURITY_SCHEMES)
api.register(adage_v1)
