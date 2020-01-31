from models import ApiErrors
from models.db import Model


def validate_offerer(model: Model, api_errors: ApiErrors) -> ApiErrors:
    if model.siren is not None and (not len(model.siren) == 9):
        api_errors.add_error('siren', 'Ce code SIREN est invalide')

    return api_errors
