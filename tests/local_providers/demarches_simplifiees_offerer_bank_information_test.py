from datetime import datetime
from unittest.mock import patch, ANY

from local_providers import OffererBankInformationProvider
from models import BankInformation, LocalProviderEvent
from models.local_provider_event import LocalProviderEventType
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_bank_information
from tests.model_creators.provider_creators import provider_test


class TestableOffererBankInformationProvider(OffererBankInformationProvider):
    def __init__(self):
        """
        Empty constructor that makes this class testable :
        no API call is made at instantiation time
        """
        pass


class OffererBankInformationProviderProviderTest:
    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_beneficiary_import')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    def test_provider_creates_nothing_if_no_data_retrieved_from_api(self, get_application_details,
                                                                    get_all_application_ids_for_beneficiary_import,
                                                                    app):
        # Given
        get_application_details.return_value = {}
        get_all_application_ids_for_beneficiary_import.return_value = []

        # When Then
        provider_test(app,
                      OffererBankInformationProvider,
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
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_beneficiary_import')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_creates_one_bank_information_with_id_at_providers_siren_if_request_for_siren(self,
                                                                                                   get_application_details,
                                                                                                   get_all_application_ids_for_beneficiary_import,
                                                                                                   app):
        # Given
        get_all_application_ids_for_beneficiary_import.return_value = [1]
        get_application_details.return_value = {
            "dossier": {
                "id": 1,
                "updated_at": "2020-04-15T09:01:12.771Z",
                "state": "closed",
                "entreprise": {
                    "siren": "793875030"
                },
                "champs": [
                    {
                        "value": 'FR7630006000011234567890189',
                        "type_de_champ": {
                            "id": 352722,
                            "libelle": "IBAN",
                            "type_champ": "text",
                            "order_place": 10,
                            "description": ""
                        }
                    },
                    {
                        "value": "BDFEFR2LCCB",
                        "type_de_champ": {
                            "id": 352727,
                            "libelle": "BIC",
                            "type_champ": "text",
                            "order_place": 11,
                            "description": ""
                        }
                    }
                ]
            }
        }

        offerer = create_offerer(siren='793875030')

        repository.save(offerer)

        offerer_id = offerer.id

        # When Then
        provider_test(app,
                      OffererBankInformationProvider,
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
        bank_information = BankInformation.query.first()
        assert bank_information.iban == 'FR7630006000011234567890189'
        assert bank_information.bic == 'BDFEFR2LCCB'
        assert bank_information.applicationId == 1
        assert bank_information.offererId == offerer_id
        assert bank_information.venueId == None
        assert bank_information.idAtProviders == '793875030'
        local_provider_events = LocalProviderEvent.query \
            .order_by(LocalProviderEvent.id) \
            .all()
        assert len(local_provider_events) == 2
        assert local_provider_events[0].type == LocalProviderEventType.SyncStart
        assert local_provider_events[1].type == LocalProviderEventType.SyncEnd

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_beneficiary_import')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_checks_two_objects_and_creates_two_when_both_rib_affiliations_are_known(
            self,
            get_application_details,
            get_all_application_ids_for_beneficiary_import,
            app):
        # Given
        get_all_application_ids_for_beneficiary_import.return_value = [1, 2]
        get_application_details.side_effect = [
            {
                "dossier":
                    {
                        "id": 1,
                        "updated_at": "2019-01-21T18:55:03.387Z",
                        "state": "closed",
                        "entreprise":
                            {
                                "siren": "793875019",
                                "siret_siege_social": "79387501900089"
                            },
                        "champs":
                            [
                                {
                                    "value": "BDFEFR2LCCB",
                                    "type_de_champ":
                                        {
                                            "id": 352727,
                                            "libelle": "BIC",
                                            "type_champ": "text",
                                            "order_place": 8,
                                            "description": ""
                                        }
                                },
                                {
                                    "value": "FR7630006000011234567890189",
                                    "type_de_champ":
                                        {
                                            "id": 352722,
                                            "libelle": "IBAN",
                                            "type_champ": "text",
                                            "order_place": 9,
                                            "description": ""
                                        }
                                }
                            ]
                    }
            },
            {
                "dossier":
                    {
                        "id": 2,
                        "updated_at": "2019-01-21T18:55:04.387Z",
                        "state": "closed",
                        "entreprise":
                            {
                                "siren": "793875030",
                            },
                        "champs":
                            [
                                {
                                    "value": "SOGEFRPP",
                                    "type_de_champ":
                                        {
                                            "id": 352727,
                                            "libelle": "BIC",
                                            "type_champ": "text",
                                            "order_place": 8,
                                            "description": ""
                                        }
                                },
                                {
                                    "value": "FR7630007000111234567890144",
                                    "type_de_champ":
                                        {
                                            "id": 352722,
                                            "libelle": "IBAN",
                                            "type_champ": "text",
                                            "order_place": 9,
                                            "description": ""
                                        }
                                },
                            ]
                    }
            }

        ]
        offerer1 = create_offerer(siren='793875019')
        offerer2 = create_offerer(siren='793875030')

        repository.save(offerer1, offerer2)

        # When Then
        provider_test(app,
                      OffererBankInformationProvider,
                      None,
                      checkedObjects=2,
                      createdObjects=2,
                      updatedObjects=0,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      BankInformation=2)
        bank_information1 = BankInformation.query.filter_by(
            applicationId=1).first()
        bank_information2 = BankInformation.query.filter_by(
            applicationId=2).first()
        assert bank_information1.iban == 'FR7630006000011234567890189'
        assert bank_information1.bic == 'BDFEFR2LCCB'
        assert bank_information1.applicationId == 1
        assert bank_information1.offererId == offerer1.id
        assert bank_information1.venueId == None
        assert bank_information1.idAtProviders == '793875019'
        assert bank_information2.iban == 'FR7630007000111234567890144'
        assert bank_information2.bic == 'SOGEFRPP'
        assert bank_information2.applicationId == 2
        assert bank_information2.offererId == offerer2.id
        assert bank_information2.venueId == None
        assert bank_information2.idAtProviders == '793875030'

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_beneficiary_import')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_does_not_create_bank_information_if_siren_unknown(
            self,
            get_application_details,
            get_all_application_ids_for_beneficiary_import,
            app):
        # Given
        get_all_application_ids_for_beneficiary_import.return_value = [1]
        get_application_details.side_effect = [
            {
                "dossier":
                    {
                        "id": 1,
                        "updated_at": "2019-01-21T18:55:03.387Z",
                        "state": "closed",
                        "entreprise":
                            {
                                "siren": "793875019",
                            },
                        "champs":
                            [
                                {
                                    "value": "BDFEFR2LCCB",
                                    "type_de_champ":
                                        {
                                            "id": 352727,
                                            "libelle": "BIC",
                                            "type_champ": "text",
                                            "order_place": 8,
                                            "description": ""
                                        }
                                },
                                {
                                    "value": "FR7630006000011234567890189",
                                    "type_de_champ":
                                        {
                                            "id": 352722,
                                            "libelle": "IBAN",
                                            "type_champ": "text",
                                            "order_place": 9,
                                            "description": ""
                                        }
                                }
                            ]
                    }
            }
        ]

        # When Then
        provider_test(app,
                      OffererBankInformationProvider,
                      None,
                      checkedObjects=1,
                      createdObjects=0,
                      updatedObjects=0,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0,
                      BankInformation=0)

        sync_error = LocalProviderEvent.query.filter_by(
            type=LocalProviderEventType.SyncError).first()
        assert sync_error.payload == 'unknown siren for application id 1'
        assert len(LocalProviderEvent.query.all()) == 3

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_beneficiary_import')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_updates_existing_bank_information(
            self,
            get_application_details,
            get_all_application_ids_for_beneficiary_import,
            app):
        # Given
        get_all_application_ids_for_beneficiary_import.return_value = [1]
        get_application_details.side_effect = [
            {
                "dossier":
                    {
                        "id": 2,
                        "updated_at": "2019-01-21T18:55:03.387Z",
                        "state": "closed",
                        "entreprise":
                            {
                                "siren": "793875019",
                            },
                        "champs":
                            [
                                {
                                    "value": "BDFEFR2LCCB",
                                    "type_de_champ":
                                        {
                                            "id": 352727,
                                            "libelle": "BIC",
                                            "type_champ": "text",
                                            "order_place": 8,
                                            "description": ""
                                        }
                                },
                                {
                                    "value": "FR7630006000011234567890189",
                                    "type_de_champ":
                                        {
                                            "id": 352722,
                                            "libelle": "IBAN",
                                            "type_champ": "text",
                                            "order_place": 9,
                                            "description": ""
                                        }
                                }
                            ]
                    }
            }
        ]

        offerer = create_offerer(siren='793875019')

        bank_information = create_bank_information(
            id_at_providers="793875019", offerer=offerer)
        repository.save(bank_information)

        # When Then
        provider_test(app,
                      OffererBankInformationProvider,
                      None,
                      checkedObjects=1,
                      createdObjects=0,
                      updatedObjects=1,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0)

        updated_bank_information = BankInformation.query.filter_by(
            idAtProviders="793875019").one()
        assert updated_bank_information.applicationId == 2
        assert updated_bank_information.iban == "FR7630006000011234567890189"
        assert updated_bank_information.bic == "BDFEFR2LCCB"

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_beneficiary_import')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_does_not_save_bank_information_if_wrong_bic_or_iban_but_continues_flow(
            self,
            get_application_details,
            get_all_application_ids_for_beneficiary_import,
            app):
        # given
        get_all_application_ids_for_beneficiary_import.return_value = [1, 2]
        get_application_details.side_effect = [
            {
                "dossier":
                    {
                        "id": 1,
                        "updated_at": "2019-01-20T18:55:03.387Z",
                        "state": "closed",
                        "entreprise":
                            {
                                "siren": "793875019",
                            },
                        "champs":
                            [
                                {
                                    "value": "wrongbic",
                                    "type_de_champ":
                                        {
                                            "id": 352727,
                                            "libelle": "BIC",
                                            "type_champ": "text",
                                            "order_place": 8,
                                            "description": ""
                                        }
                                },
                                {
                                    "value": "wrongsiren",
                                    "type_de_champ":
                                        {
                                            "id": 352722,
                                            "libelle": "IBAN",
                                            "type_champ": "text",
                                            "order_place": 9,
                                            "description": ""
                                        }
                                }
                            ]
                    }
            },
            {
                "dossier":
                    {
                        "id": 2,
                        "updated_at": "2019-01-21T18:55:04.387Z",
                        "state": "closed",
                        "entreprise":
                            {
                                "siren": "793875030",
                            },
                        "champs":
                            [
                                {
                                    "value": "SOGEFRPP",
                                    "type_de_champ":
                                        {
                                            "id": 352727,
                                            "libelle": "BIC",
                                            "type_champ": "text",
                                            "order_place": 8,
                                            "description": ""
                                        }
                                },
                                {
                                    "value": "FR7630007000111234567890144",
                                    "type_de_champ":
                                        {
                                            "id": 352722,
                                            "libelle": "IBAN",
                                            "type_champ": "text",
                                            "order_place": 9,
                                            "description": ""
                                        }
                                },
                            ]
                    }
            }
        ]

        offerer_ko = create_offerer(siren='793875019')
        offerer_ok = create_offerer(siren="793875030")

        repository.save(offerer_ko, offerer_ok)

        bank_information_provider = OffererBankInformationProvider()
        bank_information_provider.provider.isActive = True
        repository.save(bank_information_provider.provider)

        # when
        bank_information_provider.updateObjects()

        # then
        bank_information = BankInformation.query.all()
        assert len(bank_information) == 1
        assert bank_information[0].applicationId == 2
        local_provider_event = LocalProviderEvent.query.filter_by(
            type=LocalProviderEventType.SyncError).one()
        assert local_provider_event.payload == 'ApiErrors'

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_beneficiary_import')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_calls_get_all_application_ids_with_1900_01_01_when_table_bank_information_is_empty(
            self,
            get_application_details,
            get_all_application_ids_for_beneficiary_import,
            app):
        # given
        get_all_application_ids_for_beneficiary_import.return_value = [1]
        get_application_details.return_value = {
            "dossier":
                {
                    "id": 2,
                    "updated_at": "2019-01-21T18:55:03.387Z",
                    "state": "closed",
                    "entreprise":
                        {
                            "siren": "793875019",
                        },
                    "champs":
                        [
                            {
                                "value": "BDFEFR2LCCB",
                                "type_de_champ":
                                    {
                                        "id": 352727,
                                        "libelle": "BIC",
                                        "type_champ": "text",
                                        "order_place": 8,
                                        "description": ""
                                    }
                            },
                            {
                                "value": "FR7630006000011234567890189",
                                "type_de_champ":
                                    {
                                        "id": 352722,
                                        "libelle": "IBAN",
                                        "type_champ": "text",
                                        "order_place": 9,
                                        "description": ""
                                    }
                            }
                        ]
                }
        }

        bank_information_provider = OffererBankInformationProvider()
        bank_information_provider.provider.isActive = True
        repository.save(bank_information_provider.provider)

        # when
        bank_information_provider.updateObjects()

        # then
        get_all_application_ids_for_beneficiary_import.assert_called_with(ANY, ANY,
                                                                          datetime(1900, 1, 1))

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_beneficiary_import')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_calls_get_all_application_ids_with_last_update_from_table_bank_information(
            self,
            get_application_details,
            get_all_application_ids_for_beneficiary_import,
            app):
        # given
        get_all_application_ids_for_beneficiary_import.return_value = [1]
        get_application_details.return_value = {
            "dossier":
                {
                    "id": 2,
                    "updated_at": "2019-01-21T18:55:03.387Z",
                    "state": "closed",
                    "entreprise":
                        {
                            "siren": "793875019",
                        },
                    "champs":
                        [
                            {
                                "value": "BDFEFR2LCCB",
                                "type_de_champ":
                                    {
                                        "id": 352727,
                                        "libelle": "BIC",
                                        "type_champ": "text",
                                        "order_place": 8,
                                        "description": ""
                                    }
                            },
                            {
                                "value": "FR7630006000011234567890189",
                                "type_de_champ":
                                    {
                                        "id": 352722,
                                        "libelle": "IBAN",
                                        "type_champ": "text",
                                        "order_place": 9,
                                        "description": ""
                                    }
                            }
                        ]
                }
        }

        offerer = create_offerer(siren='793875019')

        bank_information = create_bank_information(id_at_providers='79387501900056',
                                                   date_modified_at_last_provider=datetime(2019, 1, 1), offerer=offerer)
        repository.save(bank_information)

        bank_information_provider = OffererBankInformationProvider()
        bank_information_provider.provider.isActive = True
        repository.save(bank_information_provider.provider)

        # when
        bank_information_provider.updateObjects()

        # then
        get_all_application_ids_for_beneficiary_import.assert_called_with(ANY, ANY,
                                                                          datetime(2019, 1, 1))

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_beneficiary_import')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_creates_one_bank_information_and_format_IBAN_and_BIC(self,
                                                                           get_application_details,
                                                                           get_all_application_ids_for_beneficiary_import,
                                                                           app):
        # Given
        get_all_application_ids_for_beneficiary_import.return_value = [1]
        get_application_details.return_value = {
            "dossier":
                {
                    "id": 1,
                    "updated_at": "2019-01-21T18:55:03.387Z",
                    "state": "closed",
                    "entreprise":
                        {
                            "siren": "793875030",
                        },
                    "champs":
                        [
                            {
                                "value": "BdFefr2LCCB",
                                "type_de_champ":
                                    {
                                        "id": 352727,
                                        "libelle": "BIC",
                                        "type_champ": "text",
                                        "order_place": 8,
                                        "description": ""
                                    }
                            },
                            {
                                "value": "FR76 3000 6000  0112 3456 7890 189",
                                "type_de_champ":
                                    {
                                        "id": 352722,
                                        "libelle": "IBAN",
                                        "type_champ": "text",
                                        "order_place": 9,
                                        "description": ""
                                    }
                            },
                        ]
                }
        }
        offerer = create_offerer(siren='793875030')

        repository.save(offerer)

        # When Then
        provider_test(app,
                      OffererBankInformationProvider,
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
        bank_information = BankInformation.query.first()
        assert bank_information.iban == 'FR7630006000011234567890189'
        assert bank_information.bic == 'BDFEFR2LCCB'


class RetrieveBankInformationTest:
    @clean_database
    def when_rib_affiliation_is_on_siren(self, app):
        # Given
        application_details = {
            "dossier":
                {
                    "id": 1,
                    "updated_at": "2019-01-21T18:55:03.387Z",
                    "entreprise":
                        {
                            "siren": "793875019",
                        },
                    "champs":
                        [
                            {
                                "value": "BDFEFR2LCCB",
                                "type_de_champ":
                                    {
                                        "libelle": "BIC",
                                    }
                            },
                            {
                                "value": "FR7630006000011234567890189",
                                "type_de_champ":
                                    {
                                        "libelle": "IBAN",
                                    }
                            }
                        ]
                }
        }
        offerer = create_offerer(siren="793875019")
        repository.save(offerer)
        offerer_id = offerer.id
        bank_information_provider = TestableOffererBankInformationProvider()

        # When
        bank_information_dict = bank_information_provider.retrieve_bank_information(
            application_details)

        # Then
        assert bank_information_dict['iban'] == "FR7630006000011234567890189"
        assert bank_information_dict['bic'] == "BDFEFR2LCCB"
        assert bank_information_dict['applicationId'] == 1
        assert bank_information_dict['offererId'] == offerer_id
        assert 'venueId' not in bank_information_dict
