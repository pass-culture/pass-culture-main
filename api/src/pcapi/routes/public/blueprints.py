from flask import Blueprint
from flask import redirect
from flask import request
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
from werkzeug.wrappers.response import Response

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


public_api_blueprint = Blueprint(
    "public_api", __name__, url_prefix="/"  # we must add `url_prefix="/"` for spectree to work
)

# [ACTIVE] Public API following pattern /public/<resource>/v1/....
public_v1_blueprint = Blueprint("v1_public_api", __name__, url_prefix="/public")
public_v1_blueprint.before_request(_check_api_is_enabled_and_json_valid)

# [ACTIVE] Public API following pattern /v2/collective/....
v2_prefixed_public_api = Blueprint("v2_prefixed_public_api", __name__, url_prefix="/v2")


# [OLD] Old tokens and stocks apis
_deprecated_v2_prefixed_public_api = Blueprint("deprecated_public_api", __name__, url_prefix="/v2")
_deprecated_v2_prefixed_public_api.register_blueprint(booking_token_blueprint.deprecated_booking_token_blueprint)
_deprecated_v2_prefixed_public_api.register_blueprint(booking_stocks_blueprint.deprecated_books_stocks_blueprint)


# DOCUMENTATION REDIRECTS
# TODO: Remove once all the providers have been informed that the documentation has changed location (by the end of year 2024).
documentation_redirect_blueprint = Blueprint("documentation_redirect", __name__)


@documentation_redirect_blueprint.route("/v2/swagger", methods=["GET"])
@documentation_redirect_blueprint.route("/public/bookings/v1/swagger", methods=["GET"])
@documentation_redirect_blueprint.route("/public/offers/v1/event/swagger", methods=["GET"])
@documentation_redirect_blueprint.route("/public/offers/v1/swagger", methods=["GET"])
def redirect_to_new_swagger() -> "Response":
    return redirect("/swagger", code=301)


@documentation_redirect_blueprint.route("/v2/redoc", methods=["GET"])
@documentation_redirect_blueprint.route("/public/bookings/v1/redoc", methods=["GET"])
@documentation_redirect_blueprint.route("/public/offers/v1/event/redoc", methods=["GET"])
@documentation_redirect_blueprint.route("/public/offers/v1/redoc", methods=["GET"])
def redirect_bookings_swagger_to_new_swagger() -> "Response":
    return redirect("/redoc", code=301)


public_api_blueprint.register_blueprint(documentation_redirect_blueprint)
# End TODO


# Registering blueprints (current & deprecated public APIs)
public_api_blueprint.register_blueprint(public_v1_blueprint)
public_api_blueprint.register_blueprint(v2_prefixed_public_api)
public_api_blueprint.register_blueprint(_deprecated_v2_prefixed_public_api)
CORS(
    public_api_blueprint,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)


# Registering spectree schemas
spectree_schemas.public_api_schema.register(public_api_blueprint)
spectree_schemas.deprecated_public_api_schema.register(_deprecated_v2_prefixed_public_api)
