from pcapi.core.finance.models import BankInformation as BankInformationsSQLEntity
from pcapi.domain.bank_informations.bank_informations import BankInformations
from pcapi.domain.bank_informations.bank_informations_repository import BankInformationsRepository
from pcapi.infrastructure.repository.bank_informations import bank_informations_domain_converter
from pcapi.repository import repository


class BankInformationsSQLRepository(BankInformationsRepository):
    def find_by_offerer(self, offerer_id: int) -> BankInformations | None:
        bank_informations_sql_entity = BankInformationsSQLEntity.query.filter_by(offererId=offerer_id).one_or_none()
        if not bank_informations_sql_entity:
            return None
        return bank_informations_domain_converter.to_domain(bank_informations_sql_entity)

    def find_by_venue(self, venue_id: int) -> BankInformations | None:
        bank_informations_sql_entity = BankInformationsSQLEntity.query.filter_by(venueId=venue_id).one_or_none()
        if not bank_informations_sql_entity:
            return None
        return bank_informations_domain_converter.to_domain(bank_informations_sql_entity)

    def get_by_application(self, application_id: int) -> BankInformations | None:
        bank_informations_sql_entity = BankInformationsSQLEntity.query.filter_by(
            applicationId=application_id
        ).one_or_none()
        if not bank_informations_sql_entity:
            return None
        return bank_informations_domain_converter.to_domain(bank_informations_sql_entity)

    def save(self, bank_informations: BankInformations) -> BankInformations:
        bank_informations_sql_entity = bank_informations_domain_converter.to_model(bank_informations)
        repository.save(bank_informations_sql_entity)
        bank_informations.id = bank_informations_sql_entity.id  # type: ignore [assignment]
        return bank_informations

    def update_by_application_id(self, bank_informations: BankInformations) -> BankInformations | None:
        bank_informations_sql_entity = BankInformationsSQLEntity.query.filter_by(
            applicationId=bank_informations.application_id
        ).one_or_none()

        if not bank_informations_sql_entity:
            return None

        bank_informations_sql_entity.applicationId = bank_informations.application_id
        bank_informations_sql_entity.bic = bank_informations.bic
        bank_informations_sql_entity.iban = bank_informations.iban
        bank_informations_sql_entity.status = bank_informations.status
        bank_informations_sql_entity.offererId = bank_informations.offerer_id
        bank_informations_sql_entity.venueId = bank_informations.venue_id
        bank_informations_sql_entity.dateModified = bank_informations.date_modified

        repository.save(bank_informations_sql_entity)
        bank_informations.id = bank_informations_sql_entity.id
        return bank_informations

    def update_by_offerer_id(self, bank_informations: BankInformations) -> BankInformations | None:
        bank_informations_sql_entity = BankInformationsSQLEntity.query.filter_by(
            offererId=bank_informations.offerer_id
        ).one_or_none()

        if not bank_informations_sql_entity:
            return None

        bank_informations_sql_entity.applicationId = bank_informations.application_id
        bank_informations_sql_entity.bic = bank_informations.bic
        bank_informations_sql_entity.iban = bank_informations.iban
        bank_informations_sql_entity.status = bank_informations.status
        bank_informations_sql_entity.offererId = bank_informations.offerer_id
        bank_informations_sql_entity.dateModified = bank_informations.date_modified

        repository.save(bank_informations_sql_entity)
        bank_informations.id = bank_informations_sql_entity.id
        return bank_informations

    def update_by_venue_id(self, bank_informations: BankInformations) -> BankInformations | None:
        bank_informations_sql_entity = BankInformationsSQLEntity.query.filter_by(
            venueId=bank_informations.venue_id
        ).one_or_none()

        if not bank_informations_sql_entity:
            return None

        bank_informations_sql_entity.applicationId = bank_informations.application_id
        bank_informations_sql_entity.bic = bank_informations.bic
        bank_informations_sql_entity.iban = bank_informations.iban
        bank_informations_sql_entity.status = bank_informations.status
        bank_informations_sql_entity.venueId = bank_informations.venue_id
        bank_informations_sql_entity.dateModified = bank_informations.date_modified

        repository.save(bank_informations_sql_entity)
        bank_informations.id = bank_informations_sql_entity.id
        return bank_informations
