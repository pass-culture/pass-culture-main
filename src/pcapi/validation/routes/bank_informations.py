from typing import Dict

from flask import request

from pcapi import settings
from pcapi.models.api_errors import ApiErrors
from pcapi.models.api_errors import ForbiddenError


def check_demarches_simplifiees_webhook_payload(payload: Dict):
    try:
        request.form["dossier_id"]
    except:
        errors = ApiErrors()
        errors.add_error("application_id", "Invalid application id")
        raise errors


def check_demarches_simplifiees_webhook_token(token):
    if token != settings.DMS_WEBHOOK_TOKEN:
        errors = ForbiddenError()
        errors.add_error("token", "Invalid token")
        raise errors
