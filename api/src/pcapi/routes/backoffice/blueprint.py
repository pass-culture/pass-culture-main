from flask import Blueprint
from flask_cors import CORS
from spectree import SecurityScheme

from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


backoffice_blueprint = Blueprint("backoffice_blueprint", __name__)
CORS(
    backoffice_blueprint,
    # FIXME (ASK, 2022/04/12): adapter le CORS resources car c'est sûrement pas
    #  ce qu'on veut au final
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)


JWT_AUTH = "JWTAuth"

SECURITY_SCHEMES = [
    SecurityScheme(name=JWT_AUTH, data={"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}),
]


api = ExtendedSpecTree(
    "flask",
    title="pass Culture backoffice API",
    MODE="strict",
    before=before_handler,
    PATH="/",
    security_schemes=None,  # FIXME (ASK, 2022/04/12): mettre un vrai security scheme ici
    humanize_operation_id=True,
    version=1,
)
api.register(backoffice_blueprint)
