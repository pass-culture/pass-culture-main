from schwifty import BIC, IBAN

from models import ApiErrors, BankInformation
from models.bank_information import BankInformationStatus


def validate(bank_information: BankInformation, api_errors: ApiErrors) -> ApiErrors:
    if bank_information.status == BankInformationStatus.ACCEPTED:
        if bank_information.iban is None:
            api_errors.add_error(
                'iban', 'Cette information est obligatoire')
        else:
            try:
                IBAN(bank_information.iban)
            except (ValueError, TypeError):
                api_errors.add_error(
                    'iban', f'L’IBAN renseigné ("{bank_information.iban}") est invalide')

        if bank_information.bic is None:
            api_errors.add_error(
                'bic', 'Cette information est obligatoire')
        else:
            try:
                BIC(bank_information.bic)
            except (ValueError, TypeError):
                api_errors.add_error(
                    'bic', f'Le BIC renseigné ("{bank_information.bic}") est invalide')
    else:
        if bank_information.iban is not None:
            api_errors.add_error(
                'iban', f'L’IBAN doit être vide pour le statut {bank_information.status.name}')
        if bank_information.bic is not None:
            api_errors.add_error(
                'bic', f'Le BIC doit être vide pour le statut {bank_information.status.name}')

    return api_errors
