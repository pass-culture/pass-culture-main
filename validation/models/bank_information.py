from schwifty import BIC, IBAN

from models import ApiErrors, BankInformation


def validate(bank_information: BankInformation, api_errors: ApiErrors) -> ApiErrors:
    if bank_information.iban is not None:
        try:
            IBAN(bank_information.iban)
        except (ValueError, TypeError):
            api_errors.add_error(
                'iban', f'L’IBAN renseigné ("{bank_information.iban}") est invalide')

    if bank_information.bic is not None:
        try:
            BIC(bank_information.bic)
        except (ValueError, TypeError):
            api_errors.add_error(
                'bic', f'Le BIC renseigné ("{bank_information.bic}") est invalide')

    return api_errors
