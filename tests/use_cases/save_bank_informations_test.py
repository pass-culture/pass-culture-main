from unittest.mock import patch, call
from datetime import datetime

import pytest
from use_cases.save_bank_informations import  save_offerer_bank_informations, \
    save_venue_bank_informations
from models import ApiErrors

from connectors.api_demarches_simplifiees import DmsApplicationStates
from models.bank_information import BankInformationStatus
from tests.model_creators.generic_creators import create_bank_information, create_offerer, create_venue
from tests.connector_creators.demarches_simplifiees_creators import offerer_demarche_simplifiee_application_detail_response, \
    venue_demarche_simplifiee_application_detail_response_with_siret, venue_demarche_simplifiee_application_detail_response_without_siret
from repository import repository
from tests.conftest import clean_database
from models import BankInformation
from domain.bank_information import CannotRegisterBankInformation



class SaveOffererBankInformationsTest:
    @patch('use_cases.save_bank_informations.get_application_details')
    class CreateNewBankInformationTest:
        @clean_database
        def test_when_dms_state_is_refused_should_create_the_correct_bank_information(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            repository.save(offerer)
            mock_application_details.return_value = offerer_demarche_simplifiee_application_detail_response(
                siren="793875030", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='refused')

            # When
            save_offerer_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == BankInformationStatus.REJECTED

        @clean_database
        def test_when_dms_state_is_without_continuation_should_create_the_correct_bank_information(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            repository.save(offerer)
            mock_application_details.return_value = offerer_demarche_simplifiee_application_detail_response(
                siren="793875030", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='without_continuation')

            # When
            save_offerer_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == BankInformationStatus.REJECTED

        @clean_database
        def test_when_dms_state_is_closed_should_create_the_correct_bank_information(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            repository.save(offerer)
            mock_application_details.return_value = offerer_demarche_simplifiee_application_detail_response(
                siren="793875030", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='closed')

            # When
            save_offerer_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == "SOGEFRPP"
            assert bank_information.iban == "FR7630007000111234567890144"
            assert bank_information.status == BankInformationStatus.ACCEPTED

        @clean_database
        def test_when_dms_state_is_received_should_create_the_correct_bank_information(self, mock_application_details,
                                                                                  app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            repository.save(offerer)
            mock_application_details.return_value = offerer_demarche_simplifiee_application_detail_response(
                siren="793875030", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='received')

            # When
            save_offerer_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == BankInformationStatus.DRAFT

        @clean_database
        def test_when_dms_state_is_initiated_should_create_the_correct_bank_information(self, mock_application_details,
                                                                                   app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            repository.save(offerer)
            mock_application_details.return_value = offerer_demarche_simplifiee_application_detail_response(
                siren="793875030", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='initiated')

            # When
            save_offerer_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == BankInformationStatus.DRAFT

        @clean_database
        def test_when_no_offerer_siren_specified_should_not_create_bank_information(self, mock_application_details, app):
            # Given
            application_id = '8'
            mock_application_details.return_value = offerer_demarche_simplifiee_application_detail_response(
                siren="793875030", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8)

            # When
            with pytest.raises(CannotRegisterBankInformation) as error:
                save_offerer_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 0
            assert error.value.args == (f'Offerer not found',)

    @patch('use_cases.save_bank_informations.get_application_details')
    class UpdateBankInformationByApplicationIdTest:
        @clean_database
        def test_when_rib_and_offerer_change_everything_should_be_updated(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            new_offerer = create_offerer(siren='793875019')
            bank_information = create_bank_information(
                application_id=8,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                offerer=offerer,
            )
            repository.save(offerer, new_offerer, bank_information)
            mock_application_details.return_value = offerer_demarche_simplifiee_application_detail_response(
                siren="793875019", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8)

            # When
            save_offerer_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == 'SOGEFRPP'
            assert bank_information.iban == 'FR7630007000111234567890144'
            assert bank_information.offererId == new_offerer.id

        @clean_database
        def test_when_status_change_rib_should_be_correctly_updated(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            bank_information = create_bank_information(
                application_id=8,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                offerer=offerer,
                status=BankInformationStatus.ACCEPTED
            )
            repository.save(offerer, bank_information)
            mock_application_details.return_value = offerer_demarche_simplifiee_application_detail_response(
                siren="793875030", bic="QSDFGH8Z555", iban="NL36INGB2682297498", idx=8, state="initiated")

            # When
            save_offerer_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == None
            assert bank_information.iban == None
            assert bank_information.status == BankInformationStatus.DRAFT

        @clean_database
        def test_when_overriding_another_bank_information_should_raise(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            other_offerer = create_offerer(siren='793875019')
            bank_information = create_bank_information(
                application_id=8,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                offerer=offerer,
            )
            other_bank_information = create_bank_information(
                application_id=79,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                offerer=other_offerer,
            )
            repository.save(offerer, other_offerer,
                            bank_information, other_bank_information)
            mock_application_details.return_value = offerer_demarche_simplifiee_application_detail_response(
                siren="793875019", bic="QSDFGH8Z555", iban="NL36INGB2682297498", idx=8)

            # When
            with pytest.raises(ApiErrors) as errors:
                save_offerer_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 2
            print(errors.value.errors)
            assert errors.value.errors['"offererId"'] == [
                'Une entrée avec cet identifiant existe déjà dans notre base de données']

    @patch('use_cases.save_bank_informations.get_application_details')
    class OverrideBankInformationByReffererTest:
        @clean_database
        def test_when_receive_new_closed_application_should_override_previous_one(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            bank_information = create_bank_information(
                application_id=79,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                offerer=offerer,
                date_modified_at_last_provider=datetime(2018, 1, 1)
            )
            repository.save(offerer, bank_information)
            mock_application_details.return_value = offerer_demarche_simplifiee_application_detail_response(
                siren="793875030", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8)

            # When
            save_offerer_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == 'SOGEFRPP'
            assert bank_information.iban == 'FR7630007000111234567890144'
            assert bank_information.applicationId == 8

        @clean_database
        def test_when_receive_new_application_with_draft_state_should_update_previously_rejected_bank_information(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            bank_information = create_bank_information(
                application_id=79,
                bic=None,
                iban=None,
                offerer=offerer,
                date_modified_at_last_provider=datetime(2018, 1, 1),
                status=BankInformationStatus.REJECTED
            )
            repository.save(offerer, bank_information)
            mock_application_details.return_value = offerer_demarche_simplifiee_application_detail_response(
                siren="793875030", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state="initiated")

            # When
            save_offerer_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == None
            assert bank_information.iban == None
            assert bank_information.status == BankInformationStatus.DRAFT

        @clean_database
        def test_when_receive_new_application_with_lower_status_should_reject(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            bank_information = create_bank_information(
                application_id=79,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                offerer=offerer,
                date_modified_at_last_provider=datetime(2018, 1, 1),
                status=BankInformationStatus.ACCEPTED
            )
            repository.save(offerer, bank_information)
            mock_application_details.return_value = offerer_demarche_simplifiee_application_detail_response(
                siren="793875030", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state="initiated")

            # When
            save_offerer_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == 'QSDFGH8Z555'
            assert bank_information.iban == "NL36INGB2682297498"
            assert bank_information.status == BankInformationStatus.ACCEPTED
            assert bank_information.applicationId == 79

        @clean_database
        def test_when_receive_older_application_should_reject(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            bank_information = create_bank_information(
                application_id=79,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                offerer=offerer,
                date_modified_at_last_provider=datetime(2020, 1, 1)
            )
            repository.save(offerer, bank_information)
            mock_application_details.return_value = offerer_demarche_simplifiee_application_detail_response(
                siren="793875030", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8)

            # When
            save_offerer_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == 'QSDFGH8Z555'
            assert bank_information.iban == "NL36INGB2682297498"
            assert bank_information.status == BankInformationStatus.ACCEPTED
            assert bank_information.applicationId == 79


class SaveVenueBankInformationsTest:
    class CreateNewBankInformationTest:
        @patch('use_cases.save_bank_informations.get_application_details')
        class VenueWithSiretTest:
            @clean_database
            def test_when_dms_state_is_refused_should_create_the_correct_bank_information(self, mock_application_details, app):
                # Given
                application_id = '8'
                offerer = create_offerer(siren='793875030')
                venue = create_venue(offerer, siret='79387503012345')
                repository.save(venue)
                mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='refused')

                # When
                save_venue_bank_informations(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.REJECTED

            @clean_database
            def test_when_dms_state_is_without_continuation_should_create_the_correct_bank_information(self, mock_application_details, app):
                # Given
                application_id = '8'
                offerer = create_offerer(siren='793875030')
                venue = create_venue(offerer, siret='79387503012345')
                repository.save(venue)
                mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='without_continuation')

                # When
                save_venue_bank_informations(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.REJECTED

            @clean_database
            def test_when_dms_state_is_closed_should_create_the_correct_bank_information(self, mock_application_details, app):
                # Given
                application_id = '8'
                offerer = create_offerer(siren='793875030')
                venue = create_venue(offerer, siret='79387503012345')
                repository.save(venue)
                mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='closed')

                # When
                save_venue_bank_informations(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic == "SOGEFRPP"
                assert bank_information.iban == "FR7630007000111234567890144"
                assert bank_information.status == BankInformationStatus.ACCEPTED

            @clean_database
            def test_when_dms_state_is_received_should_create_the_correct_bank_information(self, mock_application_details,
                                                                                      app):
                # Given
                application_id = '8'
                offerer = create_offerer(siren='793875030')
                venue = create_venue(offerer, siret='79387503012345')
                repository.save(venue)
                mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='received')

                # When
                save_venue_bank_informations(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.DRAFT

            @clean_database
            def test_when_dms_state_is_initiated_should_create_the_correct_bank_information(self, mock_application_details,
                                                                                       app):
                # Given
                application_id = '8'
                offerer = create_offerer(siren='793875030')
                venue = create_venue(offerer, siret='79387503012345')
                repository.save(venue)
                mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='initiated')

                # When
                save_venue_bank_informations(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.DRAFT

            @clean_database
            def test_when_no_venue_siret_specified_should_not_create_bank_information(self, mock_application_details, app):
                # Given
                application_id = '8'
                offerer = create_offerer(siren='793875030')
                repository.save(offerer)
                mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8)

                # When
                with pytest.raises(CannotRegisterBankInformation) as error:
                    save_venue_bank_informations(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 0
                assert error.value.args == (f'Venue not found',)

        @patch('use_cases.save_bank_informations.get_application_details')
        class VenueWitoutSiretTest:
            @clean_database
            def test_when_dms_state_is_refused_should_create_the_correct_bank_information(self, mock_application_details, app):
                # Given
                application_id = '8'
                offerer = create_offerer(siren='793875030')
                venue = create_venue(offerer, siret=None,
                                     comment='comment', name='VENUE_NAME')
                repository.save(venue)
                mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_without_siret(
                    siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='refused')

                # When
                save_venue_bank_informations(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.REJECTED

            @clean_database
            def test_when_dms_state_is_without_continuation_should_create_the_correct_bank_information(self, mock_application_details, app):
                # Given
                application_id = '8'
                offerer = create_offerer(siren='793875030')
                venue = create_venue(offerer, siret=None,
                                     comment='comment', name='VENUE_NAME')
                repository.save(venue)
                mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_without_siret(
                    siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='without_continuation')

                # When
                save_venue_bank_informations(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.REJECTED

            @clean_database
            def test_when_dms_state_is_closed_should_create_the_correct_bank_information(self, mock_application_details, app):
                # Given
                application_id = '8'
                offerer = create_offerer(siren='793875030')
                venue = create_venue(offerer, siret=None,
                                     comment='comment', name='VENUE_NAME')
                repository.save(venue)
                mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_without_siret(
                    siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='closed')

                # When
                save_venue_bank_informations(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic == "SOGEFRPP"
                assert bank_information.iban == "FR7630007000111234567890144"
                assert bank_information.status == BankInformationStatus.ACCEPTED

            @clean_database
            def test_when_dms_state_is_received_should_create_the_correct_bank_information(self, mock_application_details,
                                                                                      app):
                # Given
                application_id = '8'
                offerer = create_offerer(siren='793875030')
                venue = create_venue(offerer, siret=None,
                                     comment='comment', name='VENUE_NAME')
                repository.save(venue)
                mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_without_siret(
                    siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='received')

                # When
                save_venue_bank_informations(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.DRAFT

            @clean_database
            def test_when_dms_state_is_initiated_should_create_the_correct_bank_information(self, mock_application_details,
                                                                                       app):
                # Given
                application_id = '8'
                offerer = create_offerer(siren='793875030')
                venue = create_venue(offerer, siret=None,
                                     comment='comment', name='VENUE_NAME')
                repository.save(venue)
                mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_without_siret(
                    siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state='initiated')

                # When
                save_venue_bank_informations(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 1
                bank_information = BankInformation.query.one()
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.DRAFT

            @clean_database
            def test_when_no_venue_without_siret_specified_should_not_create_bank_information(self, mock_application_details, app):
                # Given
                application_id = '8'
                offerer = create_offerer(siren='793875030')
                venue = create_venue(offerer, siret='79387503012345')
                repository.save(venue)
                mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_without_siret(
                    siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8)

                # When
                with pytest.raises(CannotRegisterBankInformation) as error:
                    save_venue_bank_informations(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 0
                assert error.value.args == (f'Venue name not found',)

    @patch('use_cases.save_bank_informations.get_application_details')
    class UpdateBankInformationByApplicationIdTest:
        @clean_database
        def test_when_rib_and_offerer_change_everything_should_be_updated(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            new_offerer = create_offerer(siren='793875019')
            new_venue = create_venue(new_offerer, siret='79387501912345')
            bank_information = create_bank_information(
                application_id=8,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                offerer=offerer,
            )
            repository.save(offerer, new_venue, bank_information)
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret='79387501912345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8)

            # When
            save_venue_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == 'SOGEFRPP'
            assert bank_information.iban == 'FR7630007000111234567890144'
            assert bank_information.offererId == None
            assert bank_information.venueId == new_venue.id

        @clean_database
        def test_when_status_change_rib_should_be_correctly_updated(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            venue = create_venue(offerer, siret='79387503012345')
            bank_information = create_bank_information(
                application_id=8,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                venue=venue,
                status=BankInformationStatus.ACCEPTED
            )
            repository.save(offerer, bank_information)
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret='79387503012345', bic="QSDFGH8Z555", iban="NL36INGB2682297498", idx=8, state="initiated")

            # When
            save_venue_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == None
            assert bank_information.iban == None
            assert bank_information.status == BankInformationStatus.DRAFT

        @clean_database
        def test_when_overriding_another_bank_information_should_raise(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            venue = create_venue(offerer, siret='79387503012345')
            other_offerer = create_offerer(siren='793875019')
            other_venue = create_venue(other_offerer, siret='79387501912345')
            bank_information = create_bank_information(
                application_id=8,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                venue=venue,
            )
            other_bank_information = create_bank_information(
                application_id=79,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                venue=other_venue,
            )
            repository.save(bank_information, other_bank_information)
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret='79387501912345', bic="QSDFGH8Z555", iban="NL36INGB2682297498", idx=8)

            # When
            with pytest.raises(ApiErrors) as errors:
                save_venue_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 2
            print(errors.value.errors)
            assert errors.value.errors['"venueId"'] == [
                'Une entrée avec cet identifiant existe déjà dans notre base de données']

    @patch('use_cases.save_bank_informations.get_application_details')
    class OverrideBankInformationByReffererTest:
        @clean_database
        def test_when_receive_new_closed_application_should_override_previous_one(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            venue = create_venue(offerer, siret='79387503012345')
            bank_information = create_bank_information(
                application_id=79,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                venue=venue,
                date_modified_at_last_provider=datetime(2018, 1, 1)
            )
            repository.save(bank_information)
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8)

            # When
            save_venue_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == 'SOGEFRPP'
            assert bank_information.iban == 'FR7630007000111234567890144'
            assert bank_information.applicationId == 8

        @clean_database
        def test_when_receive_new_application_with_draft_state_should_update_previously_rejected_bank_information(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            venue = create_venue(offerer, siret='79387503012345')
            bank_information = create_bank_information(
                application_id=79,
                bic=None,
                iban=None,
                venue=venue,
                date_modified_at_last_provider=datetime(2018, 1, 1),
                status=BankInformationStatus.REJECTED
            )
            repository.save(bank_information)
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state="initiated")

            # When
            save_venue_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == None
            assert bank_information.iban == None
            assert bank_information.status == BankInformationStatus.DRAFT

        @clean_database
        def test_when_receive_new_application_with_lower_status_should_reject(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            venue = create_venue(offerer, siret='79387503012345')
            bank_information = create_bank_information(
                application_id=79,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                venue=venue,
                date_modified_at_last_provider=datetime(2018, 1, 1),
                status=BankInformationStatus.ACCEPTED
            )
            repository.save(bank_information)
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8, state="initiated")

            # When
            save_venue_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == 'QSDFGH8Z555'
            assert bank_information.iban == "NL36INGB2682297498"
            assert bank_information.status == BankInformationStatus.ACCEPTED
            assert bank_information.applicationId == 79

        @clean_database
        def test_when_receive_older_application_should_reject(self, mock_application_details, app):
            # Given
            application_id = '8'
            offerer = create_offerer(siren='793875030')
            venue = create_venue(offerer, siret='79387503012345')
            bank_information = create_bank_information(
                application_id=79,
                bic='QSDFGH8Z555',
                iban="NL36INGB2682297498",
                venue=venue,
                date_modified_at_last_provider=datetime(2020, 1, 1)
            )
            repository.save(bank_information)
            mock_application_details.return_value = venue_demarche_simplifiee_application_detail_response_with_siret(
                siret='79387503012345', bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=8)

            # When
            save_venue_bank_informations(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == 'QSDFGH8Z555'
            assert bank_information.iban == "NL36INGB2682297498"
            assert bank_information.status == BankInformationStatus.ACCEPTED
            assert bank_information.applicationId == 79
