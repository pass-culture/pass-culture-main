from infrastructure.repository.bank_informations import bank_informations_domain_converter
from infrastructure.repository.bank_informations.bank_informations_sql_repository import BankInformationsSQLRepository
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_bank_information, create_venue

class BankInformationsSQLRepositoryTest:
    def setup_method(self):
        self.bank_informations_sql_repository = BankInformationsSQLRepository()

    @clean_database
    def test_returns_bank_informations_when_offerer_has_bank_informations(self, app):
        # given
        offerer = create_offerer()
        bank_informations = create_bank_information(offerer=offerer)
        repository.save(bank_informations)

        expected_bank_informations = bank_informations_domain_converter.to_domain(bank_informations)

        # when
        bank_informations = self.bank_informations_sql_repository.find_by_offerer(offerer_id=offerer.id)

        # then
        assert bank_informations.application_id == expected_bank_informations.application_id
        assert bank_informations.status == expected_bank_informations.status
        assert bank_informations.iban == expected_bank_informations.iban
        assert bank_informations.bic == expected_bank_informations.bic

    @clean_database
    def test_returns_none_when_offerer_has_no_bank_informations(self, app):
        # given
        offerer = create_offerer()
        bank_informations = create_bank_information(offerer=offerer)
        repository.save(bank_informations)

        # when
        bank_informations = self.bank_informations_sql_repository.find_by_offerer(offerer_id=0)

        # then
        assert bank_informations is None

    @clean_database
    def test_returns_bank_informations_when_venue_has_bank_informations(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        bank_informations = create_bank_information(venue=venue)
        repository.save(bank_informations)

        expected_bank_informations = bank_informations_domain_converter.to_domain(bank_informations)

        # when
        bank_informations = self.bank_informations_sql_repository.find_by_venue(venue_id=venue.id)

        # then
        assert bank_informations.application_id == expected_bank_informations.application_id
        assert bank_informations.status == expected_bank_informations.status
        assert bank_informations.iban == expected_bank_informations.iban
        assert bank_informations.bic == expected_bank_informations.bic

    @clean_database
    def test_returns_none_when_venue_has_no_bank_informations(self, app):
        # given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        bank_informations = create_bank_information(venue=venue)
        repository.save(bank_informations)

        # when
        bank_informations = self.bank_informations_sql_repository.find_by_venue(venue_id=0)

        # then
        assert bank_informations is None

    @clean_database
    def test_returns_bank_informations_when_there_is_bank_informations_associated_with_this_application_id(self, app):
        # given
        offerer = create_offerer()
        bank_informations = create_bank_information(offerer=offerer, application_id=2)
        repository.save(bank_informations)

        expected_bank_informations = bank_informations_domain_converter.to_domain(bank_informations)

        # when
        bank_informations = self.bank_informations_sql_repository.get_by_application(application_id=2)

        # then
        assert bank_informations.application_id == expected_bank_informations.application_id
        assert bank_informations.status == expected_bank_informations.status
        assert bank_informations.iban == expected_bank_informations.iban
        assert bank_informations.bic == expected_bank_informations.bic

    @clean_database
    def test_returns_none_when_there_is_no_bank_informations_associated_with_this_application_id(self, app):
        # given
        offerer = create_offerer()
        bank_informations = create_bank_information(offerer=offerer, application_id=2)
        repository.save(bank_informations)

        # when
        bank_informations = self.bank_informations_sql_repository.get_by_application(application_id=1)

        # then
        assert bank_informations is None
