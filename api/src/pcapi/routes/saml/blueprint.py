from flask import Blueprint
from flask_cors.extension import CORS

from pcapi import settings
from pcapi.routes.native import utils
from pcapi.routes.utils import tag_with_api_user_typology


saml_blueprint = Blueprint("saml_blueprint", __name__)
saml_blueprint.before_request(utils.check_client_version)
saml_blueprint.before_request(lambda: tag_with_api_user_typology("jeunes"))
CORS(saml_blueprint, origins=settings.CORS_ALLOWED_ORIGINS_NATIVE, supports_credentials=True)
