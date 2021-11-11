from datetime import datetime
from unittest.mock import patch

import pytest

from pcapi.domain.bank_information import CannotRegisterBankInformation
from pcapi.infrastructure.repository.bank_informations.bank_informations_sql_repository import (
    BankInformationsSQLRepository,
)
from pcapi.infrastructure.repository.offerer.offerer_sql_repository import OffererSQLRepository
from pcapi.infrastructure.repository.venue.venue_with_basic_information.venue_with_basic_information_sql_repository import (
    VenueWithBasicInformationSQLRepository,
)
from pcapi.model_creators.generic_creators import create_bank_information
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.models import ApiErrors
from pcapi.models import BankInformation
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
    class SaveBankInformationTest:
        @patch("pcapi.domain.demarches_simplifiees.get_application_details")
        class VenueWithSiretTest:
            def setup_method(self):
                self.save_venue_bank_informations = SaveVenueBankInformations(
                    offerer_repository=OffererSQLRepository(),
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
                venue = create_venue(offerer, siret="79387503012345")
                repository.save(venue)
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
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret="79387503012345")
                repository.save(venue)
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
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret="79387503012345")
                repository.save(venue)
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
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret="79387503012345")
                repository.save(venue)
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
            def test_when_dms_state_is_initiated_should_create_the_correct_bank_information(
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                venue = create_venue(offerer, siret="79387503012345")
                repository.save(venue)
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
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
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
                assert error.value.args == ("Offerer not found",)

            @pytest.mark.usefixtures("db_session")
            def test_when_no_offerer_is_found_but_status_is_not_closed_should_not_create_bank_information_and_not_raise(
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
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
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                repository.save(offerer)
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
                assert error.value.args == ("Venue not found",)

            @pytest.mark.usefixtures("db_session")
            def test_when_no_venue_is_found_but_status_is_not_closed_should_not_create_bank_information_and_not_raise(
                self, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerer = create_offerer(siren="793875030")
                repository.save(offerer)
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

        @patch("pcapi.domain.demarches_simplifiees.get_application_details")
        class VenueWitoutSiretTest:
            def setup_method(self):
                self.save_venue_bank_informations = SaveVenueBankInformations(
                    offerer_repository=OffererSQLRepository(),
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
                assert error.value.args == ("Offerer not found",)

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
                assert error.value.args == ("Venue name not found",)

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

    @patch("pcapi.domain.demarches_simplifiees.get_application_details")
    class UpdateBankInformationByApplicationIdTest:
        def setup_method(self):
            self.save_venue_bank_informations = SaveVenueBankInformations(
                offerer_repository=OffererSQLRepository(),
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
            bank_information = create_bank_information(
                application_id=8,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                date_modified=datetime(2012, 1, 1),
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
            bank_information = create_bank_information(
                application_id=8,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                status=BankInformationStatus.ACCEPTED,
                date_modified=datetime(2012, 1, 1),
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
            bank_information = create_bank_information(
                application_id=8,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                date_modified=datetime(2012, 1, 1),
            )
            other_bank_information = create_bank_information(
                application_id=79,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=other_venue,
                date_modified=datetime(2012, 1, 1),
            )
            repository.save(bank_information, other_bank_information)
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

    @patch("pcapi.domain.demarches_simplifiees.get_application_details")
    class UpdateBankInformationByVenueIdTest:
        def setup_method(self):
            self.save_venue_bank_informations = SaveVenueBankInformations(
                offerer_repository=OffererSQLRepository(),
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        @pytest.mark.usefixtures("db_session")
        def test_when_receive_new_closed_application_should_override_previous_one(self, mock_application_details, app):
            # Given
            application_id = "8"
            offerer = create_offerer(siren="793875030")
            venue = create_venue(offerer, siret="79387503012345")
            bank_information = create_bank_information(
                application_id=79,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                date_modified=datetime(2018, 1, 1),
            )
            repository.save(bank_information)
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

        @pytest.mark.usefixtures("db_session")
        def test_when_receive_new_application_with_draft_state_should_update_previously_rejected_bank_information(
            self, mock_application_details, app
        ):
            # Given
            application_id = "8"
            offerer = create_offerer(siren="793875030")
            venue = create_venue(offerer, siret="79387503012345")
            bank_information = create_bank_information(
                application_id=79,
                bic=None,
                iban=None,
                venue=venue,
                date_modified=datetime(2018, 1, 1),
                status=BankInformationStatus.REJECTED,
            )
            repository.save(bank_information)
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
            bank_information = create_bank_information(
                application_id=79,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                date_modified=datetime(2018, 1, 1),
                status=BankInformationStatus.ACCEPTED,
            )
            repository.save(bank_information)
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
            assert error.value.args == ("Received application details state does not allow to change bank information",)

        @pytest.mark.usefixtures("db_session")
        def test_when_receive_older_application_should_reject(self, mock_application_details, app):
            # Given
            application_id = "8"
            offerer = create_offerer(siren="793875030")
            venue = create_venue(offerer, siret="79387503012345")
            bank_information = create_bank_information(
                application_id=79,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                date_modified=datetime(2021, 1, 1),
            )
            repository.save(bank_information)
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
            assert error.value.args == ("Received application details are older than saved one",)

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
            assert error.value.args == (f"Unknown Demarches Simplifiées state {unknown_status}",)
