from models import BankInformation
from models.bank_information import BankInformationStatus

status_weight = {
    BankInformationStatus.ACCEPTED: 2,
    BankInformationStatus.DRAFT: 1,
    BankInformationStatus.REJECTED: 0
}


def new_application_can_update_bank_information(bank_information: BankInformation,
                                                new_application_id: int,
                                                new_application_status: int):
    same_demarches_simplifiees_application = new_application_id == bank_information.applicationId

    new_status_is_more_advanced_than_previous = (
        status_weight[new_application_status] >= status_weight[bank_information.status])

    return same_demarches_simplifiees_application or new_status_is_more_advanced_than_previous


class NoRefererException(Exception):
    pass


def check_offerer_presence(offerer):
    if not offerer:
        raise NoRefererException("Offerer not found")


def check_venue_presence(venue):
    if not venue:
        raise NoRefererException("Venue not found")


def check_venue_queried_by_name(venues):
    if len(venues) == 0:
        raise NoRefererException("Venue name not found")
    if len(venues) > 1:
        raise NoRefererException("Multiple venues found")
