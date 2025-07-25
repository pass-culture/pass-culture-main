from flask import Blueprint
from flask_cors.extension import CORS

from pcapi import settings


e2e_app_blueprint = Blueprint("e2e", __name__)
CORS(
    e2e_app_blueprint,
    origins=settings.CORS_ALLOWED_ORIGINS_NATIVE,
    supports_credentials=True,
)
