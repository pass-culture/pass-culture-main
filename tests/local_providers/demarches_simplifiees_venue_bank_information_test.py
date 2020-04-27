from datetime import datetime
from unittest.mock import patch, ANY

from local_providers import VenueBankInformationProvider
from local_providers import BankInformationProvider
from models import BankInformation, LocalProviderEvent
from models.local_provider_event import LocalProviderEventType
from repository import repository
from repository.provider_queries import get_provider_by_local_class
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_bank_information
from tests.model_creators.provider_creators import provider_test, activate_provider
from utils.date import DATE_ISO_FORMAT


class TestableVenueBankInformationProvider(VenueBankInformationProvider):
    def __init__(self):
        """
        Empty constructor that makes this class testable :
        no API call is made at instantiation time
        """
        pass


def demarche_simplifiee_application_detail_response(siret, bic, iban, idx=1, updated_at="2019-01-21T18:55:03.387Z", siren=None):
    return {
        "dossier": {
            "id": idx,
            "updated_at": updated_at,
            "state": "closed",
            "entreprise": {
                "siren": siren or siret[0: 9],
            },
            "etablissement": {
                "siret": siret,
            },
            "champs": [
                {
                    "value": siret,
                    "type_de_champ": {
                        "id": 782800,
                        "libelle": "Si vous souhaitez renseigner les coordonn\u00e9es bancaires d'un lieu avec SIRET, merci de saisir son SIRET :",
                    },
                    "etablissement": {
                        "siret": siret,
                    },
                    "entreprise": {
                        "siren": siret[0: 9],
                    }
                },
                {
                    "value": "",
                    "type_de_champ": {
                        "id": 909032,
                        "libelle": "Si vous souhaitez renseigner les coordonn\\u00e9es bancaires d\'un lieu sans SIRET, merci de saisir le \"Nom du lieu\", \\u00e0 l\'identique de celui dans le pass Culture Pro :",
                    }
                },
                {
                    "value": iban,
                    "type_de_champ": {
                        "id": 352722,
                        "libelle": "IBAN",
                    }
                },
                {
                    "value": bic,
                    "type_de_champ": {
                        "id": 352727,
                        "libelle": "BIC",
                    }
                }
            ]
        }
    }


def create_demarche_simplifiee_application_detail_response_without_venue_siret(siret, bic, iban, idx=1, updated_at="2019-01-21T18:55:03.387Z", venue_name='VENUE WITHOUT SIRET'):
    return {
        "dossier": {
            "id": idx,
            "updated_at": updated_at,
            "state": "closed",
            "entreprise": {
                "siren": siret[0: 9],
            },
            "etablissement": {
                "siret": siret,
            },
            "champs": [
                {
                    "value": "",
                    "type_de_champ": {
                        "id": 782800,
                        "libelle": "Si vous souhaitez renseigner les coordonn\u00e9es bancaires d'un lieu avec SIRET, merci de saisir son SIRET :",
                    },
                    "etablissement": None,
                    "entreprise": None
                },
                {
                    "value": venue_name,
                    "type_de_champ": {
                        "id": 909032,
                        "libelle": "Si vous souhaitez renseigner les coordonn\u00e9es bancaires d'un lieu sans SIRET, merci de saisir le \"Nom du lieu\", \u00e0 l'identique de celui dans le pass Culture Pro :",
                    }
                },
                {
                    "value": iban,
                    "type_de_champ": {
                        "id": 352722,
                        "libelle": "IBAN",
                    }
                },
                {
                    "value": bic,
                    "type_de_champ": {
                        "id": 352727,
                        "libelle": "BIC",
                    }
                }
            ]
        }
    }


