from flask import Blueprint

from .v1 import blueprint as v1_blueprint


individual_offers_blueprint = Blueprint("individual_offers", __name__, url_prefix="/offers")
individual_offers_blueprint.register_blueprint(v1_blueprint.v1_offers_blueprint)

individual_bookings_blueprint = Blueprint("individual_bookings", __name__, url_prefix="/bookings")
individual_bookings_blueprint.register_blueprint(v1_blueprint.v1_bookings_blueprint)
