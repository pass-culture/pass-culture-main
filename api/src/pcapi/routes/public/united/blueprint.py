from flask import Blueprint
import flask_cors
import spectree

from pcapi.serialization import utils as serialization_utils
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.validation.routes import users_authentifications


public_api_blueprint = Blueprint("public_api", __name__, url_prefix="/oops")
flask_cors.CORS(public_api_blueprint, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

public_api_schema = ExtendedSpecTree(
    "flask",
    title="pass Culture pro public API",
    description="API publique du pass culture",
    MODE="strict",
    before=serialization_utils.before_handler,
    PATH="/",
    security_schemes=[
        spectree.SecurityScheme(
            name=users_authentifications.API_KEY_AUTH_NAME,
            data={
                "type": "http",
                "scheme": "bearer",
                "description": "Api key issued by passculture",
            },  # type: ignore [arg-type]
        ),
        spectree.SecurityScheme(
            name=users_authentifications.COOKIE_AUTH_NAME,
            data={"type": "apiKey", "in": "cookie", "name": "session"},  # type: ignore [arg-type]
        ),
    ],
    humanize_operation_id=True,
)
public_api_schema.register(public_api_blueprint)
