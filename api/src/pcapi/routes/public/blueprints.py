from flask import Blueprint
from flask_cors import CORS

# Spectree schemas
from . import spectree_schemas

# DEPRECATED APIs
from .booking_token import blueprint as booking_token_blueprint
from .books_stocks import blueprint as booking_stocks_blueprint

# ACTIVE APIs
from .collective import blueprint as collective_blueprint
from .individual_offers import blueprint as indivual_offers_blueprints


public_api_blueprint = Blueprint(
    "public_api", __name__, url_prefix="/"  # we must add `url_prefix="/"` for spectree to work
)

# [ACTIVE] Public API following pattern /public/<resource>/v1/....
_public_v1_blueprint = Blueprint("v1_public_api", __name__, url_prefix="/public")
_public_v1_blueprint.register_blueprint(indivual_offers_blueprints.individual_offers_blueprint)
_public_v1_blueprint.register_blueprint(indivual_offers_blueprints.individual_bookings_blueprint)


# [ACTIVE] Public API following pattern /v2/collective/....
_v2_prefixed_public_api = Blueprint("v2_prefixed_public_api", __name__, url_prefix="/v2")
_v2_prefixed_public_api.register_blueprint(collective_blueprint.collective_offers_blueprint)


# [OLD] Old tokens and stocks apis
_deprecated_v2_prefixed_public_api = Blueprint("deprecated_public_api", __name__, url_prefix="/v2")
_deprecated_v2_prefixed_public_api.register_blueprint(booking_token_blueprint.deprecated_booking_token_blueprint)
_deprecated_v2_prefixed_public_api.register_blueprint(booking_stocks_blueprint.deprecated_books_stocks_blueprint)


# Registering blueprints (current & deprecated public APIs)
public_api_blueprint.register_blueprint(_public_v1_blueprint)
public_api_blueprint.register_blueprint(_v2_prefixed_public_api)
public_api_blueprint.register_blueprint(_deprecated_v2_prefixed_public_api)
CORS(
    public_api_blueprint,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)


# Registering spectree schemas
spectree_schemas.public_api_schema.register(public_api_blueprint)
spectree_schemas.deprecated_public_api_schema.register(_deprecated_v2_prefixed_public_api)
