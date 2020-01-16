import os
from datetime import datetime
from unittest.mock import patch, call

from local_providers.demarches_simplifiees_bank_information_without_siret import \
    VenueWithoutSIRETBankInformationProvider, DemarchesSimplifieesMapper
from models import BankInformation, LocalProviderEvent
from models.local_provider_event import LocalProviderEventType
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_bank_information
from tests.model_creators.provider_creators import provider_test, activate_provider
from utils.human_ids import dehumanize, humanize


def _create_detail_response(application_id=145, offerer_id=267, venue_id=578, bic="TRPUFRP1",
                            iban="FR7610271490201000200481837"):
    return {
        "dossier": {
            "id": application_id,
            "created_at": "2019-04-25T15:20:06.532Z",
            "updated_at": "2019-04-25T15:23:36.490Z",
            "state": "closed",
            "simplified_state": "Validé",
            "initiated_at": "2019-04-25T15:23:35.255Z",
            "instructeurs": [],
            "individual": {
                "civilite": "M.",
                "nom": "PORT MUSEE",
                "prenom": " \tCOMMUNE DE DOUARNENEZ"
            },
            "champs": [
                {
                    "value": "https://pro.passculture.beta.gouv.fr/"
                             "structures/" + humanize(offerer_id) + "/"
                                                                    "lieux/" + humanize(venue_id),
                    "type_de_champ": {
                        "id": 407889,
                        "libelle": "URL",
                        "type_champ": "text",
                        "order_place": 1,
                        "description": ""
                    }
                },
                {
                    "value": bic,
                    "type_de_champ": {
                        "id": 352727,
                        "libelle": "BIC",
                        "type_champ": "text",
                        "order_place": 9,
                        "description": ""
                    }
                },
                {
                    "value": iban,
                    "type_de_champ": {
                        "id": 352722,
                        "libelle": "IBAN",
                        "type_champ": "text",
                        "order_place": 10,
                        "description": ""
                    }
                }
            ]
        }
    }


