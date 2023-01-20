from flask import Blueprint
import flask_cors
import spectree

from pcapi.serialization import utils as serialization_utils
from pcapi.serialization.spec_tree import ExtendedSpecTree

from .individual_offers import blueprint


public_blueprint = Blueprint("public_blueprint", __name__, url_prefix="/public")
public_blueprint.register_blueprint(blueprint.individual_offers_blueprint)


v2_prefixed_public_api = Blueprint("pro_public_api_v2", __name__, url_prefix="/v2")
flask_cors.CORS(v2_prefixed_public_api, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

API_KEY_AUTH = "ApiKeyAuth"
COOKIE_AUTH = "SessionAuth"

v2_prefixed_public_api_schema = ExtendedSpecTree(
    "flask",
    title="pass Culture pro public API v2",
    MODE="strict",
    before=serialization_utils.before_handler,
    PATH="/",
    security_schemes=[
        spectree.SecurityScheme(
            name=API_KEY_AUTH, data={"type": "http", "scheme": "bearer", "description": "Api key issued by passculture"}
        ),
        spectree.SecurityScheme(name=COOKIE_AUTH, data={"type": "apiKey", "in": "cookie", "name": "session"}),
    ],
    humanize_operation_id=True,
    version=2,
)
v2_prefixed_public_api_schema.register(v2_prefixed_public_api)
