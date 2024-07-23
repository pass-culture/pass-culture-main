from flask import Blueprint
from flask import request
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

from pcapi.models import api_errors

# Spectree schemas
from . import spectree_schemas

# DEPRECATED APIs
from .booking_token import blueprint as booking_token_blueprint
from .books_stocks import blueprint as booking_stocks_blueprint


def _check_api_is_enabled_and_json_valid() -> None:
    # We test the json validity because pydantic will not raise an error if the json is not valid.
    # Pydantic will then try to apply the validation schema and throws unintelligible errors.
    try:
        _ = request.get_json()
    except BadRequest as e:
        raise api_errors.ApiErrors({"global": [e.description]}, status_code=400)


public_api = Blueprint("public_api", __name__, url_prefix="/")  # we must add `url_prefix="/"` for spectree to work
public_api.before_request(_check_api_is_enabled_and_json_valid)


# [OLD] Old tokens and stocks apis
deprecated_v2_prefixed_public_api = Blueprint("deprecated_public_api", __name__, url_prefix="/v2")
deprecated_v2_prefixed_public_api.register_blueprint(booking_token_blueprint.deprecated_booking_token_blueprint)
deprecated_v2_prefixed_public_api.register_blueprint(booking_stocks_blueprint.deprecated_books_stocks_blueprint)

# Setting CORS
CORS(
    public_api,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)
CORS(
    deprecated_v2_prefixed_public_api,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)

# Registering spectree schemas
spectree_schemas.public_api_schema.register(public_api)
spectree_schemas.deprecated_public_api_schema.register(deprecated_v2_prefixed_public_api)
