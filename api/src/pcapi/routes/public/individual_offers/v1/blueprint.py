from flask import Blueprint
from flask import request
from flask_cors import CORS
from spectree import SecurityScheme
from werkzeug.exceptions import BadRequest

from pcapi.models import api_errors
from pcapi.models import feature
from pcapi.serialization.spec_tree import ExtendedSpecTree
from pcapi.serialization.utils import public_api_before_handler
from pcapi.validation.routes import users_authentifications


def check_api_is_enabled_and_json_valid() -> None:
    # We test the json validity because pydantic will not raise an error if the json is not valid.
    # Pydantic will then try to apply the validation schema and throws unintelligible errors.
    try:
        _ = request.get_json()
    except BadRequest as e:
        raise api_errors.ApiErrors({"global": [e.description]}, status_code=400)
    if not feature.FeatureToggle.WIP_ENABLE_OFFER_CREATION_API_V1.is_active():
        raise api_errors.ApiErrors({"global": ["This API is not enabled"]}, status_code=400)


class IndividualApiSpectree(ExtendedSpecTree):
    def __init__(self, title: str, PATH: str, version: str):
        super().__init__(
            "flask",
            title=title,
            MODE="strict",
            before=public_api_before_handler,
            security_schemes=[
                SecurityScheme(
                    name=users_authentifications.API_KEY_AUTH_NAME,
                    data={"type": "http", "scheme": "bearer", "description": "Api key issued on passculture.pro"},  # type: ignore [arg-type]
                )
            ],
            PATH=PATH,
            version=version,
        )


v1_blueprint = Blueprint("v1_blueprint", __name__, url_prefix="/v1")
v1_blueprint.before_request(check_api_is_enabled_and_json_valid)
CORS(
    v1_blueprint,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)

v1_bookings_blueprint = Blueprint("v1_bookings_blueprint", __name__, url_prefix="/v1")
v1_bookings_blueprint.before_request(check_api_is_enabled_and_json_valid)
CORS(
    v1_bookings_blueprint,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)

# FIXME (mageoffray, 2023-05-19)
# For a short period of time we want to move event documentation
# out of the main path.
# In the long run we will want to have all our apis documentation at the same
# place.
v1_event_schema = IndividualApiSpectree(
    title="Event Offers API",
    PATH="/event",
    version="1.0",
)
v1_event_schema.register(v1_blueprint)

v1_product_schema = IndividualApiSpectree(
    title="Product Offers API",
    PATH="/",
    version="1.0",
)
v1_product_schema.register(v1_blueprint)

v1_bookings_schema = IndividualApiSpectree(
    title="Bookings API",
    PATH="/",
    version="1.0",
)
v1_bookings_schema.register(v1_bookings_blueprint)
