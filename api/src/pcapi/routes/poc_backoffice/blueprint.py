from flask import Blueprint
from flask_cors import CORS
from spectree import SecurityScheme

from pcapi import settings
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


poc_backoffice_web = Blueprint(
    "poc_backoffice_web",
    __name__,
    template_folder="templates"
)
CORS(
    poc_backoffice_web,
    origins=settings.CORS_ALLOWED_ORIGINS,
    supports_credentials=True,
)


COOKIE_AUTH = "SessionAuth"


SECURITY_SCHEMES = [
    SecurityScheme(name=COOKIE_AUTH, data={"type": "apiKey", "in": "cookie", "name": "session"}),
]


poc_backoffice_web_schema = ExtendedSpecTree(
    "flask",
    title="pass Culture poc backoffice web",
    MODE="strict",
    before=before_handler,
    PATH="pocbo",
    security_schemes=SECURITY_SCHEMES,
    humanize_operation_id=True,
    version=1,
)
poc_backoffice_web_schema.register(poc_backoffice_web)