class VenueWithoutSIRETBankInformationProviderTest:

    def setup(self):
        self.VENUE_ID = 256351
        self.OFFERER_ID = 49153
        self.APPLICATION_ID = 145

    @patch(
        'local_providers.demarches_simplifiees_bank_information_without_siret.get_all_application_ids_for_procedure')
    @patch(
        'local_providers.demarches_simplifiees_bank_information_without_siret.find_latest_sync_end_event')
    def test_collect_updated_applications_ids_to_handle_using_environment_vars(self,
                                                                               find_latest_sync_end_event,
                                                                               get_all_application_ids_for_procedure,
                                                                               app):
        # Given
        last_provider_sync = LocalProviderEvent()
        last_provider_sync.date = datetime(2020, 1, 2)
        find_latest_sync_end_event.return_value = last_provider_sync
        get_all_application_ids_for_procedure.return_value = []
        PROCEDURE_ID_VENUE_WITHOUT_SIRET = '5636727'
        TOKEN = '4872'

        # When
        with patch.dict(os.environ, {
            'DEMARCHES_SIMPLIFIEES_VENUE_WITHOUT_SIRET_PROCEDURE_ID': PROCEDURE_ID_VENUE_WITHOUT_SIRET,
            'DEMARCHES_SIMPLIFIEES_TOKEN': TOKEN
        }, clear=True):
            VenueWithoutSIRETBankInformationProvider()

        # Then
        get_all_application_ids_for_procedure.assert_called_with(
            PROCEDURE_ID_VENUE_WITHOUT_SIRET, TOKEN, datetime(2020, 1, 2)
        )

    @patch(
        'local_providers.demarches_simplifiees_bank_information_without_siret.get_all_application_ids_for_procedure')
    @patch(
        'local_providers.demarches_simplifiees_bank_information_without_siret.find_latest_sync_end_event')
    def test_when_applications_never_treated_then_collect_applications_ids_from_1970(self,
                                                                                     find_latest_sync_end_event,
                                                                                     get_all_application_ids_for_procedure,
                                                                                     app):
        # Given
        find_latest_sync_end_event.return_value = None
        get_all_application_ids_for_procedure.return_value = []
        PROCEDURE_ID_VENUE_WITHOUT_SIRET = '5636727'
        TOKEN = '4872'

        # When
        with patch.dict(os.environ, {
            'DEMARCHES_SIMPLIFIEES_VENUE_WITHOUT_SIRET_PROCEDURE_ID': PROCEDURE_ID_VENUE_WITHOUT_SIRET,
            'DEMARCHES_SIMPLIFIEES_TOKEN': TOKEN
        }, clear=True):
            VenueWithoutSIRETBankInformationProvider()

        # Then
        get_all_application_ids_for_procedure.assert_called_with(
            PROCEDURE_ID_VENUE_WITHOUT_SIRET, TOKEN, datetime(1970, 1, 1)
        )

    @patch(
        'local_providers.demarches_simplifiees_bank_information_without_siret.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information_without_siret.get_application_details')
    @patch('local_providers.demarches_simplifiees_bank_information_without_siret.find_latest_sync_end_event')
    @clean_database
    def test_collect_application_details_for_each_application(self,
                                                              find_latest_sync_end_event,
                                                              get_application_details,
                                                              get_all_application_ids_for_procedure,
                                                              app):
        # Given
        APPLICATION_ID_2 = 2

        last_provider_sync = LocalProviderEvent()
        last_provider_sync.date = datetime(2020, 1, 2)
        find_latest_sync_end_event.return_value = last_provider_sync
        get_all_application_ids_for_procedure.return_value = [
            self.APPLICATION_ID,
            APPLICATION_ID_2
        ]
        get_application_details.return_value = _create_detail_response(self.APPLICATION_ID,
                                                                       self.OFFERER_ID,
                                                                       self.VENUE_ID)

        PROCEDURE_ID_VENUE_WITHOUT_SIRET = '5636727'
        TOKEN = '4872'
        offerer = create_offerer(siren='793875030', idx=self.OFFERER_ID)
        venue = create_venue(offerer=offerer, idx=self.VENUE_ID)
        Repository.save(venue)

        # When
        with patch.dict(os.environ, {
            'DEMARCHES_SIMPLIFIEES_VENUE_WITHOUT_SIRET_PROCEDURE_ID': PROCEDURE_ID_VENUE_WITHOUT_SIRET,
            'DEMARCHES_SIMPLIFIEES_TOKEN': TOKEN
        }, clear=True):
            provider_test(app,
                          VenueWithoutSIRETBankInformationProvider,
                          None,
                          checkedObjects=0,
                          createdObjects=0,
                          updatedObjects=0,
                          erroredObjects=2,
                          checkedThumbs=0,
                          createdThumbs=0,
                          updatedThumbs=0,
                          erroredThumbs=0,
                          BankInformation=0)

        # Then
        assert get_application_details.call_count == 2
        assert get_application_details.call_args_list == [
            call(self.APPLICATION_ID, PROCEDURE_ID_VENUE_WITHOUT_SIRET, TOKEN),
            call(APPLICATION_ID_2, PROCEDURE_ID_VENUE_WITHOUT_SIRET, TOKEN)
        ]

    @patch('os.environ', return_value={
        'DEMARCHES_SIMPLIFIEES_VENUE_WITHOUT_SIRET_PROCEDURE_ID': '5636727',
        'DEMARCHES_SIMPLIFIEES_TOKEN': '4872'
    }, clear=True)
    @patch(
        'local_providers.demarches_simplifiees_bank_information_without_siret.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information_without_siret.get_application_details')
    @patch('local_providers.demarches_simplifiees_bank_information_without_siret.find_latest_sync_end_event')
    @clean_database
    def test_do_not_create_bank_information_when_offerer_does_not_exist(self,
                                                                        find_latest_sync_end_event,
                                                                        get_application_details,
                                                                        get_all_application_ids_for_procedure,
                                                                        environment,
                                                                        app):
        # Given
        last_provider_sync = LocalProviderEvent()
        last_provider_sync.date = datetime(2020, 1, 2)
        find_latest_sync_end_event.return_value = last_provider_sync
        get_all_application_ids_for_procedure.return_value = [self.APPLICATION_ID]
        get_application_details.return_value = _create_detail_response(self.APPLICATION_ID, self.OFFERER_ID,
                                                                       self.VENUE_ID)
        activate_provider('VenueWithoutSIRETBankInformationProvider')
        venue_without_siret_bank_information_provider = VenueWithoutSIRETBankInformationProvider()

        # When
        venue_without_siret_bank_information_provider.updateObjects()

        # Then
        local_provider_event = LocalProviderEvent.query \
            .filter(LocalProviderEvent.type == LocalProviderEventType.SyncError) \
            .one()
        assert local_provider_event.payload == f"unknown offerer for id {self.OFFERER_ID}"

    @patch('os.environ', return_value={
        'DEMARCHES_SIMPLIFIEES_VENUE_WITHOUT_SIRET_PROCEDURE_ID': '5636727',
        'DEMARCHES_SIMPLIFIEES_TOKEN': '4872'
    }, clear=True)
    @patch(
        'local_providers.demarches_simplifiees_bank_information_without_siret.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information_without_siret.get_application_details')
    @patch('local_providers.demarches_simplifiees_bank_information_without_siret.find_latest_sync_end_event')
    @clean_database
    def test_do_not_create_bank_information_when_venue_does_not_exist(self,
                                                                      find_latest_sync_end_event,
                                                                      get_application_details,
                                                                      get_all_application_ids_for_procedure,
                                                                      environment,
                                                                      app):
        # Given
        last_provider_sync = LocalProviderEvent()
        last_provider_sync.date = datetime(2020, 1, 2)
        find_latest_sync_end_event.return_value = last_provider_sync
        offerer = create_offerer(siren='793875030', idx=49153)
        Repository.save(offerer)

        get_all_application_ids_for_procedure.return_value = [self.APPLICATION_ID]
        get_application_details.return_value = _create_detail_response(self.APPLICATION_ID, self.OFFERER_ID,
                                                                       self.VENUE_ID)

        activate_provider('VenueWithoutSIRETBankInformationProvider')
        venue_without_siret_bank_information_provider = VenueWithoutSIRETBankInformationProvider()

        # When
        venue_without_siret_bank_information_provider.updateObjects()

        # Then
        local_provider_event = LocalProviderEvent.query \
            .filter(LocalProviderEvent.type == LocalProviderEventType.SyncError) \
            .one()
        assert local_provider_event.payload == f"unknown venue for id {self.VENUE_ID}"

    @patch('os.environ', return_value={
        'DEMARCHES_SIMPLIFIEES_VENUE_WITHOUT_SIRET_PROCEDURE_ID': '5636727',
        'DEMARCHES_SIMPLIFIEES_TOKEN': '4872'
    })
    @patch(
        'local_providers.demarches_simplifiees_bank_information_without_siret.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information_without_siret.get_application_details')
    @patch('local_providers.demarches_simplifiees_bank_information_without_siret.find_latest_sync_end_event')
    @clean_database
    def test_create_bank_information_when_the_bank_information_does_not_exist(self,
                                                                              find_latest_sync_end_event,
                                                                              get_application_details,
                                                                              get_all_application_ids_for_procedure,
                                                                              environment,
                                                                              app):
        # Given
        IBAN = 'FR7630006000011234567890189'
        BIC = 'BDFEFR2LCCB'
        offerer = create_offerer(siren='793875030', idx=self.OFFERER_ID)
        venue = create_venue(offerer=offerer, idx=self.VENUE_ID)
        Repository.save(venue)
        last_provider_sync = LocalProviderEvent()
        last_provider_sync.date = datetime(2020, 1, 2)
        find_latest_sync_end_event.return_value = last_provider_sync
        get_all_application_ids_for_procedure.return_value = [self.APPLICATION_ID]
        get_application_details.return_value = _create_detail_response(
            self.APPLICATION_ID, self.OFFERER_ID, self.VENUE_ID, iban=IBAN, bic=BIC
        )

        # When
        provider_test(app,
                      VenueWithoutSIRETBankInformationProvider,
                      None,
                      checkedObjects=1,
                      createdObjects=1,
                      updatedObjects=0,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      BankInformation=1)

        # Then
        bank_information = BankInformation.query.first()
        assert bank_information.iban == IBAN
        assert bank_information.bic == BIC
        assert bank_information.venueId == self.VENUE_ID

    @patch('os.environ', return_value={
        'DEMARCHES_SIMPLIFIEES_VENUE_WITHOUT_SIRET_PROCEDURE_ID': '5636727',
        'DEMARCHES_SIMPLIFIEES_TOKEN': '4872'
    })
    @patch(
        'local_providers.demarches_simplifiees_bank_information_without_siret.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information_without_siret.get_application_details')
    @patch('local_providers.demarches_simplifiees_bank_information_without_siret.find_latest_sync_end_event')
    @clean_database
    def test_updates_bank_information_when_existing_bank_information_with_same_id_at_provider(self,
                                                                                              find_latest_sync_end_event,
                                                                                              get_application_details,
                                                                                              get_all_application_ids_for_procedure,
                                                                                              environment,
                                                                                              app):
        # Given
        offerer = create_offerer(siren='793875030', idx=self.OFFERER_ID)
        venue = create_venue(offerer=offerer, idx=self.VENUE_ID)
        bank_information = create_bank_information(
            application_id=self.APPLICATION_ID,
            bic='PSSTFRPPLIL',
            iban="FR1420041010050500013M02606",
            offerer=offerer,
            venue=venue,
            id_at_providers=f"{self.OFFERER_ID}%{self.VENUE_ID}"
        )
        Repository.save(venue, bank_information)
        last_provider_sync = LocalProviderEvent()
        last_provider_sync.date = datetime(2020, 1, 2)
        find_latest_sync_end_event.return_value = last_provider_sync
        get_all_application_ids_for_procedure.return_value = [self.APPLICATION_ID]
        NEW_IBAN = 'FR7630006000011234567890189'
        NEW_BIC = 'AGRIFRPP'
        get_application_details.return_value = _create_detail_response(
            self.APPLICATION_ID, self.OFFERER_ID, self.VENUE_ID, iban=NEW_IBAN, bic=NEW_BIC
        )

        # When
        provider_test(app,
                      VenueWithoutSIRETBankInformationProvider,
                      None,
                      checkedObjects=1,
                      createdObjects=0,
                      updatedObjects=1,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0)

        # Then
        bank_information = BankInformation.query.all()
        assert len(bank_information) == 1

        bank_information = BankInformation.query.first()
        assert bank_information.iban == NEW_IBAN
        assert bank_information.bic == NEW_BIC
        assert bank_information.offererId == self.OFFERER_ID
        assert bank_information.venueId == self.VENUE_ID


