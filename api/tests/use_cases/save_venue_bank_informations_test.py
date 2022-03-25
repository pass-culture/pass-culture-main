from datetime import datetime
from unittest.mock import patch

import pytest

import pcapi.core.finance.models as finance_models
from pcapi.core.offerers.factories import OffererFactory
from pcapi.core.offers import factories as offers_factories
from pcapi.domain.bank_information import CannotRegisterBankInformation
from pcapi.domain.demarches_simplifiees import ApplicationDetail
from pcapi.infrastructure.repository.bank_informations.bank_informations_sql_repository import (
    BankInformationsSQLRepository,
)
from pcapi.infrastructure.repository.venue.venue_with_basic_information.venue_with_basic_information_sql_repository import (
    VenueWithBasicInformationSQLRepository,
)
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.models.api_errors import ApiErrors
from pcapi.models.bank_information import BankInformation
from pcapi.models.bank_information import BankInformationStatus
from pcapi.repository import repository
from pcapi.use_cases.save_venue_bank_informations import SaveVenueBankInformations

from tests.connector_creators.demarches_simplifiees_creators import (
    venue_demarche_simplifiee_application_detail_response_with_siret,
)
from tests.connector_creators.demarches_simplifiees_creators import (
    venue_demarche_simplifiee_application_detail_response_without_siret,
)


