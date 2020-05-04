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
    if(same_demarches_simplifiees_application):
        return True

    new_status_is_more_advanced_than_previous = (
        status_weight[new_application_status] >= status_weight[bank_information.status])
    if(new_status_is_more_advanced_than_previous):
        return True

    return False


class VenueMatchingError(Exception):
    pass


def check_offerer_presence(offerer):
    if not offerer:
        raise VenueMatchingError("Offerer not found")


def check_venue_presence(venue):
    if not venue:
        raise VenueMatchingError("Venue not found")


def check_venue_queried_by_name(venues):
    if len(venues) == 0:
        raise VenueMatchingError("Venue name for found")
    if len(venues) > 1:
        raise VenueMatchingError("Multiple venues found")
