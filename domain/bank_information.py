from typing import List

from models import BankInformation, Venue, Offerer
from domain.bank_informations.bank_informations import BankInformations
from models.bank_information import BankInformationStatus


status_weight = {
    BankInformationStatus.ACCEPTED: 2,
    BankInformationStatus.DRAFT: 1,
    BankInformationStatus.REJECTED: 0
}

class CannotRegisterBankInformation(Exception):
    pass


def check_offerer_presence(offerer: Offerer):
    if not offerer:
        raise CannotRegisterBankInformation("Offerer not found")


def check_venue_presence(venue: Venue):
    if not venue:
        raise CannotRegisterBankInformation("Venue not found")


def check_venue_queried_by_name(venues: List[Venue]):
    if len(venues) == 0:
        raise CannotRegisterBankInformation("Venue name not found")
    if len(venues) > 1:
        raise CannotRegisterBankInformation("Multiple venues found")


def check_new_bank_information_older_than_saved_one(bank_information: BankInformations, application_details):
    is_new_bank_information_older_than_saved_one = bank_information.date_modified_at_last_provider is not None and application_details.modification_date < bank_information.date_modified_at_last_provider
    if is_new_bank_information_older_than_saved_one:
        raise CannotRegisterBankInformation(
            'Received application details are older than saved one')


def check_new_bank_information_has_a_more_advanced_status(bank_information: BankInformations, application_details):
    is_new_bank_information_status_more_important_than_saved_one = bank_information.status and status_weight[
        application_details.status] < status_weight[bank_information.status]
    if is_new_bank_information_status_more_important_than_saved_one:
        raise CannotRegisterBankInformation(
            'Received application details state does not allow to change bank information')
