from flask import Blueprint
from flask import current_app
from flask import request
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import UnsupportedMediaType

from pcapi.models import api_errors

# Spectree schemas
from . import spectree_schemas


def _is_route_reading_json() -> bool:
    endpoint_name = request.url_rule.endpoint if request.url_rule else None
    endpoint_function = current_app.view_functions.get(endpoint_name)
    return endpoint_function and "body" in endpoint_function.__annotations__


def _check_api_is_enabled_and_json_valid() -> None:
    # We test the json validity because pydantic will not raise an error if the json is not valid.
    # Pydantic will then try to apply the validation schema and throws unintelligible errors.
    if _is_route_reading_json():
        # only test if data are present
        try:
            _ = request.get_json()
        except (BadRequest, UnsupportedMediaType) as e:
            raise api_errors.ApiErrors({"global": [e.description]}, status_code=400)


public_api = Blueprint("public_api", __name__, url_prefix="/")  # we must add `url_prefix="/"` for spectree to work
public_api.before_request(_check_api_is_enabled_and_json_valid)


# Deprecated collective endpoints
deprecated_collective_public_api = Blueprint("public_api_deprecated", __name__, url_prefix="/")

# Setting CORS
CORS(
    public_api,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)
CORS(
    deprecated_collective_public_api,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)

# Registering spectree schemas
spectree_schemas.public_api_schema.register(public_api)
spectree_schemas.deprecated_collective_public_api_schema.register(deprecated_collective_public_api)
