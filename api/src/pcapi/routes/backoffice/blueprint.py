from flask import Blueprint
from flask_cors import CORS
from spectree import SecurityScheme
from spectree import SecuritySchemeData

from pcapi import settings
from pcapi.core.permissions import models as perm_models
from pcapi.routes.backoffice.utils import access_control
from pcapi.routes.backoffice.utils import extra_funcs as extra
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler

from .forms import empty as empty_forms
from .utils import menu
from .utils import static as static_utils
from .utils.access_control import _check_any_permission_of


BACKOFFICE_WEB_BLUEPRINT_NAME = "backoffice_web"
backoffice_web = Blueprint(BACKOFFICE_WEB_BLUEPRINT_NAME, __name__, url_prefix="/", template_folder="templates")
CORS(
    backoffice_web,
    origins=settings.CORS_ALLOWED_ORIGINS,
    supports_credentials=True,
)


COOKIE_AUTH = "SessionAuth"


SECURITY_SCHEMES = [
    SecurityScheme(
        name=COOKIE_AUTH, data=SecuritySchemeData.parse_obj({"type": "apiKey", "in": "cookie", "name": "session"})
    ),
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
        "has_permission": access_control.has_current_user_permission,
        "is_feature_active": extra.is_feature_active,
        "random_hash": extra.random_hash,
        "get_setting": extra.get_setting,
        "static_hashes": static_utils.get_hashes(),
        "menu": menu.get_menu_sections(),
    }


def child_backoffice_blueprint(
    name: str, import_name: str, url_prefix: str, permission: perm_models.Permissions | None = None
) -> Blueprint:
    child_blueprint = Blueprint(name, import_name, url_prefix=url_prefix)
    backoffice_web.register_blueprint(child_blueprint)

    @child_blueprint.before_request
    def check_permission() -> None:
        if permission:
            _check_any_permission_of((permission,))

    return child_blueprint
