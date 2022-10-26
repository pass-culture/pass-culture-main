from flask import Blueprint

from .individual_offers import blueprint


public_blueprint = Blueprint("public_blueprint", __name__, url_prefix="/public")

public_blueprint.register_blueprint(blueprint.individual_offers_blueprint)
