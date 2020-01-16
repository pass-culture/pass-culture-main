""" local providers BankInformation test """
from datetime import datetime
from unittest.mock import patch, ANY

from local_providers import BankInformationProvider
from models import BankInformation, LocalProviderEvent
from models.local_provider_event import LocalProviderEventType
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_bank_information
from tests.model_creators.provider_creators import provider_test


class TestableBankInformationProvider(BankInformationProvider):
    def __init__(self):
        """
        Empty constructor that makes this class testable :
        no API call is made at instantiation time
        """
        pass


class BankInformationProviderProviderTest:
    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    def test_provider_creates_nothing_if_no_data_retrieved_from_api(self, get_application_details,
                                                                    get_all_application_ids_for_procedure,
                                                                    app):
        # Given
        get_application_details.return_value = {}
        get_all_application_ids_for_procedure.return_value = []

        # When Then
        provider_test(app,
                      BankInformationProvider,
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
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_creates_one_bank_information_with_id_at_prividers_siren_if_request_for_siren(self,
                                                                                                   get_application_details,
                                                                                                   get_all_application_ids_for_procedure,
                                                                                                   app):
        # Given
        get_all_application_ids_for_procedure.return_value = [1]
        get_application_details.return_value = {
            "dossier":
                {
                    "id": 1,
                    "updated_at": "2019-01-21T18:55:03.387Z",
                    "state": "closed",
                    "entreprise":
                        {
                            "siren": "793875030",
                            "siret_siege_social": "79387503000017"
                        },
                    "etablissement":
                        {
                            "siret": "79387503000016"
                        },
                    "champs":
                        [
                            {
                                "value": "Le RIB par défaut pour toute structure liée à mon SIREN",
                                "type_de_champ":
                                    {
                                        "id": 352721,
                                        "libelle": "Je souhaite renseigner",
                                        "type_champ": "drop_down_list",
                                        "order_place": 6,
                                        "description": ""
                                    }
                            },
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
                            },
                        ]
                }
        }
        offerer = create_offerer(siren='793875030')
        venue = create_venue(offerer, siret='79387503000016')

        Repository.save(venue)

        offerer_id = offerer.id

        # When Then
        provider_test(app,
                      BankInformationProvider,
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
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_creates_one_bank_information_with_id_at_prividers_siret_if_request_for_siret(self,
                                                                                                   get_application_details,
                                                                                                   get_all_application_ids_for_procedure,
                                                                                                   app):
        # Given
        get_all_application_ids_for_procedure.return_value = [1]
        get_application_details.return_value = {
            "dossier":
                {
                    "id": 1,
                    "updated_at": "2019-01-21T18:55:03.387Z",
                    "state": "closed",
                    "entreprise":
                        {
                            "siren": "793875030",
                            "siret_siege_social": "79387503000017"
                        },
                    "etablissement":
                        {
                            "siret": "79387503000016"
                        },
                    "champs":
                        [
                            {
                                "value": "Le RIB lié à un unique SIRET",
                                "type_de_champ": {
                                    "id": 352721,
                                    "libelle": "Je souhaite renseigner",
                                    "type_champ": "drop_down_list",
                                    "order_place": 6,
                                    "description": ""
                                }
                            },
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
                            },
                        ]
                }
        }
        offerer = create_offerer(siren='793875030')
        venue = create_venue(offerer, siret='79387503000016')

        Repository.save(venue)

        offerer_id = offerer.id
        venue_id = venue.id

        # When Then
        provider_test(app,
                      BankInformationProvider,
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
        assert bank_information.offererId == None
        assert bank_information.venueId == venue_id
        assert bank_information.idAtProviders == '79387503000016'

    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_raises_unknown_rib_affiliation_exception_when_rib_affiliation_unknown_but_saves_older_bank_information(
            self,
            get_application_details,
            get_all_application_ids_for_procedure,
            app):
        # Given
        get_all_application_ids_for_procedure.return_value = [2, 1]
        get_application_details.side_effect = [
            {
                "dossier":
                    {
                        "id": 2,
                        "updated_at": "2019-01-20T18:55:03.387Z",
                        "state": "closed",
                        "entreprise":
                            {
                                "siren": "793875030",
                                "siret_siege_social": "79387503000017"
                            },
                        "etablissement":
                            {
                                "siret": "79387503000016"
                            },
                        "champs":
                            [
                                {
                                    "value": "Le RIB lié à un unique SIRET",
                                    "type_de_champ": {
                                        "id": 352721,
                                        "libelle": "Je souhaite renseigner",
                                        "type_champ": "drop_down_list",
                                        "order_place": 6,
                                        "description": ""
                                    }
                                },
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
                                },
                            ]
                    }
            },
            {
                "dossier":
                    {
                        "id": 1,
                        "updated_at": "2019-01-21T18:55:03.387Z",
                        "state": "closed",
                        "entreprise":
                            {
                                "siren": "793875030",
                                "siret_siege_social": "79387503000017"
                            },
                        "etablissement":
                            {
                                "siret": "79387503000016"
                            },
                        "champs":
                            [
                                {
                                    "value": "Champ chelou auquel on n'a pas pensé",
                                    "type_de_champ": {
                                        "id": 352721,
                                        "libelle": "Je souhaite renseigner",
                                        "type_champ": "drop_down_list",
                                        "order_place": 6,
                                        "description": ""
                                    }
                                },
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
                                },
                            ]
                    }
            }
        ]
        offerer = create_offerer(siren='793875030')
        venue = create_venue(offerer, siret='79387503000016')

        Repository.save(venue)

        bank_information_provider = BankInformationProvider()
        bank_information_provider.provider.isActive = True
        Repository.save(bank_information_provider.provider)

        # when
        bank_information_provider.updateObjects()

        # Then
        bank_information = BankInformation.query.all()
        assert len(bank_information)
        assert bank_information[0].idAtProviders == '79387503000016'
        sync_error = LocalProviderEvent.query \
            .filter_by(type=LocalProviderEventType.SyncError) \
            .first()
        assert sync_error.payload == 'unknown RIB affiliation for application id 1'

    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_checks_two_objects_and_creates_two_when_both_rib_affiliations_are_known(
            self,
            get_application_details,
            get_all_application_ids_for_procedure,
            app):
        # Given
        get_all_application_ids_for_procedure.return_value = [1, 2]
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
                        "etablissement":
                            {
                                "siret": "79387501900056"
                            },
                        "champs":
                            [
                                {
                                    "value": "Le RIB lié à un unique SIRET",
                                    "type_de_champ": {
                                        "id": 352721,
                                        "libelle": "Je souhaite renseigner",
                                        "type_champ": "drop_down_list",
                                        "order_place": 6,
                                        "description": ""
                                    }
                                },
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
                                "siret_siege_social": "79387503000017"
                            },
                        "etablissement":
                            {
                                "siret": "79387503000016"
                            },
                        "champs":
                            [
                                {
                                    "value": "Le RIB lié à un unique SIRET",
                                    "type_de_champ": {
                                        "id": 352721,
                                        "libelle": "Je souhaite renseigner",
                                        "type_champ": "drop_down_list",
                                        "order_place": 6,
                                        "description": ""
                                    }
                                },
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
        venue1 = create_venue(offerer1, siret='79387501900056')

        offerer2 = create_offerer(siren='793875030')
        venue2 = create_venue(offerer2, siret='79387503000016')

        Repository.save(venue1, venue2)
        venue1_id = venue1.id
        venue2_id = venue2.id

        # When Then
        provider_test(app,
                      BankInformationProvider,
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
        bank_information1 = BankInformation.query.filter_by(applicationId=1).first()
        bank_information2 = BankInformation.query.filter_by(applicationId=2).first()
        assert bank_information1.iban == 'FR7630006000011234567890189'
        assert bank_information1.bic == 'BDFEFR2LCCB'
        assert bank_information1.applicationId == 1
        assert bank_information1.offererId == None
        assert bank_information1.venueId == venue1_id
        assert bank_information1.idAtProviders == '79387501900056'
        assert bank_information2.iban == 'FR7630007000111234567890144'
        assert bank_information2.bic == 'SOGEFRPP'
        assert bank_information2.applicationId == 2
        assert bank_information2.offererId == None
        assert bank_information2.venueId == venue2_id
        assert bank_information2.idAtProviders == '79387503000016'

    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_does_not_create_bank_information_if_siren_unknown(
            self,
            get_application_details,
            get_all_application_ids_for_procedure,
            app):
        # Given
        get_all_application_ids_for_procedure.return_value = [1]
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
                        "etablissement":
                            {
                                "siret": "79387501900056"
                            },
                        "champs":
                            [
                                {
                                    "value": "Le RIB lié à un unique SIRET",
                                    "type_de_champ": {
                                        "id": 352721,
                                        "libelle": "Je souhaite renseigner",
                                        "type_champ": "drop_down_list",
                                        "order_place": 6,
                                        "description": ""
                                    }
                                },
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
                      BankInformationProvider,
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

        sync_error = LocalProviderEvent.query.filter_by(type=LocalProviderEventType.SyncError).first()
        assert sync_error.payload == 'unknown siret or siren for application id 1'
        assert len(LocalProviderEvent.query.all()) == 3

    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_updates_existing_bank_information(
            self,
            get_application_details,
            get_all_application_ids_for_procedure,
            app):
        # Given
        get_all_application_ids_for_procedure.return_value = [1]
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
                                "siret_siege_social": "79387501900089"
                            },
                        "etablissement":
                            {
                                "siret": "79387501900056"
                            },
                        "champs":
                            [
                                {
                                    "value": "Le RIB lié à un unique SIRET",
                                    "type_de_champ": {
                                        "id": 352721,
                                        "libelle": "Je souhaite renseigner",
                                        "type_champ": "drop_down_list",
                                        "order_place": 6,
                                        "description": ""
                                    }
                                },
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
        venue = create_venue(offerer, siret='79387501900056')

        bank_information = create_bank_information(id_at_providers="79387501900056", venue=venue)
        Repository.save(bank_information)

        # When Then
        provider_test(app,
                      BankInformationProvider,
                      None,
                      checkedObjects=1,
                      createdObjects=0,
                      updatedObjects=1,
                      erroredObjects=0,
                      checkedThumbs=0,
                      createdThumbs=0,
                      updatedThumbs=0,
                      erroredThumbs=0)

        updated_bank_information = BankInformation.query.filter_by(idAtProviders="79387501900056").one()
        assert updated_bank_information.applicationId == 2
        assert updated_bank_information.iban == "FR7630006000011234567890189"
        assert updated_bank_information.bic == "BDFEFR2LCCB"

    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_does_not_save_bank_information_if_wrong_bic_or_iban_but_continues_flow(
            self,
            get_application_details,
            get_all_application_ids_for_procedure,
            app):
        # given
        get_all_application_ids_for_procedure.return_value = [1, 2]
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
                                "siret_siege_social": "79387501900089"
                            },
                        "etablissement":
                            {
                                "siret": "79387501900056"
                            },
                        "champs":
                            [
                                {
                                    "value": "Le RIB lié à un unique SIRET",
                                    "type_de_champ": {
                                        "id": 352721,
                                        "libelle": "Je souhaite renseigner",
                                        "type_champ": "drop_down_list",
                                        "order_place": 6,
                                        "description": ""
                                    }
                                },
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
                                "siret_siege_social": "79387503000017"
                            },
                        "etablissement":
                            {
                                "siret": "79387503000016"
                            },
                        "champs":
                            [
                                {
                                    "value": "Le RIB lié à un unique SIRET",
                                    "type_de_champ": {
                                        "id": 352721,
                                        "libelle": "Je souhaite renseigner",
                                        "type_champ": "drop_down_list",
                                        "order_place": 6,
                                        "description": ""
                                    }
                                },
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
        venue_ko = create_venue(offerer_ko, siret='79387501900056')
        offerer_ok = create_offerer(siren="793875030")
        venue_ok = create_venue(offerer_ok, siret="79387503000016")

        Repository.save(venue_ko, venue_ok)

        bank_information_provider = BankInformationProvider()
        bank_information_provider.provider.isActive = True
        Repository.save(bank_information_provider.provider)

        # when
        bank_information_provider.updateObjects()

        # then
        bank_information = BankInformation.query.all()
        assert len(bank_information) == 1
        assert bank_information[0].applicationId == 2
        local_provider_event = LocalProviderEvent.query.filter_by(type=LocalProviderEventType.SyncError).one()
        assert local_provider_event.payload == 'ApiErrors'

    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_calls_get_all_application_ids_with_1900_01_01_when_table_bank_information_is_empty(
            self,
            get_application_details,
            get_all_application_ids_for_procedure,
            app):
        # given
        get_all_application_ids_for_procedure.return_value = [1]
        get_application_details.return_value = {
            "dossier":
                {
                    "id": 2,
                    "updated_at": "2019-01-21T18:55:03.387Z",
                    "state": "closed",
                    "entreprise":
                        {
                            "siren": "793875019",
                            "siret_siege_social": "79387501900089"
                        },
                    "etablissement":
                        {
                            "siret": "79387501900056"
                        },
                    "champs":
                        [
                            {
                                "value": "Le RIB lié à un unique SIRET",
                                "type_de_champ": {
                                    "id": 352721,
                                    "libelle": "Je souhaite renseigner",
                                    "type_champ": "drop_down_list",
                                    "order_place": 6,
                                    "description": ""
                                }
                            },
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

        bank_information_provider = BankInformationProvider()
        bank_information_provider.provider.isActive = True
        Repository.save(bank_information_provider.provider)

        # when
        bank_information_provider.updateObjects()

        # then
        get_all_application_ids_for_procedure.assert_called_with(ANY, ANY,
                                                                                        datetime(1900, 1, 1))

    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_calls_get_all_application_ids_with_last_update_from_table_bank_information(
            self,
            get_application_details,
            get_all_application_ids_for_procedure,
            app):
        # given
        get_all_application_ids_for_procedure.return_value = [1]
        get_application_details.return_value = {
            "dossier":
                {
                    "id": 2,
                    "updated_at": "2019-01-21T18:55:03.387Z",
                    "state": "closed",
                    "entreprise":
                        {
                            "siren": "793875019",
                            "siret_siege_social": "79387501900089"
                        },
                    "etablissement":
                        {
                            "siret": "79387501900056"
                        },
                    "champs":
                        [
                            {
                                "value": "Le RIB lié à un unique SIRET",
                                "type_de_champ": {
                                    "id": 352721,
                                    "libelle": "Je souhaite renseigner",
                                    "type_champ": "drop_down_list",
                                    "order_place": 6,
                                    "description": ""
                                }
                            },
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
        venue = create_venue(offerer, siret='79387501900056')

        bank_information = create_bank_information(id_at_providers='79387501900056',
                                                   date_modified_at_last_provider=datetime(2019, 1, 1), venue=venue)
        Repository.save(bank_information)

        bank_information_provider = BankInformationProvider()
        bank_information_provider.provider.isActive = True
        Repository.save(bank_information_provider.provider)

        # when
        bank_information_provider.updateObjects()

        # then
        get_all_application_ids_for_procedure.assert_called_with(ANY, ANY,
                                                                                        datetime(2019, 1, 1))

    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_for_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_creates_one_bank_information_and_format_IBAN_and_BIC(self,
                                                                           get_application_details,
                                                                           get_all_application_ids_for_procedure,
                                                                           app):
        # Given
        get_all_application_ids_for_procedure.return_value = [1]
        get_application_details.return_value = {
            "dossier":
                {
                    "id": 1,
                    "updated_at": "2019-01-21T18:55:03.387Z",
                    "state": "closed",
                    "entreprise":
                        {
                            "siren": "793875030",
                            "siret_siege_social": "79387503000017"
                        },
                    "etablissement":
                        {
                            "siret": "79387503000016"
                        },
                    "champs":
                        [
                            {
                                "value": "Le RIB par défaut pour toute structure liée à mon SIREN",
                                "type_de_champ":
                                    {
                                        "id": 352721,
                                        "libelle": "Je souhaite renseigner",
                                        "type_champ": "drop_down_list",
                                        "order_place": 6,
                                        "description": ""
                                    }
                            },
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
        venue = create_venue(offerer, siret='79387503000016')

        Repository.save(venue)

        # When Then
        provider_test(app,
                      BankInformationProvider,
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
    def when_rib_affiliation_is_on_siret(self, app):
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
                    "etablissement":
                        {
                            "siret": "79387501900056"
                        },
                    "champs":
                        [
                            {
                                "value": "Le RIB lié à un unique SIRET",
                                "type_de_champ": {
                                    "libelle": "Je souhaite renseigner",
                                }
                            },
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
        venue = create_venue(offerer, siret="79387501900056")
        Repository.save(venue)
        venue_id = venue.id

        bank_information_provider = TestableBankInformationProvider()

        # When
        bank_information_dict = bank_information_provider.retrieve_bank_information(application_details)

        # Then
        assert bank_information_dict['iban'] == "FR7630006000011234567890189"
        assert bank_information_dict['bic'] == "BDFEFR2LCCB"
        assert bank_information_dict['applicationId'] == 1
        assert 'offererId' not in bank_information_dict
        assert bank_information_dict['venueId'] == venue_id

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
                    "etablissement":
                        {
                            "siret": "79387501900056"
                        },
                    "champs":
                        [
                            {
                                "value": "Le RIB par défaut pour toute structure liée à mon SIREN",
                                "type_de_champ": {
                                    "libelle": "Je souhaite renseigner",
                                }
                            },
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
        Repository.save(offerer)
        offerer_id = offerer.id
        bank_information_provider = TestableBankInformationProvider()

        # When
        bank_information_dict = bank_information_provider.retrieve_bank_information(application_details)

        # Then
        assert bank_information_dict['iban'] == "FR7630006000011234567890189"
        assert bank_information_dict['bic'] == "BDFEFR2LCCB"
        assert bank_information_dict['applicationId'] == 1
        assert bank_information_dict['offererId'] == offerer_id
        assert 'venueId' not in bank_information_dict
