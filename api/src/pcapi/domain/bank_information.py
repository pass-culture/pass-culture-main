from datetime import datetime

from schwifty import BIC
from schwifty import IBAN

from pcapi.core.finance.models import BankInformationStatus
from pcapi.core.offerers.models import Offerer
from pcapi.domain.bank_informations.bank_informations import BankInformations
from pcapi.models.api_errors import ApiErrors


status_weight = {BankInformationStatus.ACCEPTED: 2, BankInformationStatus.DRAFT: 1, BankInformationStatus.REJECTED: 0}


class CannotRegisterBankInformation(ApiErrors):
    pass


def check_offerer_presence(offerer: Offerer, api_errors: CannotRegisterBankInformation) -> None:
    if not offerer:
        api_errors.add_error("Offerer", "Offerer not found")


def check_new_bank_information_older_than_saved_one(
    bank_information: BankInformations, modification_date: datetime, api_errors: CannotRegisterBankInformation
) -> None:
    is_new_bank_information_older_than_saved_one = (
        bank_information.date_modified is not None and modification_date < bank_information.date_modified
    )
    if is_new_bank_information_older_than_saved_one:
        api_errors.add_error("BankInformation", "Received application details are older than saved one")


def check_new_bank_information_has_a_more_advanced_status(
    bank_information: BankInformations, status: BankInformationStatus, api_errors: CannotRegisterBankInformation
) -> None:
    is_new_bank_information_status_more_important_than_saved_one = (
        bank_information.status and status_weight[status] < status_weight[bank_information.status]  # type: ignore [index]
    )
    if is_new_bank_information_status_more_important_than_saved_one:
        if status == BankInformationStatus.DRAFT:
            api_errors.add_error(
                "BankInformation", "Received dossier is in draft state. Move it to 'Accepté' to save it."
            )
        else:
            api_errors.add_error(
                "BankInformation", "Received application details state does not allow to change bank information"
            )


def check_new_bank_information_valid(
    bank_information: BankInformations, api_errors: CannotRegisterBankInformation
) -> None:
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
            api_errors.add_error("iban", f"L’IBAN doit être vide pour le statut {bank_information.status.name}")  # type: ignore [union-attr]
        if bank_information.bic is not None:
            api_errors.add_error("bic", f"Le BIC doit être vide pour le statut {bank_information.status.name}")  # type: ignore [union-attr]
