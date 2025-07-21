from flask import Blueprint
from flask import request
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

from pcapi.models import api_errors

# Spectree schemas
from . import spectree_schemas


def _check_api_is_enabled_and_json_valid() -> None:
    # We test the json validity because pydantic will not raise an error if the json is not valid.
    # Pydantic will then try to apply the validation schema and throws unintelligible errors.
    try:
        _ = request.get_json()
    except BadRequest as e:
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
