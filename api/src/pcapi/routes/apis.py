from flask import Blueprint
from flask_cors import CORS

from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import before_handler


misc_blueprint = Blueprint("misc", __name__)
CORS(misc_blueprint, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

api = ExtendedSpecTree(
    "flask",
    MODE="strict",
    before=before_handler,
    version=1,
    humanize_operation_id=True,
)
# This will register all routes from the 2 Blueprints in this file ..
api.register(misc_blueprint)
