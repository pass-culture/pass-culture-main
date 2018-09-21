from schwifty import BIC, IBAN

from models import ApiErrors
from validation.bic import KNOWN_BICS


def validate_bank_information(iban: str, bic: str):
    if iban and bic:
        api_errors = ApiErrors()

        try:
            IBAN(iban)
        except ValueError:
            api_errors.addError('iban', "L'IBAN saisi est invalide")

        try:
            BIC(bic)
        except ValueError:
            api_errors.addError('bic', "Le BIC saisi est invalide")
        else:
            if bic not in KNOWN_BICS:
                api_errors.addError('bic', "Le BIC saisi est inconnu")

        raise api_errors