class SaveVenueBankInformationsTest:
    class GetReferentVenueTest:
        def setup_method(self):
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        @patch("pcapi.connectors.api_entreprises.check_siret_is_still_active", return_value=False)
        @pytest.mark.usefixtures("db_session")
        def test_raises_an_error_if_no_venue_found_by_siret(self, siret_is_active):
            application_details = ApplicationDetail(
                siren="999999999",
                status=BankInformationStatus.ACCEPTED,
                application_id=1,
                iban="XXX",
                bic="YYY",
                modification_date=datetime.utcnow(),
                siret="99999999900000",
            )
            errors = ApiErrors()

            self.save_venue_bank_informations.get_referent_venue(application_details, None, errors)
            assert errors.errors["Venue"] == ["Venue not found", "SIRET is no longer active"]

        @pytest.mark.usefixtures("db_session")
        def test_raises_an_error_if_no_venue_found_by_name(self):
            offerer = OffererFactory()
            application_details = ApplicationDetail(
                siren="999999999",
                status=BankInformationStatus.ACCEPTED,
                application_id=1,
                iban="XXX",
                bic="YYY",
                modification_date=datetime.utcnow(),
                venue_name="venuedemo",
            )
            errors = ApiErrors()

            self.save_venue_bank_informations.get_referent_venue(application_details, offerer, errors)
            assert errors.errors["Venue"] == ["Venue name not found"]

        @pytest.mark.usefixtures("db_session")
        def test_raises_an_error_if_more_than_one_venue_found(self):
            offerer = OffererFactory()
            offers_factories.VenueFactory.build_batch(
                2, managingOfferer=offerer, name="venuedemo", siret=None, comment="No siret"
            )
            application_details = ApplicationDetail(
                siren="999999999",
                status=BankInformationStatus.ACCEPTED,
                application_id=1,
                iban="XXX",
                bic="YYY",
                modification_date=datetime.utcnow(),
                venue_name="venuedemo",
            )
            errors = ApiErrors()

            self.save_venue_bank_informations.get_referent_venue(application_details, offerer, errors)
            assert errors.errors["Venue"] == ["Multiple venues found"]

    class SaveBankInformationTest:
        @patch("pcapi.connectors.api_entreprises.check_siret_is_still_active")
        @patch("pcapi.connectors.dms.api.get_application_details")
        class VenueWithSiretTest:
            def setup_method(self):
                self.save_venue_bank_informations = SaveVenueBankInformations(
                    venue_repository=VenueWithBasicInformationSQLRepository(),
                    bank_informations_repository=BankInformationsSQLRepository(),
                )

            @pytest.mark.usefixtures("db_session")
            def test_when_dms_state_is_refused_should_create_the_correct_bank_information(
                self, mock_application_details, mock_check_siret_is_still_active, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret="79387503012345")
                repository.save(venue)
                mock_check_siret_is_still_active.return_value = True
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="refused",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.REJECTED

            @pytest.mark.usefixtures("db_session")
            def test_when_dms_state_is_without_continuation_should_create_the_correct_bank_information(
                self, mock_application_details, mock_check_siret_is_still_active, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret="79387503012345")
                repository.save(venue)
                mock_check_siret_is_still_active.return_value = True
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="without_continuation",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.REJECTED

            @pytest.mark.usefixtures("db_session")
            def test_when_dms_state_is_closed_should_create_the_correct_bank_information(
                self, mock_application_details, mock_check_siret_is_still_active, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret="79387503012345")
                repository.save(venue)
                mock_check_siret_is_still_active.return_value = True
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="closed",
                        updated_at="2020-01-01T10:10:10.10Z",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic == "SOGEFRPP"
                assert bank_information.iban == "FR7630007000111234567890144"
                assert bank_information.status == BankInformationStatus.ACCEPTED
                assert bank_information.dateModified == datetime(2020, 1, 1, 10, 10, 10, 100000)

            @pytest.mark.usefixtures("db_session")
            def test_when_dms_state_is_received_should_create_the_correct_bank_information(
                self, mock_application_details, mock_check_siret_is_still_active, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret="79387503012345")
                repository.save(venue)
                mock_check_siret_is_still_active.return_value = True
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="received",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.DRAFT

            @pytest.mark.usefixtures("db_session")
            def test_when_siret_is_not_valid_should_not_create_the_correct_bank_information(
                self, mock_application_details, mock_check_siret_is_still_active, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret="79387503012345")
                repository.save(venue)
                mock_check_siret_is_still_active.return_value = False
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="received",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 0

            @pytest.mark.usefixtures("db_session")
            def test_when_dms_state_is_initiated_should_create_the_correct_bank_information(
                self, mock_application_details, mock_check_siret_is_still_active, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret="79387503012345")
                repository.save(venue)
                mock_check_siret_is_still_active.return_value = True
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="initiated",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.DRAFT

            @pytest.mark.usefixtures("db_session")
            def test_when_no_offerer_is_found_and_status_is_closed_should_raise_and_not_create_bank_information(
                self, mock_application_details, mock_check_siret_is_still_active, app
            ):
                # Given
                application_id = "8"
                mock_check_siret_is_still_active.return_value = True
                offers_factories.VenueFactory(
                    siret="79387503012345", managingOfferer__siren="123456789", businessUnit=None
                )
                bank_information_count = BankInformation.query.count()
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="closed",
                    )
                )

                # When
                with pytest.raises(CannotRegisterBankInformation) as error:
                    self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 0
                assert error.value.errors == {"Offerer": ["Offerer not found"]}

            @pytest.mark.usefixtures("db_session")
            def test_when_no_offerer_is_found_but_status_is_not_closed_should_not_create_bank_information_and_not_raise(
                self, mock_application_details, mock_check_siret_is_still_active, app
            ):
                # Given
                application_id = "8"
                mock_check_siret_is_still_active.return_value = True
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="without_continuation",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 0

            @pytest.mark.usefixtures("db_session")
            def test_when_no_venue_is_found_and_status_is_closed_should_raise_and_not_create_bank_information(
                self, mock_application_details, mock_check_siret_is_still_active, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                repository.save(offerer)
                mock_check_siret_is_still_active.return_value = True
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="closed",
                    )
                )

                # When
                with pytest.raises(CannotRegisterBankInformation) as error:
                    self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 0
                assert error.value.errors == {"Venue": ["Venue not found"]}

            @pytest.mark.usefixtures("db_session")
            def test_when_no_venue_is_found_but_status_is_not_closed_should_not_create_bank_information_and_not_raise(
                self, mock_application_details, mock_check_siret_is_still_active, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                repository.save(offerer)
                mock_check_siret_is_still_active.return_value = True
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="received",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 0

        @patch("pcapi.connectors.api_entreprises.check_siret_is_still_active", return_value=True)
        @patch("pcapi.connectors.dms.api.get_application_details")
        class VenueWitoutSiretTest:
            def setup_method(self):
                self.save_venue_bank_informations = SaveVenueBankInformations(
                    venue_repository=VenueWithBasicInformationSQLRepository(),
                    bank_informations_repository=BankInformationsSQLRepository(),
                )

            @pytest.mark.usefixtures("db_session")
            def test_when_dms_state_is_refused_should_create_the_correct_bank_information(
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret=None, comment="comment", name="VENUE_NAME")
                repository.save(venue)
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="refused",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.REJECTED

            @pytest.mark.usefixtures("db_session")
            def test_when_dms_state_is_without_continuation_should_create_the_correct_bank_information(
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret=None, comment="comment", name="VENUE_NAME")
                repository.save(venue)
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="without_continuation",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.REJECTED

            @pytest.mark.usefixtures("db_session")
            def test_when_dms_state_is_closed_should_create_the_correct_bank_information(
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret=None, comment="comment", name="VENUE_NAME")
                repository.save(venue)
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="closed",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic == "SOGEFRPP"
                assert bank_information.iban == "FR7630007000111234567890144"
                assert bank_information.status == BankInformationStatus.ACCEPTED

            @pytest.mark.usefixtures("db_session")
            def test_when_dms_state_is_received_should_create_the_correct_bank_information(
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret=None, comment="comment", name="VENUE_NAME")
                repository.save(venue)
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="received",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.DRAFT

            @pytest.mark.usefixtures("db_session")
            def test_when_dms_state_is_initiated_should_create_the_correct_bank_information(
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret=None, comment="comment", name="VENUE_NAME")
                repository.save(venue)
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="initiated",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.DRAFT

            @pytest.mark.usefixtures("db_session")
            def test_when_no_offerer_is_found_but_status_is_not_closed_should_not_raise(
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="initiated",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 0

            @pytest.mark.usefixtures("db_session")
            def test_when_no_offerer_is_found_and_state_is_closed_should_raise_and_not_create_bank_information(
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="closed",
                    )
                )

                # When
                with pytest.raises(CannotRegisterBankInformation) as error:
                    self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 0
                assert error.value.errors == {"Offerer": ["Offerer not found"]}

            @pytest.mark.usefixtures("db_session")
            def test_when_no_venue_without_siret_is_found_and_state_is_closed_should_raise_and_not_create_bank_information(
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret="79387503012345")
                repository.save(venue)
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="closed",
                    )
                )

                # When
                with pytest.raises(CannotRegisterBankInformation) as error:
                    self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 0
                assert error.value.errors["Venue"] == ["Venue name not found"]

            @pytest.mark.usefixtures("db_session")
            def test_when_no_venue_is_found_but_status_is_not_closed_should_not_raise(
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                repository.save(offerer)
                mock_application_details.return_value = (
                    venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=8,
                        state="received",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 0

    @patch("pcapi.connectors.api_entreprises.check_siret_is_still_active", return_value=True)
    @patch("pcapi.connectors.dms.api.get_application_details")
    class UpdateBankInformationByApplicationIdTest:
        def setup_method(self):
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        @pytest.mark.usefixtures("db_session")
        def test_when_rib_and_offerer_change_everything_should_be_updated(self, mock_application_details, app):
            # Given
            application_id = "8"
            offerer = create_offerer(siren="793875030")
            venue = create_venue(offerer, siret="79387503012345")
            new_offerer = create_offerer(siren="123456789")
            new_venue = create_venue(new_offerer, siret="12345678912345")
            bank_information = offers_factories.BankInformationFactory(
                applicationId=8,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
            )
            repository.save(new_venue, bank_information)
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret="12345678912345", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8
            )

            # When
            self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == "SOGEFRPP"
            assert bank_information.iban == "FR7630007000111234567890144"
            assert bank_information.offererId == None
            assert bank_information.venueId == new_venue.id

        @pytest.mark.usefixtures("db_session")
        def test_when_status_change_rib_should_be_correctly_updated(self, mock_application_details, app):
            # Given
            application_id = "8"
            offerer = create_offerer(siren="793875030")
            venue = create_venue(offerer, siret="79387503012345")
            bank_information = offers_factories.BankInformationFactory(
                applicationId=8,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                status=BankInformationStatus.ACCEPTED,
            )
            repository.save(offerer, bank_information)
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret="79387503012345", bic="QSDFGH8Z555", iban="NL36INGB2682297498", idx=8, state="initiated"
            )

            # When
            self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == None
            assert bank_information.iban == None
            assert bank_information.status == BankInformationStatus.DRAFT

        @pytest.mark.usefixtures("db_session")
        def test_when_overriding_another_bank_information_should_raise(self, mock_application_details, app):
            # Given
            application_id = "8"
            offerer = create_offerer(siren="793875030")
            venue = create_venue(offerer, siret="79387503012345")
            other_offerer = create_offerer(siren="793875019")
            other_venue = create_venue(other_offerer, siret="79387501912345")
            offers_factories.BankInformationFactory(
                applicationId=8,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
            )
            offers_factories.BankInformationFactory(
                applicationId=79,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=other_venue,
            )
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret="79387501912345", bic="QSDFGH8Z555", iban="NL36INGB2682297498", idx=8
            )

            # When
            with pytest.raises(ApiErrors) as errors:
                self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 2
            assert errors.value.errors['"venueId"'] == [
                "Une entrée avec cet identifiant existe déjà dans notre base de données"
            ]

    @patch("pcapi.connectors.api_entreprises.check_siret_is_still_active", return_value=True)
    @patch("pcapi.connectors.dms.api.get_application_details")
    class UpdateBankInformationByVenueIdTest:
        def setup_method(self):
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        @pytest.mark.usefixtures("db_session")
        def test_when_receive_new_closed_application_should_override_previous_one(self, mock_application_details, app):
            # Given
            application_id = "8"
            offerer = create_offerer(siren="793875030")
            venue = create_venue(offerer, siret="79387503012345")
            bank_information = offers_factories.BankInformationFactory(
                applicationId=79,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                dateModified=datetime(2018, 1, 1),
            )
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret="79387503012345", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8
            )

            # When
            self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == "SOGEFRPP"
            assert bank_information.iban == "FR7630007000111234567890144"
            assert bank_information.applicationId == 8
            assert finance_models.BusinessUnit.query.count() == 1
            business_unit = finance_models.BusinessUnit.query.one()
            assert business_unit.bankAccountId == bank_information.id
            assert venue.businessUnitId == business_unit.id

        @pytest.mark.usefixtures("db_session")
        def test_when_receive_new_application_with_draft_state_should_update_previously_rejected_bank_information(
            self, mock_application_details, app
        ):
            # Given
            application_id = "8"
            offerer = create_offerer(siren="793875030")
            venue = create_venue(offerer, siret="79387503012345")
            bank_information = offers_factories.BankInformationFactory(
                applicationId=79,
                bic=None,
                iban=None,
                venue=venue,
                status=BankInformationStatus.REJECTED,
            )
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret="79387503012345", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state="initiated"
            )

            # When
            self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == None
            assert bank_information.iban == None
            assert bank_information.status == BankInformationStatus.DRAFT

        @pytest.mark.usefixtures("db_session")
        def test_when_receive_new_application_with_lower_status_should_reject(self, mock_application_details, app):
            # Given
            application_id = "8"
            offerer = create_offerer(siren="793875030")
            venue = create_venue(offerer, siret="79387503012345")
            bank_information = offers_factories.BankInformationFactory(
                applicationId=79,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                status=BankInformationStatus.ACCEPTED,
            )
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret="79387503012345", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state="initiated"
            )

            # When
            with pytest.raises(CannotRegisterBankInformation) as error:
                self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == "QSDFGH8Z555"
            assert bank_information.iban == "NL36INGB2682297498"
            assert bank_information.status == BankInformationStatus.ACCEPTED
            assert bank_information.applicationId == 79
            assert error.value.errors == {
                "BankInformation": ["Received application details state does not allow to change bank information"]
            }

        @pytest.mark.usefixtures("db_session")
        def test_when_receive_older_application_should_reject(self, mock_application_details, app):
            # Given
            application_id = "8"
            offerer = create_offerer(siren="793875030")
            venue = create_venue(offerer, siret="79387503012345")
            bank_information = offers_factories.BankInformationFactory(
                applicationId=79,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                dateModified=datetime(2021, 1, 1),
            )
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret="79387503012345", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8
            )

            # When
            with pytest.raises(CannotRegisterBankInformation) as error:
                self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == "QSDFGH8Z555"
            assert bank_information.iban == "NL36INGB2682297498"
            assert bank_information.status == BankInformationStatus.ACCEPTED
            assert bank_information.applicationId == 79
            assert error.value.errors == {"BankInformation": ["Received application details are older than saved one"]}

        @pytest.mark.usefixtures("db_session")
        def test_when_state_is_unknown(self, mock_application_details, app):
            # Given
            application_id = "8"
            offerer = create_offerer(siren="793875030")
            venue = create_venue(offerer, siret="79387503012345")
            repository.save(venue)
            unknown_status = "unknown_status"
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret="79387503012345", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state=unknown_status
            )

            # When
            with pytest.raises(CannotRegisterBankInformation) as error:
                self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 0
            assert error.value.errors == {"BankInformation": f"Unknown Demarches Simplifiées state {unknown_status}"}

        @pytest.mark.usefixtures("db_session")
        def test_raises_an_error_when_bank_information_data_is_invalid(self, mock_application_details, app):
            application_id = "8"
            offerer = OffererFactory(siren="793875030")
            offers_factories.VenueFactory(managingOfferer=offerer, siret="79387503012345", businessUnit=None)
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret="79387503012345", bic="SOG", iban="FR76", idx=8
            )
            with pytest.raises(CannotRegisterBankInformation) as error:
                self.save_venue_bank_informations.execute(application_id)

            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 0
            assert error.value.errors == {
                "bic": ['Le BIC renseigné ("SOG") est invalide'],
                "iban": ['L’IBAN renseigné ("FR76") est invalide'],
            }

        @pytest.mark.usefixtures("db_session")
        def test_raises_an_error_when_no_bank_information_data_is_provided(self, mock_application_details, app):
            application_id = "8"
            offerer = OffererFactory(siren="793875030")
            offers_factories.VenueFactory(managingOfferer=offerer, siret="79387503012345", businessUnit=None)
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret="79387503012345", bic="", iban="", idx=8
            )
            with pytest.raises(CannotRegisterBankInformation) as error:
                self.save_venue_bank_informations.execute(application_id)

            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 0
            assert error.value.errors == {
                "bic": ["Cette information est obligatoire"],
                "iban": ["Cette information est obligatoire"],
            }
