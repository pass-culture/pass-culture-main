from models import BankInformation, Venue, Offerer
from models.bank_information import BankInformationStatus
from repository import bank_information_queries, offerer_queries, repository, venue_queries
from domain.bank_information import check_offerer_presence, check_venue_presence, check_venue_queried_by_name, \
     check_new_bank_information_older_than_saved_one, check_new_bank_information_has_a_more_advanced_status
from domain.demarches_simplifiees import get_venue_bank_information_application_details_by_application_id, ApplicationDetail

class SaveVenueBankInformations:
    def execute(self, application_id: str):
        application_details = get_venue_bank_information_application_details_by_application_id(
            application_id)

        siren = application_details.siren
        offerer = offerer_queries.find_by_siren(siren)
        check_offerer_presence(offerer)
        venue = _get_referent_venue(application_details, offerer)

        save_bank_information(application_details, venue.id)


def save_bank_information(application_details: ApplicationDetail, venue_id: str):
    application_bank_information = _get_application_bank_information(
        application_details)

    if not application_bank_information:
        previous_bank_information = bank_information_queries.get_by_offerer_and_venue(
            None, venue_id)

        if previous_bank_information:
            check_new_bank_information_older_than_saved_one(
                previous_bank_information, application_details)
            check_new_bank_information_has_a_more_advanced_status(
                previous_bank_information, application_details)

    bank_information = application_bank_information or previous_bank_information or BankInformation()
    bank_information = _fill_bank_information(
        application_details, bank_information, venue_id)

    repository.save(bank_information)


def _get_application_bank_information(application_details: ApplicationDetail) -> BankInformation:
    application_bank_information = bank_information_queries.get_by_application_id(
        application_details.application_id)
    return application_bank_information


def _get_referent_venue(application_details: ApplicationDetail, offerer: Offerer) -> Venue:
    siret = application_details.siret

    if siret:
        venue = venue_queries.find_by_managing_offerer_id_and_siret(
            offerer.id, siret)
        check_venue_presence(venue)
    else:
        name = application_details.venue_name
        venues = venue_queries.find_venue_without_siret_by_managing_offerer_id_and_name(
            offerer.id, name)
        check_venue_queried_by_name(venues)
        venue = venues[0]
    return venue


def _fill_bank_information(application_details: ApplicationDetail, bank_information: BankInformation, venue_id: str) -> BankInformation:
    bank_information.applicationId = application_details.application_id
    bank_information.offererId = None
    bank_information.venueId = venue_id
    bank_information.status = application_details.status
    if application_details.status == BankInformationStatus.ACCEPTED:
        bank_information.iban = application_details.iban
        bank_information.bic = application_details.bic
    else:
        bank_information.iban = None
        bank_information.bic = None
    return bank_information