class DemarchesSimplifieesMapperTest:
    class fromVenueWithoutSIRETApplicationTest:
        def test_returns_dict_with_application_details(self):
            # Given
            simplified_response = {
                "dossier": {
                    "id": 451574,
                    "created_at": "2019-04-25T15:20:06.532Z",
                    "updated_at": "2019-04-25T15:23:36.490Z",
                    "state": "closed",
                    "simplified_state": "Validé",
                    "initiated_at": "2019-04-25T15:23:35.255Z",
                    "instructeurs": [],
                    "individual": {
                        "civilite": "M.",
                        "nom": "PORT MUSEE",
                        "prenom": " \tCOMMUNE DE DOUARNENEZ"
                    },
                    "champs": [
                        {
                            "value": "https://pro.passculture.beta.gouv.fr/structures/YAAT/lieux/DBMQ",
                            "type_de_champ": {
                                "id": 407889,
                                "libelle": "URL",
                                "type_champ": "text",
                                "order_place": 1,
                                "description": ""
                            }
                        },
                        {
                            "value": '',
                            "type_de_champ": {
                                "id": 352724,
                                "libelle": "Information bancaires",
                                "type_champ": "header_section",
                                "order_place": 8,
                                "description": ""
                            }
                        },
                        {
                            "value": "TRPUFRP1",
                            "type_de_champ": {
                                "id": 352727,
                                "libelle": "BIC",
                                "type_champ": "text",
                                "order_place": 9,
                                "description": ""
                            }
                        },
                        {
                            "value": "FR7610271490201000200481837",
                            "type_de_champ": {
                                "id": 352722,
                                "libelle": "IBAN",
                                "type_champ": "text",
                                "order_place": 10,
                                "description": ""
                            }
                        }
                    ]
                }
            }

            # When
            extracted_dict = DemarchesSimplifieesMapper.from_venue_without_SIRET_application(simplified_response)

            # Then
            assert extracted_dict['BIC'] == 'TRPUFRP1'
            assert extracted_dict['IBAN'] == 'FR7610271490201000200481837'
            assert extracted_dict['applicationId'] == 451574
            assert extracted_dict['structureId'] == dehumanize('YAAT')
            assert extracted_dict['venueId'] == dehumanize('DBMQ')
            assert extracted_dict['updated_at'] == datetime(2019, 4, 25, 15, 23, 36, 490000)
