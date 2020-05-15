from domain.bank_informations.bank_informations import BankInformations
from domain.bank_informations.bank_informations_repository import BankInformationsRepository
from infrastructure.repository.bank_informations import bank_informations_domain_converter
from models import BankInformation as BankInformationsSQLEntity


class BankInformationsSQLRepository(BankInformationsRepository):
    def find_by_offerer(self, offerer_id: str) -> BankInformations:
        bank_informations_entity = BankInformationsSQLEntity.query \
            .filter_by(offererId=offerer_id) \
            .one_or_none()

        if bank_informations_entity is not None:
            return bank_informations_domain_converter.to_domain(bank_informations_entity)

    def find_by_venue(self, venue_id: str) -> BankInformations:
        bank_informations_entity = BankInformationsSQLEntity.query \
            .filter_by(venueId=venue_id) \
            .one_or_none()

        if bank_informations_entity is not None:
            return bank_informations_domain_converter.to_domain(bank_informations_entity)

    def get_by_application(self, application_id: str) -> BankInformations:
        bank_informations_entity = BankInformationsSQLEntity.query \
            .filter_by(applicationId=application_id) \
            .first()

        if bank_informations_entity is not None:
            return bank_informations_domain_converter.to_domain(bank_informations_entity)
