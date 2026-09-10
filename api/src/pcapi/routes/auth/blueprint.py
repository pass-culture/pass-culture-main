from flask import Blueprint
from flask_cors import CORS

from pcapi import settings
from pcapi.routes.auth import utils
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


discord_blueprint = Blueprint("discord", __name__, template_folder="templates", url_prefix="/auth/discord")
CORS(
    discord_blueprint,
    origins=settings.CORS_ALLOWED_ORIGINS_AUTH,
    supports_credentials=True,
)
auth_web = ExtendedSpecTree("flask", MODE="strict", before=before_handler, PATH="/")
auth_web.register(discord_blueprint)


@discord_blueprint.context_processor
def extra_funcs() -> dict:
    return {
        "random_hash": utils.random_hash,
        "get_setting": utils.get_setting,
    }
