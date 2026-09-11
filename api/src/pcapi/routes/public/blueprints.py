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
    endpoint_function = current_app.view_functions.get(endpoint_name) if endpoint_name is not None else None
    return endpoint_function is not None and "body" in endpoint_function.__annotations__


def _check_api_is_enabled_and_json_valid() -> None:
    # We test the json validity because pydantic will not raise an error if the json is not valid.
    # Pydantic will then try to apply the validation schema and throws unintelligible errors.
    if _is_route_reading_json():
        # only test if data are present
        try:
            _ = request.get_json()
        except (BadRequest, UnsupportedMediaType) as e:
            raise api_errors.ApiErrors({"global": [e.description]}, status_code=400)


provider_blueprint = Blueprint(
    name="provider",
    import_name=__name__,  # we must add `url_prefix="/"` for spectree to work
    url_prefix="/",
)
provider_blueprint.before_request(_check_api_is_enabled_and_json_valid)


# Setting CORS
CORS(
    provider_blueprint,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)

# Registering spectree schemas
spectree_schemas.public_api_schema.register(provider_blueprint)
