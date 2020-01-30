from schwifty import BIC, IBAN

from models import ApiErrors
from models.db import Model


def get_bank_information_errors(model: Model, api_errors: ApiErrors) -> ApiErrors:
    try:
        IBAN(model.iban)
    except (ValueError, TypeError):
        api_errors.add_error('iban', f'L’IBAN renseigné ("{model.iban}") est invalide')

    try:
        BIC(model.bic)
    except (ValueError, TypeError):
        api_errors.add_error('bic', f'Le BIC renseigné ("{model.bic}") est invalide')

    return api_errors
