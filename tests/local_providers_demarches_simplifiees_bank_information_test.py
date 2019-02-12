import pytest
from unittest.mock import patch

from local_providers import BankInformationProvider
from models import BankInformation, PcObject
from tests.conftest import clean_database
from utils.test_utils import provider_test_without_mock, create_venue, create_offerer


@pytest.mark.standalone
class DemarchesSimplifieesBankInformationTest:
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
        assert bank_information.venueId == venue_id
        assert bank_information.idAtProviders == '793875030'

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
        assert bank_information.offererId == offerer_id
        assert bank_information.venueId == venue_id
        assert bank_information.idAtProviders == '79387503000016'
