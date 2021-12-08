from datetime import datetime

from pcapi.core.offerers.models import Offerer
from pcapi.domain.bank_informations.bank_informations import BankInformations
from pcapi.models.bank_information import BankInformationStatus


status_weight = {BankInformationStatus.ACCEPTED: 2, BankInformationStatus.DRAFT: 1, BankInformationStatus.REJECTED: 0}


class CannotRegisterBankInformation(Exception):
    pass


def check_offerer_presence(offerer: Offerer) -> None:
    if not offerer:
        raise CannotRegisterBankInformation("Offerer not found")


def check_new_bank_information_older_than_saved_one(
    bank_information: BankInformations, modification_date: datetime
) -> None:
    is_new_bank_information_older_than_saved_one = (
        bank_information.date_modified is not None and modification_date < bank_information.date_modified
    )
    if is_new_bank_information_older_than_saved_one:
        raise CannotRegisterBankInformation("Received application details are older than saved one")


def check_new_bank_information_has_a_more_advanced_status(
    bank_information: BankInformations, status: BankInformationStatus
) -> None:
    is_new_bank_information_status_more_important_than_saved_one = (
        bank_information.status and status_weight[status] < status_weight[bank_information.status]
    )
    if is_new_bank_information_status_more_important_than_saved_one:
        raise CannotRegisterBankInformation(
            "Received application details state does not allow to change bank information"
        )
