import re

from models import ApiErrors
from models.db import Model


def validate_has_address_mixin(model: Model, api_errors: ApiErrors) -> ApiErrors:
    if model.postalCode is not None and not re.match(r'^\d[AB0-9]\d{3,4}$', model.postalCode):
        api_errors.add_error('postalCode', 'Ce code postal est invalide')

    return api_errors
