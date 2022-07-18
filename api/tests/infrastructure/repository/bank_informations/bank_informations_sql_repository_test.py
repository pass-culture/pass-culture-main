from datetime import datetime

import pytest

import pcapi.core.finance.factories as finance_factories
from pcapi.core.finance.models import BankInformation as BankInformationsSQLEntity
from pcapi.core.finance.models import BankInformationStatus
import pcapi.core.offerers.factories as offerers_factories
from pcapi.domain.bank_informations.bank_informations import BankInformations
from pcapi.infrastructure.repository.bank_informations import bank_informations_domain_converter
from pcapi.infrastructure.repository.bank_informations.bank_informations_sql_repository import (
    BankInformationsSQLRepository,
)
from pcapi.models.api_errors import ApiErrors


class BankInformationsSQLRepositoryTest:
    def setup_method(self):
        self.bank_informations_sql_repository = BankInformationsSQLRepository()

    @pytest.mark.usefixtures("db_session")
    def test_returns_bank_informations_when_offerer_has_bank_informations(self, app):
        # given
        offerer = offerers_factories.OffererFactory()
        bank_informations = finance_factories.BankInformationFactory(offerer=offerer)

        expected_bank_informations = bank_informations_domain_converter.to_domain(bank_informations)

        # when
        bank_informations = self.bank_informations_sql_repository.find_by_offerer(offerer_id=offerer.id)

        # then
        assert bank_informations.application_id == expected_bank_informations.application_id
        assert bank_informations.status == expected_bank_informations.status
        assert bank_informations.iban == expected_bank_informations.iban
        assert bank_informations.bic == expected_bank_informations.bic
        assert bank_informations.date_modified == expected_bank_informations.date_modified

    @pytest.mark.usefixtures("db_session")
    def test_returns_none_when_offerer_has_no_bank_informations(self, app):
        # given
        offerer = offerers_factories.OffererFactory()
        bank_informations = finance_factories.BankInformationFactory(offerer=offerer)

        # when
        bank_informations = self.bank_informations_sql_repository.find_by_offerer(offerer_id=0)

        # then
        assert bank_informations is None

    @pytest.mark.usefixtures("db_session")
    def test_returns_bank_informations_when_venue_has_bank_informations(self, app):
        # given
        venue = offerers_factories.VenueFactory()
        bank_informations = finance_factories.BankInformationFactory(venue=venue)

        expected_bank_informations = bank_informations_domain_converter.to_domain(bank_informations)

        # when
        bank_informations = self.bank_informations_sql_repository.find_by_venue(venue_id=venue.id)

        # then
        assert bank_informations.application_id == expected_bank_informations.application_id
        assert bank_informations.status == expected_bank_informations.status
        assert bank_informations.iban == expected_bank_informations.iban
        assert bank_informations.bic == expected_bank_informations.bic

    @pytest.mark.usefixtures("db_session")
    def test_returns_none_when_venue_has_no_bank_informations(self, app):
        # given
        venue = offerers_factories.VenueFactory()
        bank_informations = finance_factories.BankInformationFactory(venue=venue)

        # when
        bank_informations = self.bank_informations_sql_repository.find_by_venue(venue_id=0)

        # then
        assert bank_informations is None

    @pytest.mark.usefixtures("db_session")
    def test_returns_bank_informations_when_there_is_bank_informations_associated_with_this_application_id(self, app):
        # given
        offerer = offerers_factories.OffererFactory()
        bank_informations = finance_factories.BankInformationFactory(offerer=offerer, applicationId=2)

        expected_bank_informations = bank_informations_domain_converter.to_domain(bank_informations)

        # when
        bank_informations = self.bank_informations_sql_repository.get_by_application(application_id=2)

        # then
        assert bank_informations.application_id == expected_bank_informations.application_id
        assert bank_informations.date_modified == expected_bank_informations.date_modified
        assert bank_informations.status == expected_bank_informations.status
        assert bank_informations.iban == expected_bank_informations.iban
        assert bank_informations.bic == expected_bank_informations.bic

    @pytest.mark.usefixtures("db_session")
    def test_returns_none_when_there_is_no_bank_informations_associated_with_this_application_id(self, app):
        # given
        offerer = offerers_factories.OffererFactory()
        bank_informations = finance_factories.BankInformationFactory(offerer=offerer, applicationId=2)

        # when
        bank_informations = self.bank_informations_sql_repository.get_by_application(application_id=1)

        # then
        assert bank_informations is None

    @pytest.mark.usefixtures("db_session")
    def test_should_create_bank_informations_on_save_when_bank_informations_does_not_exist(self, app):
        # given
        offerer = offerers_factories.OffererFactory()
        bank_informations_to_save = BankInformations(
            offerer_id=offerer.id,
            status=BankInformationStatus.ACCEPTED,
            application_id=8,
            iban="FR7630006000011234567890189",
            bic="QSDFGH8Z555",
            date_modified=datetime(2000, 1, 1),
        )

        # when
        bank_informations_saved = self.bank_informations_sql_repository.save(bank_informations_to_save)

        # then
        assert BankInformationsSQLEntity.query.count() == 1

        sql_bank_informations_saved = BankInformationsSQLEntity.query.one()
        assert sql_bank_informations_saved.offererId == offerer.id
        assert sql_bank_informations_saved.venueId is None
        assert sql_bank_informations_saved.iban == bank_informations_to_save.iban
        assert sql_bank_informations_saved.bic == bank_informations_to_save.bic
        assert sql_bank_informations_saved.applicationId == bank_informations_to_save.application_id
        assert sql_bank_informations_saved.status == bank_informations_to_save.status
        assert sql_bank_informations_saved.dateModified is not None

        assert bank_informations_saved.iban == bank_informations_to_save.iban
        assert bank_informations_saved.bic == bank_informations_to_save.bic

    @pytest.mark.usefixtures("db_session")
    def test_should_not_create_bank_informations_on_save_when_no_offerer_associated_in_database(self, app):
        # given
        bank_informations_to_save = BankInformations(offerer_id=9, status="ACCEPTED", application_id=8)

        # when
        with pytest.raises(ApiErrors) as error:
            self.bank_informations_sql_repository.save(bank_informations_to_save)

        # then
        assert BankInformationsSQLEntity.query.count() == 0
        assert error.value.errors["offererId"] == [
            "Aucun objet ne correspond \u00e0 cet identifiant dans notre base de donn\u00e9es"
        ]

    @pytest.mark.usefixtures("db_session")
    def test_should_not_create_bank_informations_on_save_when_bank_infos_is_already_associated_to_an_offerer_in_database(
        self, app
    ):
        # given
        offerer = offerers_factories.OffererFactory()
        finance_factories.BankInformationFactory(offerer=offerer)
        bank_informations_to_save = BankInformations(offerer_id=offerer.id, status="ACCEPTED", application_id=8)

        # when
        with pytest.raises(ApiErrors) as error:
            self.bank_informations_sql_repository.save(bank_informations_to_save)

        # then
        assert BankInformationsSQLEntity.query.count() == 1
        assert error.value.errors['"offererId"'] == [
            "Une entrée avec cet identifiant existe déjà dans notre base de données"
        ]

    @pytest.mark.usefixtures("db_session")
    def test_should_update_bank_informations_when_bank_informations_already_exist_for_offerer(self, app):
        # given
        offerer = offerers_factories.OffererFactory()
        finance_factories.BankInformationFactory(
            offerer=offerer, applicationId=9, status=BankInformationStatus.DRAFT, iban=None, bic=None
        )

        bank_informations_to_save = BankInformations(
            status=BankInformationStatus.ACCEPTED,
            application_id=9,
            iban="FR7630006000011234567890189",
            bic="QSDFGH8Z555",
            offerer_id=offerer.id,
            date_modified=datetime(2018, 2, 3),
        )

        # when
        bank_informations_saved = self.bank_informations_sql_repository.update_by_offerer_id(bank_informations_to_save)

        # then
        assert BankInformationsSQLEntity.query.count() == 1

        sql_bank_informations_saved = BankInformationsSQLEntity.query.first()
        assert sql_bank_informations_saved.offererId == offerer.id
        assert sql_bank_informations_saved.venueId is None
        assert sql_bank_informations_saved.iban == bank_informations_to_save.iban
        assert sql_bank_informations_saved.bic == bank_informations_to_save.bic
        assert sql_bank_informations_saved.applicationId == bank_informations_to_save.application_id
        assert sql_bank_informations_saved.status == bank_informations_to_save.status
        assert sql_bank_informations_saved.dateModified == bank_informations_to_save.date_modified

        assert bank_informations_saved.iban == bank_informations_to_save.iban
        assert bank_informations_saved.bic == bank_informations_to_save.bic

    @pytest.mark.usefixtures("db_session")
    def test_should_not_update_bank_informations_when_bank_informations_do_not_exist_for_offerer(self, app):
        # given
        bank_informations_to_save = BankInformations(
            status=BankInformationStatus.ACCEPTED,
            application_id=9,
            iban="FR7630006000011234567890189",
            bic="QSDFGH8Z555",
            offerer_id=1,
        )

        # when
        bank_informations_updated = self.bank_informations_sql_repository.update_by_offerer_id(
            bank_informations_to_save
        )

        # then
        assert BankInformationsSQLEntity.query.count() == 0
        assert bank_informations_updated is None

    @pytest.mark.usefixtures("db_session")
    def test_should_update_bank_informations_when_bank_informations_already_exist_for_application(self, app):
        # given
        offerer = offerers_factories.OffererFactory()
        finance_factories.BankInformationFactory(
            offerer=offerer, applicationId=9, status=BankInformationStatus.DRAFT, iban=None, bic=None
        )

        bank_informations_to_save = BankInformations(
            status=BankInformationStatus.ACCEPTED,
            application_id=9,
            iban="FR7630006000011234567890189",
            bic="QSDFGH8Z555",
            offerer_id=offerer.id,
            date_modified=datetime(2018, 2, 3),
        )

        # when
        bank_informations_saved = self.bank_informations_sql_repository.update_by_application_id(
            bank_informations_to_save
        )

        # then
        assert BankInformationsSQLEntity.query.count() == 1

        sql_bank_informations_saved = BankInformationsSQLEntity.query.first()
        assert sql_bank_informations_saved.offererId == offerer.id
        assert sql_bank_informations_saved.venueId is None
        assert sql_bank_informations_saved.iban == bank_informations_to_save.iban
        assert sql_bank_informations_saved.bic == bank_informations_to_save.bic
        assert sql_bank_informations_saved.applicationId == bank_informations_to_save.application_id
        assert sql_bank_informations_saved.status == bank_informations_to_save.status
        assert sql_bank_informations_saved.dateModified == bank_informations_to_save.date_modified

        assert bank_informations_saved.iban == bank_informations_to_save.iban
        assert bank_informations_saved.bic == bank_informations_to_save.bic

    @pytest.mark.usefixtures("db_session")
    def test_should_not_update_bank_informations_when_bank_informations_do_not_exist_for_this_application(self, app):
        # given
        bank_informations_to_save = BankInformations(
            status=BankInformationStatus.ACCEPTED,
            application_id=9,
            iban="FR7630006000011234567890189",
            bic="QSDFGH8Z555",
            offerer_id=1,
        )

        # when
        bank_informations_updated = self.bank_informations_sql_repository.update_by_application_id(
            bank_informations_to_save
        )

        # then
        assert BankInformationsSQLEntity.query.count() == 0
        assert bank_informations_updated is None

    @pytest.mark.usefixtures("db_session")
    def test_should_update_bank_informations_when_bank_informations_already_exist_for_venue(self, app):
        # given
        venue = offerers_factories.VenueFactory(businessUnit=None)
        finance_factories.BankInformationFactory(
            venue=venue,
            applicationId=9,
            status=BankInformationStatus.DRAFT,
            iban=None,
            bic=None,
        )

        bank_informations_to_save = BankInformations(
            status=BankInformationStatus.ACCEPTED,
            application_id=9,
            iban="FR7630006000011234567890189",
            bic="QSDFGH8Z555",
            venue_id=venue.id,
            date_modified=datetime(2018, 2, 3),
        )

        # when
        bank_informations_saved = self.bank_informations_sql_repository.update_by_venue_id(bank_informations_to_save)

        # then
        assert BankInformationsSQLEntity.query.count() == 1

        sql_bank_informations_saved = BankInformationsSQLEntity.query.first()
        assert sql_bank_informations_saved.offererId == None
        assert sql_bank_informations_saved.venueId == venue.id
        assert sql_bank_informations_saved.iban == bank_informations_to_save.iban
        assert sql_bank_informations_saved.bic == bank_informations_to_save.bic
        assert sql_bank_informations_saved.applicationId == bank_informations_to_save.application_id
        assert sql_bank_informations_saved.status == bank_informations_to_save.status
        assert sql_bank_informations_saved.dateModified == bank_informations_to_save.date_modified

        assert bank_informations_saved.iban == bank_informations_to_save.iban
        assert bank_informations_saved.bic == bank_informations_to_save.bic

    @pytest.mark.usefixtures("db_session")
    def test_should_not_update_bank_informations_when_bank_informations_do_not_exist_for_venue(self, app):
        # given
        bank_informations_to_save = BankInformations(
            status=BankInformationStatus.ACCEPTED,
            application_id=9,
            iban="FR7630006000011234567890189",
            bic="QSDFGH8Z555",
            venue_id=1,
        )

        # when
        bank_informations_updated = self.bank_informations_sql_repository.update_by_venue_id(bank_informations_to_save)

        # then
        assert BankInformationsSQLEntity.query.count() == 0
        assert bank_informations_updated is None
