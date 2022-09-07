from schwifty import BIC
from schwifty import IBAN

from pcapi.core.finance.models import BankInformation
from pcapi.core.finance.models import BankInformationStatus
from pcapi.models.api_errors import ApiErrors


# TODO(mgeoffray, 2022-03-24): This should be deleted when save_offerer_bank_information is deleted
def validate(bank_information: BankInformation, api_errors: ApiErrors) -> ApiErrors:
    if bank_information.status == BankInformationStatus.ACCEPTED:
        if bank_information.iban is None:
            api_errors.add_error("iban", "Cette information est obligatoire")
        else:
            try:
                IBAN(bank_information.iban)
            except (ValueError, TypeError):
                api_errors.add_error("iban", f'L’IBAN renseigné ("{bank_information.iban}") est invalide')

        if bank_information.bic is None:
            api_errors.add_error("bic", "Cette information est obligatoire")
        else:
            try:
                BIC(bank_information.bic)
            except (ValueError, TypeError):
                api_errors.add_error("bic", f'Le BIC renseigné ("{bank_information.bic}") est invalide')
    else:
        if bank_information.iban is not None:
            api_errors.add_error("iban", f"L’IBAN doit être vide pour le statut {bank_information.status.name}")
        if bank_information.bic is not None:
            api_errors.add_error("bic", f"Le BIC doit être vide pour le statut {bank_information.status.name}")

    return api_errors
