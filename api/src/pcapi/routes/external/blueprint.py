from flask import Blueprint
from flask_cors import CORS


external_blueprint = Blueprint(name="external", import_name=__name__, url_prefix="/webhooks")
CORS(external_blueprint, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
