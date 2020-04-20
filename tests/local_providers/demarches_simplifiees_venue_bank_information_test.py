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
from tests.model_creators.provider_creators import provider_test
from utils.date import DATE_ISO_FORMAT


class TestableVenueBankInformationProvider(VenueBankInformationProvider):
    def __init__(self):
        """
        Empty constructor that makes this class testable :
        no API call is made at instantiation time
        """
        pass


def demarche_simplifiee_application_detail_response(siret, bic, iban, id=1, updated_at="2019-01-21T18:55:03.387Z"):
    return {
        "dossier": {
            "id": id,
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
                    "value": siret,
                    "type_de_champ": {
                        "id": 782800,
                        "libelle": "Si vous souhaitez renseigner les coordonn\\u00e9es bancaires d\'un lieu avec SIRET, merci de saisir son SIRET : ",
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


def activate_provider():
    provider_object = VenueBankInformationProvider()
    provider_object.provider.isActive = True
    repository.save(provider_object.provider)
    provider_object.updateObjects()


class VenueBankInformationProviderProviderTest:
    @patch(
        'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
    def test_provider_creates_nothing_if_no_data_retrieved_from_api(self, get_application_details,
                                                                    get_all_application_ids_for_demarche_simplifiee,
                                                                    app):
        # Given
        get_application_details.return_value = {}
        get_all_application_ids_for_demarche_simplifiee.return_value = []

        # When Then
        provider_test(app,
                      VenueBankInformationProvider,
                      None,
                      checkedObjects=0,
                      createdObjects=0,
                      updatedObjects=0,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      BankInformation=0)

    @patch(
        'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
    @clean_database
    def test_provider_creates_one_bank_information_with_id_at_providers_siret(self,
                                                                              get_application_details,
                                                                              get_all_application_ids_for_demarche_simplifiee,
                                                                              app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1]
        get_application_details.return_value = demarche_simplifiee_application_detail_response(siret="42486171400014",
                                                                                               bic="BDFEFR2LCCB",
                                                                                               iban="FR7630006000011234567890189",
                                                                                               id=1,
                                                                                               updated_at="2019-01-21T18:55:03.387Z")
        offerer = create_offerer(siren='424861714')
        venue = create_venue(offerer, siret='42486171400014')
        repository.save(venue)
        venue_id = venue.id


        # When
        activate_provider()

        # Then
        bank_information = BankInformation.query.one()
        assert bank_information.iban == 'FR7630006000011234567890189'
        assert bank_information.bic == 'BDFEFR2LCCB'
        assert bank_information.applicationId == 1
        assert bank_information.offererId == None
        assert bank_information.venueId == venue_id
        assert bank_information.idAtProviders == '42486171400014'
        local_provider_events = LocalProviderEvent.query \
            .order_by(LocalProviderEvent.id) \
            .all()
        assert len(local_provider_events) == 2
        assert local_provider_events[0].type == LocalProviderEventType.SyncStart
        assert local_provider_events[1].type == LocalProviderEventType.SyncEnd

    @patch(
        'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
    @clean_database
    def test_provider_checks_two_objects_and_creates_two_when_both_rib_affiliations_are_known(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1, 2]
        get_application_details.side_effect = [
            demarche_simplifiee_application_detail_response(siret="42486171400014",
                                                            bic="BDFEFR2LCCB",
                                                            iban="FR7630006000011234567890189",
                                                            id=1,
                                                            updated_at="2020-04-17T12:56:57.529Z"),
            demarche_simplifiee_application_detail_response(siret="12345678912345",
                                                            bic="BDFEFR2LCCB",
                                                            iban="FR7630006000011234567890189",
                                                            id=2,
                                                            updated_at="2020-04-17T12:56:57.529Z")
        ]
        offerer1 = create_offerer(siren='424861714')
        venue1 = create_venue(offerer1, siret='42486171400014')
        offerer2 = create_offerer(siren='123456789')
        venue2 = create_venue(offerer2, siret='12345678912345')
        repository.save(venue1, venue2)
        venue_id1 = venue1.id
        venue_id2 = venue2.id

        # When
        activate_provider()

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
            id=1,
            updated_at="2020-04-17T12:56:57.529Z")

        # When
        activate_provider()

        # Then
        assert BankInformation.query.count() == 0
        sync_error = LocalProviderEvent.query.filter_by(
            type=LocalProviderEventType.SyncError).first()
        assert sync_error.payload == 'unknown siret for application id 1'
        assert len(LocalProviderEvent.query.all()) == 3

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
            id=2,
            updated_at="2020-04-17T12:56:57.529Z")
        offerer = create_offerer(siren='424861714')
        venue = create_venue(offerer, siret='42486171400014')
        bank_information = create_bank_information(
            id_at_providers="42486171400014", venue=venue)
        repository.save(bank_information)

        # When
        activate_provider()

        # Then
        updated_bank_information = BankInformation.query.one()
        assert updated_bank_information.applicationId == 2
        assert updated_bank_information.iban == "FR7630006000011234567890189"
        assert updated_bank_information.bic == "BDFEFR2LCCB"

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
                                                            id=1,
                                                            updated_at="2020-04-17T12:56:57.529Z"),
            demarche_simplifiee_application_detail_response(siret="12345678912345",
                                                            bic="BDFEFR2LCCB",
                                                            iban="FR7630006000011234567890189",
                                                            id=2,
                                                            updated_at="2020-04-17T12:56:57.529Z")
        ]
        offerer_ko = create_offerer(siren='424861714')
        venue_ko = create_venue(offerer_ko, siret='42486171400014')
        offerer_ok = create_offerer(siren="123456789")
        venue_ok = create_venue(offerer_ok, siret='12345678912345')

        repository.save(venue_ko, venue_ok)

        # When
        activate_provider()

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
            id=1,
            updated_at="2020-04-17T12:56:57.529Z")
        bank_information_provider = VenueBankInformationProvider()
        bank_information_provider.provider.isActive = True
        repository.save(bank_information_provider.provider)

        # when
        bank_information_provider.updateObjects()

        # then
        get_all_application_ids_for_demarche_simplifiee.assert_called_with(ANY, ANY,
                                                                           datetime(1900, 1, 1))

    @patch(
        'local_providers.demarches_simplifiees_venue_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_venue_bank_information.get_application_details')
    @clean_database
    def test_calls_get_all_application_ids_with_last_update_from_table_bank_information(
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
            id=2,
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

        # When
        activate_provider()

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
            bic="BDFEFR2LCCB",
            iban="FR7630006000011234567890189",
            id=2,
            updated_at="2020-04-17T12:56:57.529Z")

        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer, siret='12345678912345')

        repository.save(venue)

        # When
        activate_provider()

        # Then
        bank_information = BankInformation.query.one()
        assert bank_information.iban == 'FR7630006000011234567890189'
        assert bank_information.bic == 'BDFEFR2LCCB'


class RetrieveBankInformationTest:
    @clean_database
    def when_rib_affiliation_is_on_siren(self, app):
        # Given
        application_details = demarche_simplifiee_application_detail_response(
            siret="12345678912345",
            bic="BDFEFR2LCCB",
            iban="FR7630006000011234567890189",
            id=1,
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
        assert bank_information_dict['iban'] == "FR7630006000011234567890189"
        assert bank_information_dict['bic'] == "BDFEFR2LCCB"
        assert bank_information_dict['applicationId'] == 1
        assert bank_information_dict['venueId'] == venue_id
        assert 'offererId' not in bank_information_dict
