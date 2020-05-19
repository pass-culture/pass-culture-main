from models import BankInformation, Venue, Offerer
from models.bank_information import BankInformationStatus
from repository import bank_information_queries, offerer_queries, repository, venue_queries
from domain.bank_information import check_offerer_presence, check_venue_presence, check_venue_queried_by_name, \
    check_new_bank_information_older_than_saved_one, check_new_bank_information_has_a_more_advanced_status
from domain.demarches_simplifiees import get_venue_bank_information_application_details_by_application_id, ApplicationDetail
from domain.offerer.offerer_repository import OffererRepository
from domain.bank_informations.bank_informations_repository import BankInformationsRepository
from domain.venue.venue_repository import VenueRepository
from domain.bank_informations.bank_informations import BankInformations


class SaveVenueBankInformations:
    def __init__(self,
                 offerer_repository: OffererRepository,
                 venue_repository: VenueRepository,
                 bank_informations_repository: BankInformationsRepository
                 ):
        self.offerer_repository = offerer_repository
        self.venue_repository = venue_repository
        self.bank_informations_repository = bank_informations_repository

    def execute(self, application_id: str):
        application_details = get_venue_bank_information_application_details_by_application_id(
            application_id)

        siren = application_details.siren
        offerer = self.offerer_repository.find_by_siren(siren)
        check_offerer_presence(offerer)
        venue = self.get_referent_venue(application_details, offerer)

        bank_information_by_application_id = self.bank_informations_repository.get_by_application(
            application_details.application_id)

        if bank_information_by_application_id:
            check_new_bank_information_older_than_saved_one(bank_information_by_application_id, application_details)
            new_bank_informations = self.create_new_bank_informations(application_details, venue.id)
            return self.bank_informations_repository.update_by_application_id(new_bank_informations)

        else:
            bank_information_by_venue_id = self.bank_informations_repository.find_by_venue(venue.id)

            if bank_information_by_venue_id:
                check_new_bank_information_older_than_saved_one(bank_information_by_venue_id, application_details)
                check_new_bank_information_has_a_more_advanced_status(bank_information_by_venue_id, application_details)

                new_bank_informations = self.create_new_bank_informations(application_details, venue.id)
                return self.bank_informations_repository.update_by_venue_id(new_bank_informations)

            else:
                new_bank_informations = self.create_new_bank_informations(application_details, venue.id)
                return self.bank_informations_repository.save(new_bank_informations)


    def get_referent_venue(self, application_details: ApplicationDetail, offerer: Offerer) -> Venue:
        siret = application_details.siret

        if siret:
            venue = self.venue_repository.find_by_siret(siret)
            check_venue_presence(venue)
        else:
            name = application_details.venue_name
            venues = self.venue_repository.find_by_name(name, offerer.id)
            check_venue_queried_by_name(venues)
            venue = venues[0]
        return venue


    def create_new_bank_informations(self, application_details: ApplicationDetail, venue_id: str) -> BankInformation:
        new_bank_informations = BankInformations()
        new_bank_informations.application_id = application_details.application_id
        new_bank_informations.venue_id = venue_id
        new_bank_informations.status = application_details.status
        if application_details.status == BankInformationStatus.ACCEPTED:
            new_bank_informations.iban = application_details.iban
            new_bank_informations.bic = application_details.bic
        else:
            new_bank_informations.iban = None
            new_bank_informations.bic = None
        return new_bank_informations
