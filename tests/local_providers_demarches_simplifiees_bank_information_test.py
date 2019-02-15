import pytest
from unittest.mock import patch

from local_providers import BankInformationProvider
from local_providers.demarches_simplifiees_bank_information import retrieve_bank_information_dict_from
from models import BankInformation, PcObject, LocalProviderEvent
from models.local_provider_event import LocalProviderEventType
from tests.conftest import clean_database
from utils.test_utils import provider_test_without_mock, create_venue, create_offerer


@pytest.mark.standalone
class BankInformationProviderProviderTest:
    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_from_demarches_simplifiees_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    def test_provider_creates_nothing_if_no_data_retrieved_from_api(self, get_application_details,
                                                                    get_all_application_ids_from_demarches_simplifiees_procedure,
                                                                    app):
        # Given
        get_application_details.return_value = {}
        get_all_application_ids_from_demarches_simplifiees_procedure.return_value = []

        # When Then
        provider_test_without_mock(app,
                                   BankInformationProvider,
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
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_from_demarches_simplifiees_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_creates_one_bank_information_with_id_at_prividers_siren_if_request_for_siren(self,
                                                                                                   get_application_details,
                                                                                                   get_all_application_ids_from_demarches_simplifiees_procedure,
                                                                                                   app):
        # Given
        get_all_application_ids_from_demarches_simplifiees_procedure.return_value = [1]
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
                                "value": "TEST BIC",
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
                                "value": "TEST IBAN",
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

        PcObject.check_and_save(venue)

        offerer_id = offerer.id
        venue_id = venue.id

        # When Then
        provider_test_without_mock(app,
                                   BankInformationProvider,
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
        assert bank_information.iban == 'TEST IBAN'
        assert bank_information.bic == 'TEST BIC'
        assert bank_information.application_id == 1
        assert bank_information.offererId == offerer_id
        assert bank_information.venueId == None
        assert bank_information.idAtProviders == '793875030'
        local_provider_events = LocalProviderEvent.query.all()
        assert len(local_provider_events) == 2
        assert local_provider_events[0].type == LocalProviderEventType.SyncStart
        assert local_provider_events[1].type == LocalProviderEventType.SyncEnd

    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_from_demarches_simplifiees_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_creates_one_bank_information_with_id_at_prividers_siret_if_request_for_siret(self,
                                                                                                   get_application_details,
                                                                                                   get_all_application_ids_from_demarches_simplifiees_procedure,
                                                                                                   app):
        # Given
        get_all_application_ids_from_demarches_simplifiees_procedure.return_value = [1]
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
                                "value": "TEST BIC",
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
                                "value": "TEST IBAN",
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

        PcObject.check_and_save(venue)

        offerer_id = offerer.id
        venue_id = venue.id

        # When Then
        provider_test_without_mock(app,
                                   BankInformationProvider,
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
        assert bank_information.iban == 'TEST IBAN'
        assert bank_information.bic == 'TEST BIC'
        assert bank_information.application_id == 1
        assert bank_information.offererId == None
        assert bank_information.venueId == venue_id
        assert bank_information.idAtProviders == '79387503000016'

    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_from_demarches_simplifiees_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_checks_bank_information_and_does_not_create_object_if_unknown_rib_affiliation(self,
                                                                                                    get_application_details,
                                                                                                    get_all_application_ids_from_demarches_simplifiees_procedure,
                                                                                                    app):
        # Given
        get_all_application_ids_from_demarches_simplifiees_procedure.return_value = [1]
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
                                "value": "TEST BIC",
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
                                "value": "TEST IBAN",
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

        PcObject.check_and_save(venue)

        providerObj = BankInformationProvider()
        providerObj.dbObject.isActive = True
        PcObject.check_and_save(providerObj.dbObject)

        # When Then
        provider_test_without_mock(app,
                                   BankInformationProvider,
                                   checkedObjects=1,
                                   createdObjects=0,
                                   updatedObjects=0,
                                   erroredObjects=0,
                                   checkedThumbs=0,
                                   createdThumbs=0,
                                   updatedThumbs=0,
                                   erroredThumbs=0,
                                   BankInformation=0)

    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_from_demarches_simplifiees_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_checks_two_objects_and_creates_one_when_one_rib_affiliation_known_and_one_unknown(self,
                                                                                                        get_application_details,
                                                                                                        get_all_application_ids_from_demarches_simplifiees_procedure,
                                                                                                        app):
        # Given
        get_all_application_ids_from_demarches_simplifiees_procedure.return_value = [1, 2]
        get_application_details.side_effect = [
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
                                    "value": "TEST BIC",
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
                                    "value": "TEST IBAN",
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
                        "id": 2,
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
                                    "value": "TEST BIC",
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
                                    "value": "TEST IBAN",
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

        PcObject.check_and_save(venue)

        offerer_id = offerer.id
        venue_id = venue.id

        # When Then
        provider_test_without_mock(app,
                                   BankInformationProvider,
                                   checkedObjects=2,
                                   createdObjects=1,
                                   updatedObjects=0,
                                   erroredObjects=0,
                                   checkedThumbs=0,
                                   createdThumbs=0,
                                   updatedThumbs=0,
                                   erroredThumbs=0,
                                   BankInformation=1)
        bank_information = BankInformation.query.first()
        assert bank_information.iban == 'TEST IBAN'
        assert bank_information.bic == 'TEST BIC'
        assert bank_information.application_id == 2
        assert bank_information.offererId == None
        assert bank_information.venueId == venue_id
        assert bank_information.idAtProviders == '79387503000016'
        sync_error = LocalProviderEvent.query.filter_by(type=LocalProviderEventType.SyncError).first()
        assert sync_error.payload == 'unknown RIB affiliation for application id 1'

    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_from_demarches_simplifiees_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_checks_two_objects_and_creates_two_when_both_rib_affiliations_are_known(
            self,
            get_application_details,
            get_all_application_ids_from_demarches_simplifiees_procedure,
            app):
        # Given
        get_all_application_ids_from_demarches_simplifiees_procedure.return_value = [1, 2]
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
                                    "value": "TEST BIC1",
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
                                    "value": "TEST IBAN1",
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
                                    "value": "TEST BIC2",
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
                                    "value": "TEST IBAN2",
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

        PcObject.check_and_save(venue1, venue2)
        venue1_id = venue1.id
        venue2_id = venue2.id

        # When Then
        provider_test_without_mock(app,
                                   BankInformationProvider,
                                   checkedObjects=2,
                                   createdObjects=2,
                                   updatedObjects=0,
                                   erroredObjects=0,
                                   checkedThumbs=0,
                                   createdThumbs=0,
                                   updatedThumbs=0,
                                   erroredThumbs=0,
                                   BankInformation=2)
        bank_information1 = BankInformation.query.filter_by(application_id=1).first()
        bank_information2 = BankInformation.query.filter_by(application_id=2).first()
        assert bank_information1.iban == 'TEST IBAN1'
        assert bank_information1.bic == 'TEST BIC1'
        assert bank_information1.application_id == 1
        assert bank_information1.offererId == None
        assert bank_information1.venueId == venue1_id
        assert bank_information1.idAtProviders == '79387501900056'
        assert bank_information2.iban == 'TEST IBAN2'
        assert bank_information2.bic == 'TEST BIC2'
        assert bank_information2.application_id == 2
        assert bank_information2.offererId == None
        assert bank_information2.venueId == venue2_id
        assert bank_information2.idAtProviders == '79387503000016'

    @patch(
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_from_demarches_simplifiees_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_does_not_create_bank_information_if_siren_unknown(
            self,
            get_application_details,
            get_all_application_ids_from_demarches_simplifiees_procedure,
            app):
        # Given
        get_all_application_ids_from_demarches_simplifiees_procedure.return_value = [1]
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
                                    "value": "TEST BIC1",
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
                                    "value": "TEST IBAN1",
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
        provider_test_without_mock(app,
                                   BankInformationProvider,
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
        'local_providers.demarches_simplifiees_bank_information.get_all_application_ids_from_demarches_simplifiees_procedure')
    @patch('local_providers.demarches_simplifiees_bank_information.get_application_details')
    @clean_database
    def test_provider_updates_existing_bank_information(
            self,
            get_application_details,
            get_all_application_ids_from_demarches_simplifiees_procedure,
            app):
        # Given
        get_all_application_ids_from_demarches_simplifiees_procedure.return_value = [1]
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
                                    "value": "TEST BIC1",
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
                                    "value": "TEST IBAN1",
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

        PcObject.check_and_save(venue)
        venue_id = venue.id

        bank_information = BankInformation()
        bank_information.venueId = venue_id
        bank_information.application_id = 1
        bank_information.bic = "OLD BIC"
        bank_information.iban = "OLD IBAN"
        bank_information.idAtProviders = "79387501900056"
        PcObject.check_and_save(bank_information)

        # When Then
        provider_test_without_mock(app,
                                   BankInformationProvider,
                                   checkedObjects=1,
                                   createdObjects=0,
                                   updatedObjects=1,
                                   erroredObjects=0,
                                   checkedThumbs=0,
                                   createdThumbs=0,
                                   updatedThumbs=0,
                                   erroredThumbs=0)

        updated_bank_information = BankInformation.query.filter_by(idAtProviders="79387501900056").one()
        assert updated_bank_information.application_id == 2
        assert updated_bank_information.iban == "TEST IBAN1"
        assert updated_bank_information.bic == "TEST BIC1"


class CreateBankInformationWithTest:
    @clean_database
    def when_rib_affiliation_is_on_siret(self, app):
        # Given
        application_details = {
            "dossier":
                {
                    "id": 1,
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
                                "value": "TEST BIC1",
                                "type_de_champ":
                                    {
                                        "libelle": "BIC",
                                    }
                            },
                            {
                                "value": "TEST IBAN1",
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
        PcObject.check_and_save(venue)
        venue_id = venue.id

        # When
        bank_information_dict = retrieve_bank_information_dict_from(application_details)

        # Then
        assert bank_information_dict['iban'] == "TEST IBAN1"
        assert bank_information_dict['bic'] == "TEST BIC1"
        assert bank_information_dict['application_id'] == 1
        assert 'offererId' not in bank_information_dict
        assert bank_information_dict['venueId'] == venue_id

    @clean_database
    def when_rib_affiliation_is_on_siren(self, app):
        # Given
        application_details = {
            "dossier":
                {
                    "id": 1,
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
                                "value": "TEST BIC1",
                                "type_de_champ":
                                    {
                                        "libelle": "BIC",
                                    }
                            },
                            {
                                "value": "TEST IBAN1",
                                "type_de_champ":
                                    {
                                        "libelle": "IBAN",
                                    }
                            }
                        ]
                }
        }
        offerer = create_offerer(siren="793875019")
        PcObject.check_and_save(offerer)
        offerer_id = offerer.id

        # When
        bank_information_dict = retrieve_bank_information_dict_from(application_details)

        # Then
        assert bank_information_dict['iban'] == "TEST IBAN1"
        assert bank_information_dict['bic'] == "TEST BIC1"
        assert bank_information_dict['application_id'] == 1
        assert bank_information_dict['offererId'] == offerer_id
        assert 'venueId' not in bank_information_dict
