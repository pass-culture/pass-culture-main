from flask import Blueprint
from flask_cors import CORS
from spectree import SecurityScheme

from pcapi import settings
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler

from . import utils
from .forms import empty as empty_forms


backoffice_v3_web = Blueprint("backoffice_v3_web", __name__, template_folder="templates")
CORS(
    backoffice_v3_web,
    origins=settings.CORS_ALLOWED_ORIGINS,
    supports_credentials=True,
)


COOKIE_AUTH = "SessionAuth"


SECURITY_SCHEMES = [
    SecurityScheme(name=COOKIE_AUTH, data={"type": "apiKey", "in": "cookie", "name": "session"}),
]


backoffice_v3_web_schema = ExtendedSpecTree(
    "flask",
    title="pass Culture poc backoffice web",
    MODE="strict",
    before=before_handler,
    PATH="bo",
    security_schemes=SECURITY_SCHEMES,
    humanize_operation_id=True,
    version=1,
)
backoffice_v3_web_schema.register(backoffice_v3_web)


@backoffice_v3_web.context_processor
def extra_funcs() -> dict:
    return {
        "csrf_token": empty_forms.EmptyForm().csrf_token,
        "can_user_add_comment": utils.can_user_add_comment,
        "is_user_offerer_action_type": utils.is_user_offerer_action_type,
    }
