from models import BankInformation
from models.bank_information import BankInformationStatus
from repository import bank_information_queries, offerer_queries, repository
from domain.bank_information import check_offerer_presence, \
     check_new_bank_information_older_than_saved_one, check_new_bank_information_has_a_more_advanced_status
from domain.demarches_simplifiees import get_offerer_bank_information_application_details_by_application_id, \
     ApplicationDetail


class SaveOffererBankInformations:
    def execute(self, application_id: str):
        application_details = get_offerer_bank_information_application_details_by_application_id(
            application_id)

        offerer = offerer_queries.find_by_siren(application_details.siren)

        check_offerer_presence(offerer)

        save_bank_information(application_details, offerer.id, None)


def save_bank_information(application_details: ApplicationDetail, offerer_id: str, venue_id: str):
    application_bank_information = _get_application_bank_information(
        application_details)

    if not application_bank_information:
        previous_bank_information = bank_information_queries.get_by_offerer_and_venue(
            offerer_id, venue_id)

        if previous_bank_information:
            check_new_bank_information_older_than_saved_one(
                previous_bank_information, application_details)
            check_new_bank_information_has_a_more_advanced_status(
                previous_bank_information, application_details)

    bank_information = application_bank_information or previous_bank_information or BankInformation()
    bank_information = _fill_bank_information(
        application_details, bank_information, offerer_id, venue_id)

    repository.save(bank_information)


def _get_application_bank_information(application_details: ApplicationDetail) -> BankInformation:
    application_bank_information = bank_information_queries.get_by_application_id(
        application_details.application_id)
    return application_bank_information


def _fill_bank_information(application_details: ApplicationDetail, bank_information: BankInformation, offerer_id: str, venue_id: str) -> BankInformation:
    bank_information.applicationId = application_details.application_id
    bank_information.offererId = offerer_id
    bank_information.venueId = venue_id
    bank_information.status = application_details.status
    if application_details.status == BankInformationStatus.ACCEPTED:
        bank_information.iban = application_details.iban
        bank_information.bic = application_details.bic
    else:
        bank_information.iban = None
        bank_information.bic = None
    return bank_information
