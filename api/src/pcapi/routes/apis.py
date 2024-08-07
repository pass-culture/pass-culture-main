from flask import Blueprint
from flask_cors import CORS

from pcapi import settings
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


PUBLIC_API_BLUEPRINT_NAME = "Public API"
PRIVATE_API_BLUEPRINT_NAME = "Private API"

public_api = Blueprint(PUBLIC_API_BLUEPRINT_NAME, __name__)
CORS(public_api, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

private_api = Blueprint(PRIVATE_API_BLUEPRINT_NAME, __name__)
CORS(
    private_api,
    origins=settings.CORS_ALLOWED_ORIGINS,
    supports_credentials=True,
)

api = ExtendedSpecTree(
    "flask",
    MODE="strict",
    before=before_handler,
    version=1,
    humanize_operation_id=True,
)
# This will register all routes from the 2 Blueprints in this file
api.register(public_api)
