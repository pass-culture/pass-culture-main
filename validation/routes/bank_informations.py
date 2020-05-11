import os

from models.api_errors import ForbiddenError, ApiErrors

DEMARCHES_SIMPLIFIEES_WEBHOOK_TOKEN = os.environ.get('DEMARCHES_SIMPLIFIEES_WEBHOOK_TOKEN')


def check_refferer_type(refferer_type):
    if refferer_type not in ["offerer", "venue"]:
        api_errors = ApiErrors()
        api_errors.add_error('unknown provider', 'unknown refferer type. Choose beetween offerer or venue')
        raise api_errors


def check_demarches_simplifiees_webhook_token(token):
    if token != DEMARCHES_SIMPLIFIEES_WEBHOOK_TOKEN:
        errors = ForbiddenError()
        errors.add_error('token', "Invalid token")
        raise errors
