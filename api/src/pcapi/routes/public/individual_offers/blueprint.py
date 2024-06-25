from flask import Blueprint
from flask import request
from werkzeug.exceptions import BadRequest

from pcapi.models import api_errors


def _check_api_is_enabled_and_json_valid() -> None:
    # We test the json validity because pydantic will not raise an error if the json is not valid.
    # Pydantic will then try to apply the validation schema and throws unintelligible errors.
    try:
        _ = request.get_json()
    except BadRequest as e:
        raise api_errors.ApiErrors({"global": [e.description]}, status_code=400)


individual_offers_blueprint = Blueprint("individual_offers", __name__)
individual_offers_blueprint.before_request(_check_api_is_enabled_and_json_valid)
