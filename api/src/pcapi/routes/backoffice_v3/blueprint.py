from flask import Blueprint
from flask_cors import CORS
from spectree import SecurityScheme

from pcapi import settings
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler

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


@backoffice_v3_web.before_request
def require_ff() -> None:
    if not FeatureToggle.WIP_ENABLE_BACKOFFICE_V3.is_active():
        raise ApiErrors(errors={"feature_flip": ["WIP_ENABLE_BACKOFFICE_V3 n'est pas activé"]})


@backoffice_v3_web.context_processor
def add_logout_csrf_token() -> dict:
    return {"logout_csrf_token": empty_forms.EmptyForm().csrf_token}
