from flask import Blueprint
from flask_cors import CORS

from pcapi import settings
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


public_api = Blueprint("Public API", __name__)
CORS(public_api, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

private_api = Blueprint("Private API", __name__)
CORS(
    private_api,
    origins=settings.CORS_ALLOWED_ORIGINS,
    supports_credentials=True,
)

api = ExtendedSpecTree("flask", MODE="strict", before=before_handler, PATH="/", version=1)
api.register(public_api)
