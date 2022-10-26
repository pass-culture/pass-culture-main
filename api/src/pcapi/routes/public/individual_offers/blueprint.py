from flask import Blueprint

from .v1 import blueprint as v1_blueprint


individual_offers_blueprint = Blueprint("individual_offers_blueprint", __name__, url_prefix="/offers")

individual_offers_blueprint.register_blueprint(v1_blueprint.v1_blueprint)
