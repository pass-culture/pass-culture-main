from flask import Blueprint
from flask_cors import CORS

from pcapi import settings


testing_blueprint = Blueprint("testing", __name__)
CORS(
    testing_blueprint,
    origins=settings.CORS_ALLOWED_ORIGINS,
    supports_credentials=True,
)
