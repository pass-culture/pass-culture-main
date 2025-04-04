from flask import Blueprint
from flask_cors import CORS
from spectree import SecurityScheme

from pcapi import settings
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler

from . import menu
from . import static_utils
from . import utils
from .forms import empty as empty_forms


BACKOFFICE_WEB_BLUEPRINT_NAME = "backoffice_web"
backoffice_web = Blueprint(BACKOFFICE_WEB_BLUEPRINT_NAME, __name__, url_prefix="/", template_folder="templates")
CORS(
    backoffice_web,
    origins=settings.CORS_ALLOWED_ORIGINS,
    supports_credentials=True,
)


COOKIE_AUTH = "SessionAuth"


SECURITY_SCHEMES = [
    SecurityScheme(name=COOKIE_AUTH, data={"type": "apiKey", "in": "cookie", "name": "session"}),  # type: ignore[arg-type]
]


backoffice_web_schema = ExtendedSpecTree(
    "flask",
    title="pass Culture poc backoffice web",
    MODE="strict",
    before=before_handler,
    PATH="bo",
    security_schemes=SECURITY_SCHEMES,
    humanize_operation_id=True,
    version=1,
)
backoffice_web_schema.register(backoffice_web)


@backoffice_web.context_processor
def extra_funcs() -> dict:
    return {
        "csrf_token": empty_forms.EmptyForm().csrf_token,
        "has_permission": utils.has_current_user_permission,
        "is_feature_active": utils.is_feature_active,
        "is_user_offerer_action_type": utils.is_user_offerer_action_type,
        "random_hash": utils.random_hash,
        "get_setting": utils.get_setting,
        "static_hashes": static_utils.get_hashes(),
        "menu": menu.get_menu_sections(),
    }
