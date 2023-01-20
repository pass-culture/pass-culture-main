from flask import Blueprint
import flask_cors


deprecated_booking_token_api = Blueprint("pro_public_api_v1", __name__)
flask_cors.CORS(
    deprecated_booking_token_api,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True,
)