class VenueBankInformationProviderTest:
    @patch(
        'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
    @clean_database
    def test_provider_creates_nothing_if_no_data_retrieved_from_api(self, get_application_details,
                                                                    get_all_application_ids_for_demarche_simplifiee,
                                                                    app):
        # Given
        get_application_details.return_value = {}
        get_all_application_ids_for_demarche_simplifiee.return_value = []
        venue_bank_information_provider = VenueBankInformationProvider()

        # When
        venue_bank_information_provider.updateObjects()

        # Then
        assert BankInformation.query.count() == 0

    @patch(
        'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
    @clean_database
    def test_provider_does_not_save_bank_information_if_wrong_bic_or_iban_but_continues_flow(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1, 2]
        get_application_details.side_effect = [
            demarche_simplifiee_application_detail_response(siret="42486171400014",
                                                            bic="wrong_bic",
                                                            iban="wrong_iban",
                                                            idx=1,
                                                            updated_at="2020-04-17T12:56:57.529Z"),
            demarche_simplifiee_application_detail_response(siret="12345678912345",
                                                            bic="BDFEFR2LCCB",
                                                            iban="FR7630006000011234567890189",
                                                            idx=2,
                                                            updated_at="2020-04-17T12:56:57.529Z")
        ]
        offerer_ko = create_offerer(siren='424861714')
        venue_ko = create_venue(offerer_ko, siret='42486171400014')
        offerer_ok = create_offerer(siren="123456789")
        venue_ok = create_venue(offerer_ok, siret='12345678912345')
        repository.save(venue_ko, venue_ok)
        activate_provider('VenueBankInformationProvider')
        venue_bank_information_provider = VenueBankInformationProvider()

        # When
        venue_bank_information_provider.updateObjects()

        # then
        bank_information = BankInformation.query.all()
        assert len(bank_information) == 1
        assert bank_information[0].applicationId == 2
        local_provider_event = LocalProviderEvent.query.filter_by(
            type=LocalProviderEventType.SyncError).one()
        assert local_provider_event.payload == 'ApiErrors'

    @patch(
        'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
    @clean_database
    def test_calls_get_all_application_ids_with_1900_01_01_when_table_bank_information_is_empty(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1]
        get_application_details.return_value = demarche_simplifiee_application_detail_response(
            siret="12345678912345",
            bic="BDFEFR2LCCB",
            iban="FR7630006000011234567890189",
            idx=1,
            updated_at="2020-04-17T12:56:57.529Z")
        activate_provider('VenueBankInformationProvider')
        bank_information_provider = VenueBankInformationProvider()

        # when
        bank_information_provider.updateObjects()

        # then
        get_all_application_ids_for_demarche_simplifiee.assert_called_with(ANY, ANY,
                                                                           datetime(1900, 1, 1))

    @patch(
        'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
    @clean_database
    def test_get_all_application_ids_with_last_update_from_table_bank_information(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1]
        get_application_details.return_value = demarche_simplifiee_application_detail_response(
            siret="12345678912345",
            bic="BDFEFR2LCCB",
            iban="FR7630006000011234567890189",
            idx=2,
            updated_at="2020-04-17T12:56:57.529Z")
        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer, siret='12345678912345')

        bank_information = create_bank_information(id_at_providers='12345678912345',
                                                   date_modified_at_last_provider=datetime(
                                                       2019, 1, 1),
                                                   last_provider_id=get_provider_by_local_class(
                                                       'VenueBankInformationProvider').id,
                                                   venue=venue)
        repository.save(bank_information)
        activate_provider('VenueBankInformationProvider')
        venue_bank_information_provider = VenueBankInformationProvider()

        # When
        venue_bank_information_provider.updateObjects()

        # then
        get_all_application_ids_for_demarche_simplifiee.assert_called_with(ANY, ANY,
                                                                           datetime(2019, 1, 1))

    @patch(
        'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
    @clean_database
    def test_provider_creates_one_bank_information_and_format_IBAN_and_BIC(self,
                                                                           get_application_details,
                                                                           get_all_application_ids_for_demarche_simplifiee,
                                                                           app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1]
        get_application_details.return_value = demarche_simplifiee_application_detail_response(
            siret="12345678912345",
            bic="bdfefR2LCCB",
            iban="FR76 3000 6000 0112 3456 7890 189",
            idx=2,
            updated_at="2020-04-17T12:56:57.529Z")

        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer, siret='12345678912345')

        repository.save(venue)
        activate_provider('VenueBankInformationProvider')
        venue_bank_information_provider = VenueBankInformationProvider()

        # When
        venue_bank_information_provider.updateObjects()

        # Then
        bank_information = BankInformation.query.one()
        assert bank_information.iban == 'FR7630006000011234567890189'
        assert bank_information.bic == 'BDFEFR2LCCB'

    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID': '27456'})
    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_TOKEN': 'cvNjy0RhfULAE3TMMTCkAQmD5p7bVw3s'})
    @patch(
        'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
    @clean_database
    def test_provider_request_application_ids_using_given_date(self,
                                                               get_application_details,
                                                               get_all_application_ids_for_demarche_simplifiee,
                                                               app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = []
        offerer = create_offerer(siren='793875030')
        offerer2 = create_offerer(siren='793875019')
        venue = create_venue(offerer, siret="79387503012345")
        venue2 = create_venue(offerer2, siret="79387501912345")
        bank_information = create_bank_information(id_at_providers='793875030',
                                                   date_modified_at_last_provider=datetime(
                                                       2019, 1, 1),
                                                   last_provider_id=get_provider_by_local_class(
                                                       'VenueBankInformationProvider').id,
                                                   venue=venue)
        bank_information2 = create_bank_information(id_at_providers='793875019',
                                                    date_modified_at_last_provider=datetime(
                                                        2020, 1, 1),
                                                    last_provider_id=get_provider_by_local_class(
                                                        'VenueBankInformationProvider').id,
                                                    venue=venue2)
        repository.save(bank_information, bank_information2)
        provider_object = VenueBankInformationProvider(
            minimum_requested_datetime=datetime(2019, 6, 1))
        provider_object.provider.isActive = True
        repository.save(provider_object.provider)

        # When
        provider_object.updateObjects()

        # Then
        get_all_application_ids_for_demarche_simplifiee.assert_called_once_with(
            '27456',
            'cvNjy0RhfULAE3TMMTCkAQmD5p7bVw3s',
            datetime(2019, 6, 1)
        )

    class VenueWithSiretTest:
        @patch(
            'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
        @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
        @clean_database
        def test_provider_creates_two_objects_when_payload_has_two_valid_applications(
                self,
                get_application_details,
                get_all_application_ids_for_demarche_simplifiee,
                app):
            # Given
            get_all_application_ids_for_demarche_simplifiee.return_value = [
                1, 2]
            get_application_details.side_effect = [
                demarche_simplifiee_application_detail_response(siret="42486171400014",
                                                                bic="BDFEFR2LCCB",
                                                                iban="FR7630006000011234567890189",
                                                                idx=1,
                                                                updated_at="2020-04-17T12:56:57.529Z"),
                demarche_simplifiee_application_detail_response(siret="12345678912345",
                                                                bic="BDFEFR2LCCB",
                                                                iban="FR7630006000011234567890189",
                                                                idx=2,
                                                                updated_at="2020-04-17T12:56:57.529Z")
            ]
            offerer1 = create_offerer(siren='424861714')
            venue1 = create_venue(offerer1, siret='42486171400014')
            offerer2 = create_offerer(siren='123456789')
            venue2 = create_venue(offerer2, siret='12345678912345')
            repository.save(venue1, venue2)
            venue_id1 = venue1.id
            venue_id2 = venue2.id
            activate_provider('VenueBankInformationProvider')
            venue_bank_information_provider = VenueBankInformationProvider()

            # When
            venue_bank_information_provider.updateObjects()

            # Then
            bank_information1 = BankInformation.query.filter_by(
                applicationId=1).first()
            bank_information2 = BankInformation.query.filter_by(
                applicationId=2).first()
            assert BankInformation.query.count() == 2
            assert bank_information1.iban == 'FR7630006000011234567890189'
            assert bank_information1.bic == 'BDFEFR2LCCB'
            assert bank_information1.applicationId == 1
            assert bank_information1.offererId == None
            assert bank_information1.venueId == venue_id1
            assert bank_information1.idAtProviders == '42486171400014'
            assert bank_information2.iban == 'FR7630006000011234567890189'
            assert bank_information2.bic == 'BDFEFR2LCCB'
            assert bank_information2.applicationId == 2
            assert bank_information2.offererId == None
            assert bank_information2.venueId == venue_id2
            assert bank_information2.idAtProviders == '12345678912345'

        @patch(
            'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
        @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
        @clean_database
        def test_provider_does_not_create_bank_information_if_siret_unknown(
                self,
                get_application_details,
                get_all_application_ids_for_demarche_simplifiee,
                app):
            # Given
            get_all_application_ids_for_demarche_simplifiee.return_value = [1]
            get_application_details.return_value = demarche_simplifiee_application_detail_response(
                siret="42486171400014",
                bic="BDFEFR2LCCB",
                iban="FR7630006000011234567890189",
                idx=1,
                updated_at="2020-04-17T12:56:57.529Z")
            activate_provider('VenueBankInformationProvider')
            venue_bank_information_provider = VenueBankInformationProvider()

            # When
            venue_bank_information_provider.updateObjects()

            # Then
            assert BankInformation.query.count() == 0
            sync_error = LocalProviderEvent.query.filter_by(
                type=LocalProviderEventType.SyncError).first()
            assert sync_error.payload == 'Offerer not found for application id 1'
            events = LocalProviderEvent.query.all()
            assert events[0].type == LocalProviderEventType.SyncStart
            assert events[1].type == LocalProviderEventType.SyncError
            assert events[2].type == LocalProviderEventType.SyncEnd

        @patch(
            'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
        @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
        @clean_database
        def test_provider_does_not_create_bank_information_with_siret_of_another_offerer(
                self,
                get_application_details,
                get_all_application_ids_for_demarche_simplifiee,
                app):
            # Given
            offerer1 = create_offerer(siren='424861714')
            offerer2 = create_offerer(siren='123456789')
            venue2 = create_venue(offerer2, siret='12345678912345')
            get_all_application_ids_for_demarche_simplifiee.return_value = [1]
            get_application_details.return_value = demarche_simplifiee_application_detail_response(
                siret="12345678912345",
                siren='424861714',
                bic="BDFEFR2LCCB",
                iban="FR7630006000011234567890189",
                idx=1,
                updated_at="2020-04-17T12:56:57.529Z")
            activate_provider('VenueBankInformationProvider')
            venue_bank_information_provider = VenueBankInformationProvider()

            # When
            venue_bank_information_provider.updateObjects()

            # Then
            assert BankInformation.query.count() == 0
            sync_error = LocalProviderEvent.query.filter_by(
                type=LocalProviderEventType.SyncError).first()
            assert sync_error.payload == 'Offerer not found for application id 1'
            events = LocalProviderEvent.query.all()
            assert events[0].type == LocalProviderEventType.SyncStart
            assert events[1].type == LocalProviderEventType.SyncError
            assert events[2].type == LocalProviderEventType.SyncEnd

        @patch(
            'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
        @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
        @clean_database
        def test_provider_updates_existing_bank_information(
                self,
                get_application_details,
                get_all_application_ids_for_demarche_simplifiee,
                app):
            # Given
            get_all_application_ids_for_demarche_simplifiee.return_value = [1]
            get_application_details.return_value = demarche_simplifiee_application_detail_response(
                siret="42486171400014",
                bic="BDFEFR2LCCB",
                iban="FR7630006000011234567890189",
                idx=2,
                updated_at="2020-04-17T12:56:57.529Z")
            offerer = create_offerer(siren='424861714')
            venue = create_venue(offerer, siret='42486171400014')
            bank_information = create_bank_information(
                id_at_providers="42486171400014", venue=venue, bic="SOGEFRPP", iban="FR7630007000111234567890144")
            repository.save(bank_information)
            activate_provider('VenueBankInformationProvider')
            venue_bank_information_provider = VenueBankInformationProvider()

            # When
            venue_bank_information_provider.updateObjects()

            # Then
            updated_bank_information = BankInformation.query.one()
            assert updated_bank_information.applicationId == 2
            assert updated_bank_information.iban == "FR7630006000011234567890189"
            assert updated_bank_information.bic == "BDFEFR2LCCB"

    class VenueWithoutSiretTest:
        @patch(
            'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
        @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
        @clean_database
        def test_provider_creates_two_objects_when_payload_has_two_valid_applications(
                self,
                get_application_details,
                get_all_application_ids_for_demarche_simplifiee,
                app):
            # Given
            get_all_application_ids_for_demarche_simplifiee.return_value = [
                1, 2]
            get_application_details.side_effect = [
                create_demarche_simplifiee_application_detail_response_without_venue_siret(siret="42486171400014",
                                                                                           bic="BDFEFR2LCCB",
                                                                                           iban="FR7630006000011234567890189",
                                                                                           idx=1,
                                                                                           updated_at="2020-04-17T12:56:57.529Z"),
                create_demarche_simplifiee_application_detail_response_without_venue_siret(siret="12345678912345",
                                                                                           bic="BDFEFR2LCCB",
                                                                                           iban="FR7630006000011234567890189",
                                                                                           idx=2,
                                                                                           updated_at="2020-04-17T12:56:57.529Z")
            ]
            offerer1 = create_offerer(siren='424861714')
            venue1 = create_venue(
                offerer1, siret=None, comment='without siret venue', name='VENUE WITHOUT SIRET')
            offerer2 = create_offerer(siren='123456789')
            venue2 = create_venue(
                offerer2, siret=None, comment='without siret venue', name='VENUE WITHOUT SIRET')
            repository.save(venue1, venue2)
            venue_id1 = venue1.id
            venue_id2 = venue2.id
            activate_provider('VenueBankInformationProvider')
            venue_bank_information_provider = VenueBankInformationProvider()

            # When
            venue_bank_information_provider.updateObjects()

            # Then
            bank_information1 = BankInformation.query.filter_by(
                applicationId=1).first()
            bank_information2 = BankInformation.query.filter_by(
                applicationId=2).first()
            assert BankInformation.query.count() == 2
            assert bank_information1.iban == 'FR7630006000011234567890189'
            assert bank_information1.bic == 'BDFEFR2LCCB'
            assert bank_information1.applicationId == 1
            assert bank_information1.offererId == None
            assert bank_information1.venueId == venue_id1
            assert bank_information1.idAtProviders == '424861714VENUE WITHOUT SIRET'
            assert bank_information2.iban == 'FR7630006000011234567890189'
            assert bank_information2.bic == 'BDFEFR2LCCB'
            assert bank_information2.applicationId == 2
            assert bank_information2.offererId == None
            assert bank_information2.venueId == venue_id2
            assert bank_information2.idAtProviders == '123456789VENUE WITHOUT SIRET'

        @patch(
            'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
        @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
        @clean_database
        def test_provider_does_not_create_bank_information_if_name_unknown(
                self,
                get_application_details,
                get_all_application_ids_for_demarche_simplifiee,
                app):
            # Given
            get_all_application_ids_for_demarche_simplifiee.return_value = [1]
            get_application_details.return_value = create_demarche_simplifiee_application_detail_response_without_venue_siret(
                siret="42486171400014",
                bic="BDFEFR2LCCB",
                iban="FR7630006000011234567890189",
                idx=1,
                updated_at="2020-04-17T12:56:57.529Z",
                venue_name='NOT MATCHING NAME')
            activate_provider('VenueBankInformationProvider')
            venue_bank_information_provider = VenueBankInformationProvider()

            # When
            venue_bank_information_provider.updateObjects()

            # Then
            assert BankInformation.query.count() == 0
            sync_error = LocalProviderEvent.query.filter_by(
                type=LocalProviderEventType.SyncError).first()
            assert sync_error.payload == 'Offerer not found for application id 1'
            events = LocalProviderEvent.query.all()
            assert events[0].type == LocalProviderEventType.SyncStart
            assert events[1].type == LocalProviderEventType.SyncError
            assert events[2].type == LocalProviderEventType.SyncEnd

        @patch(
            'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
        @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
        @clean_database
        def test_provider_does_not_create_bank_information_if_name_of_another_offerer_s_venue(
                self,
                get_application_details,
                get_all_application_ids_for_demarche_simplifiee,
                app):
            # Given
            offerer1 = create_offerer(siren='424861714')
            offerer2 = create_offerer(siren='123456789')
            venue2 = create_venue(offerer2, name='VENUE WITHOUT SIRET')
            get_all_application_ids_for_demarche_simplifiee.return_value = [1]
            get_application_details.return_value = create_demarche_simplifiee_application_detail_response_without_venue_siret(
                siret="42486171400014",
                bic="BDFEFR2LCCB",
                iban="FR7630006000011234567890189",
                idx=1,
                updated_at="2020-04-17T12:56:57.529Z",
                venue_name='VENUE WITHOUT SIRET')
            activate_provider('VenueBankInformationProvider')
            venue_bank_information_provider = VenueBankInformationProvider()

            # When
            venue_bank_information_provider.updateObjects()

            # Then
            assert BankInformation.query.count() == 0
            sync_error = LocalProviderEvent.query.filter_by(
                type=LocalProviderEventType.SyncError).first()
            assert sync_error.payload == 'Offerer not found for application id 1'
            events = LocalProviderEvent.query.all()
            assert events[0].type == LocalProviderEventType.SyncStart
            assert events[1].type == LocalProviderEventType.SyncError
            assert events[2].type == LocalProviderEventType.SyncEnd

        @patch(
            'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
        @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
        @clean_database
        def test_provider_does_not_create_bank_information_if_there_are_several_venues_with_same_name(
                self,
                get_application_details,
                get_all_application_ids_for_demarche_simplifiee,
                app):
            # Given
            get_all_application_ids_for_demarche_simplifiee.return_value = [1]
            get_application_details.return_value = create_demarche_simplifiee_application_detail_response_without_venue_siret(
                siret="42486171400014",
                bic="BDFEFR2LCCB",
                iban="FR7630006000011234567890189",
                idx=1,
                updated_at="2020-04-17T12:56:57.529Z",
                venue_name='VENUE WITH SAME NAME')
            offerer = create_offerer(siren='424861714')
            venue1 = create_venue(
                offerer, siret=None, comment='without siret venue', name='VENUE WITH SAME NAME')
            venue2 = create_venue(
                offerer, siret=None, comment='without siret venue', name='VENUE WITH SAME NAME')
            repository.save(venue1, venue2)
            activate_provider('VenueBankInformationProvider')
            venue_bank_information_provider = VenueBankInformationProvider()

            # When
            venue_bank_information_provider.updateObjects()

            # Then
            assert BankInformation.query.count() == 0
            sync_error = LocalProviderEvent.query.filter_by(
                type=LocalProviderEventType.SyncError).first()
            assert sync_error.payload == 'Multiple venues found for application id 1'
            events = LocalProviderEvent.query.all()
            assert events[0].type == LocalProviderEventType.SyncStart
            assert events[1].type == LocalProviderEventType.SyncError
            assert events[2].type == LocalProviderEventType.SyncEnd

        @patch(
            'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
        @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
        @clean_database
        def test_provider_updates_existing_bank_information(
                self,
                get_application_details,
                get_all_application_ids_for_demarche_simplifiee,
                app):
            # Given
            get_all_application_ids_for_demarche_simplifiee.return_value = [1]
            get_application_details.return_value = create_demarche_simplifiee_application_detail_response_without_venue_siret(
                siret="42486171400014",
                bic="BDFEFR2LCCB",
                iban="FR7630006000011234567890189",
                idx=2,
                updated_at="2020-04-17T12:56:57.529Z")
            offerer = create_offerer(siren='424861714')
            venue = create_venue(
                offerer, siret=None, name='VENUE WITHOUT SIRET', comment='venue whithout siret')
            bank_information = create_bank_information(
                id_at_providers="424861714VENUE WITHOUT SIRET", venue=venue, bic="SOGEFRPP", iban="FR7630007000111234567890144")
            repository.save(bank_information)
            activate_provider('VenueBankInformationProvider')
            venue_bank_information_provider = VenueBankInformationProvider()

            # When
            venue_bank_information_provider.updateObjects()

            # Then
            updated_bank_information = BankInformation.query.one()
            assert updated_bank_information.applicationId == 2
            assert updated_bank_information.iban == "FR7630006000011234567890189"
            assert updated_bank_information.bic == "BDFEFR2LCCB"

@patch(
    'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
@patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
@clean_database
def test_provider_can_handle_payload_with_both_venues_with_siret_and_venues_without(
        get_application_details,
        get_all_application_ids_for_demarche_simplifiee,
        app):
    # Given
    get_all_application_ids_for_demarche_simplifiee.return_value = [
        1, 2]
    get_application_details.side_effect = [
        demarche_simplifiee_application_detail_response(siret="42486171400014",
                                                        bic="BDFEFR2LCCB",
                                                        iban="FR7630006000011234567890189",
                                                        idx=1,
                                                        updated_at="2020-04-17T12:56:57.529Z"),
        create_demarche_simplifiee_application_detail_response_without_venue_siret(siret="12345678912345",
                                                                                   bic="BDFEFR2LCCB",
                                                                                   iban="FR7630006000011234567890189",
                                                                                   idx=2,
                                                                                   updated_at="2020-04-17T12:56:57.529Z")
    ]
    offerer1 = create_offerer(siren='424861714')
    venue_with_siret = create_venue(offerer1, siret='42486171400014')
    bank_information1 = create_bank_information(
        id_at_providers='42486171400014', venue=venue_with_siret, bic="SOGEFRPP", iban="FR7630007000111234567890144")
    offerer2 = create_offerer(siren='123456789')
    venue_without_siret = create_venue(
        offerer2, siret=None, comment='without siret venue', name='VENUE WITHOUT SIRET')
    bank_information2 = create_bank_information(
        id_at_providers='123456789VENUE WITHOUT SIRET', venue=venue_without_siret, bic="SOGEFRPP", iban="FR7630007000111234567890144")
    repository.save(bank_information1, bank_information2)

    activate_provider('VenueBankInformationProvider')
    venue_bank_information_provider = VenueBankInformationProvider()

    # When
    venue_bank_information_provider.updateObjects()

    # Then
    assert BankInformation.query.count() == 2

    updated_bank_information_for_venue_with_siret = BankInformation.query.filter_by(
        idAtProviders='42486171400014').one()
    assert updated_bank_information_for_venue_with_siret.applicationId == 1
    assert updated_bank_information_for_venue_with_siret.iban == "FR7630006000011234567890189"
    assert updated_bank_information_for_venue_with_siret.bic == "BDFEFR2LCCB"
    assert updated_bank_information_for_venue_with_siret.venueId == venue_with_siret.id

    updated_bank_information_for_venue_without_siret = BankInformation.query.filter_by(
        idAtProviders='123456789VENUE WITHOUT SIRET').one()
    assert updated_bank_information_for_venue_without_siret.applicationId == 2
    assert updated_bank_information_for_venue_without_siret.iban == "FR7630006000011234567890189"
    assert updated_bank_information_for_venue_without_siret.bic == "BDFEFR2LCCB"
    assert updated_bank_information_for_venue_without_siret.venueId == venue_without_siret.id


class RetrieveBankInformationTest:
    @clean_database
    def when_rib_affiliation_is_on_siren(self, app):
        # Given
        application_details = demarche_simplifiee_application_detail_response(
            siret="12345678912345",
            bic="BDFEFR2LCCB",
            iban="FR7630006000011234567890189",
            idx=1,
            updated_at="2020-04-17T12:56:57.529Z")
        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer, siret='12345678912345')
        repository.save(venue)
        venue_id = venue.id
        bank_information_provider = TestableVenueBankInformationProvider()

        # When
        bank_information_dict = bank_information_provider.retrieve_bank_information(
            application_details)

        # Then
        assert bank_information_dict['idAtProviders'] == '12345678912345'
        assert bank_information_dict['iban'] == "FR7630006000011234567890189"
        assert bank_information_dict['bic'] == "BDFEFR2LCCB"
        assert bank_information_dict['applicationId'] == 1
        assert bank_information_dict['venueId'] == venue_id
        assert 'offererId' not in bank_information_dict

    @clean_database
    def when_rib_affiliation_is_on_name(self, app):
        # Given
        application_details = create_demarche_simplifiee_application_detail_response_without_venue_siret(
            siret="12345678912345",
            bic="BDFEFR2LCCB",
            iban="FR7630006000011234567890189",
            idx=1,
            updated_at="2020-04-17T12:56:57.529Z",
            venue_name='VENUE WITHOUT SIRET')
        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer, siret=None,
                             name='VENUE WITHOUT SIRET', comment='comment')
        repository.save(venue)
        venue_id = venue.id
        bank_information_provider = TestableVenueBankInformationProvider()

        # When
        bank_information_dict = bank_information_provider.retrieve_bank_information(
            application_details)

        # Then
        assert bank_information_dict['idAtProviders'] == '123456789VENUE WITHOUT SIRET'
        assert bank_information_dict['iban'] == "FR7630006000011234567890189"
        assert bank_information_dict['bic'] == "BDFEFR2LCCB"
        assert bank_information_dict['applicationId'] == 1
        assert bank_information_dict['venueId'] == venue_id
        assert 'offererId' not in bank_information_dict
