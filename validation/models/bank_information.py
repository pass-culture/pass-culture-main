from schwifty import BIC, IBAN

from models import ApiErrors, BankInformation


def validate(bank_information: BankInformation, api_errors: ApiErrors) -> ApiErrors:
    try:
        IBAN(bank_information.iban)
    except (ValueError, TypeError):
        api_errors.add_error('iban', f'L’IBAN renseigné ("{bank_information.iban}") est invalide')

    try:
        BIC(bank_information.bic)
    except (ValueError, TypeError):
        api_errors.add_error('bic', f'Le BIC renseigné ("{bank_information.bic}") est invalide')

    return api_errors
