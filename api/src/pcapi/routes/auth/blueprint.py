from flask import Blueprint
from flask_cors import CORS

from pcapi import settings
from pcapi.routes.auth import utils
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


auth_blueprint = Blueprint("auth", __name__, template_folder="templates")
CORS(
    auth_blueprint,
    origins=settings.CORS_ALLOWED_ORIGINS_AUTH,
    supports_credentials=True,
)
auth_web = ExtendedSpecTree("flask", MODE="strict", before=before_handler, PATH="/")
auth_web.register(auth_blueprint)


@auth_blueprint.context_processor
def extra_funcs() -> dict:
    return {
        "random_hash": utils.random_hash,
    }
