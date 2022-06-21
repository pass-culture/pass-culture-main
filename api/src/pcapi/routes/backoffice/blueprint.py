from flask import Blueprint
from flask_cors import CORS

from pcapi import settings
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


backoffice_blueprint = Blueprint("backoffice_blueprint", __name__)
CORS(
    backoffice_blueprint,
    origins=settings.CORS_ALLOWED_ORIGINS_BACKOFFICE,
    supports_credentials=True,
)


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
