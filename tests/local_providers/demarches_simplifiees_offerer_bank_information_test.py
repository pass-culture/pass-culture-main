from datetime import datetime
from unittest.mock import patch, ANY

from local_providers import OffererBankInformationProvider
from local_providers import BankInformationProvider
from models import BankInformation, LocalProviderEvent
from models.local_provider_event import LocalProviderEventType
from repository import repository
from repository.provider_queries import get_provider_by_local_class
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_bank_information
from tests.model_creators.provider_creators import provider_test, activate_provider
from utils.date import DATE_ISO_FORMAT
from connectors.api_demarches_simplifiees import DmsApplicationStates


class TestableOffererBankInformationProvider(OffererBankInformationProvider):
    def __init__(self):
        """
        Empty constructor that makes this class testable :
        no API call is made at instantiation time
        """
        pass


def demarche_simplifiee_application_detail_response(siren, bic, iban,
                                                    idx=1,
                                                    updated_at="2019-01-21T18:55:03.387Z",
                                                    state=DmsApplicationStates.closed.name):
    return {
        "dossier":
        {
            "id": idx,
            "updated_at": updated_at,
            "state": state,
            "entreprise":
            {
                "siren": siren,
            },
            "champs":
            [
                {
                    "value": bic,
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
                    "value": iban,
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


class OffererBankInformationProviderProviderTest:
    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    def test_provider_creates_nothing_if_no_data_retrieved_from_api(self, get_application_details,
                                                                    get_all_application_ids_for_demarche_simplifiee,
                                                                    app):
        # Given
        get_application_details.return_value = {}
        get_all_application_ids_for_demarche_simplifiee.return_value = []

        # When
        OffererBankInformationProvider().updateObjects()

        # Then
        assert BankInformation.query.count() == 0

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_checks_two_objects_and_creates_two_when_two_applications_are_received(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1, 2]
        get_application_details.side_effect = [
            demarche_simplifiee_application_detail_response(
                siren="793875019", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=1),
            demarche_simplifiee_application_detail_response(
                siren="793875030", bic="BDFEFR2ALLD", iban="FR7630006000011234567891234", idx=2, state=DmsApplicationStates.received.name),
        ]
        offerer1 = create_offerer(siren='793875019')
        offerer2 = create_offerer(siren='793875030')
        repository.save(offerer1, offerer2)

        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()

        # When
        offerer_bank_information_provider.updateObjects()

        # Then
        assert BankInformation.query.count() == 2
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

        assert bank_information2.iban == None
        assert bank_information2.bic == None
        assert bank_information2.applicationId == 2
        assert bank_information2.offererId == offerer2.id
        assert bank_information2.venueId == None
        assert bank_information2.idAtProviders == '793875030'

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_does_not_create_bank_information_if_siren_unknown(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1]
        get_application_details.side_effect = [
            demarche_simplifiee_application_detail_response(
                siren="793875019", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189"),
        ]
        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()

        # When
        offerer_bank_information_provider.updateObjects()

        # Then
        assert BankInformation.query.count() == 0
        sync_error = LocalProviderEvent.query.filter_by(
            type=LocalProviderEventType.SyncError).first()
        assert sync_error.payload == 'unknown siren for application id 1'
        events = LocalProviderEvent.query.all()
        assert events[0].type == LocalProviderEventType.SyncStart
        assert events[1].type == LocalProviderEventType.SyncError
        assert events[2].type == LocalProviderEventType.SyncEnd

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_creates_one_bank_information_and_format_IBAN_and_BIC(self,
                                                                           get_application_details,
                                                                           get_all_application_ids_for_demarche_simplifiee,
                                                                           app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1]
        get_application_details.return_value = demarche_simplifiee_application_detail_response(
            siren="793875030", bic="BdFefr2LCCB", iban="FR76 3000 6000  0112 3456 7890 189")
        offerer = create_offerer(siren='793875030')

        repository.save(offerer)
        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()

        # When
        offerer_bank_information_provider.updateObjects()

        # Then
        bank_information = BankInformation.query.one()
        assert bank_information.iban == 'FR7630006000011234567890189'
        assert bank_information.bic == 'BDFEFR2LCCB'

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_creates_bank_informations_with_correct_status(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = [
            1, 2, 3, 4, 5]
        get_application_details.side_effect = [
            demarche_simplifiee_application_detail_response(
                siren="793875015", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=1, state=DmsApplicationStates.closed.name),
            demarche_simplifiee_application_detail_response(
                siren="793875016", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=2, state=DmsApplicationStates.initiated.name),
            demarche_simplifiee_application_detail_response(
                siren="793875017", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=3, state=DmsApplicationStates.refused.name),
            demarche_simplifiee_application_detail_response(
                siren="793875018", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=4, state=DmsApplicationStates.received.name),
            demarche_simplifiee_application_detail_response(
                siren="793875019", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=5, state=DmsApplicationStates.without_continuation.name),
        ]
        repository.save(
            create_offerer(siren='793875015'),
            create_offerer(siren='793875016'),
            create_offerer(siren='793875017'),
            create_offerer(siren='793875018'),
            create_offerer(siren='793875019')
        )
        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()

        # When
        offerer_bank_information_provider.updateObjects()

        # Then
        assert BankInformation.query.count() == 5
        bank_information1 = BankInformation.query.filter_by(
            applicationId=1).one()
        bank_information2 = BankInformation.query.filter_by(
            applicationId=2).one()
        bank_information3 = BankInformation.query.filter_by(
            applicationId=3).one()
        bank_information4 = BankInformation.query.filter_by(
            applicationId=4).one()
        bank_information5 = BankInformation.query.filter_by(
            applicationId=5).one()
        assert bank_information1.status == "ACCEPTED"
        assert bank_information2.status == "DRAFT"
        assert bank_information3.status == "REJECTED"
        assert bank_information4.status == "DRAFT"
        assert bank_information5.status == "REJECTED"

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_updates_existing_bank_information_with_new_bank_information(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1]
        get_application_details.side_effect = [
            demarche_simplifiee_application_detail_response(
                siren="793875019", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189"),
        ]

        offerer = create_offerer(siren='793875019')

        bank_information = create_bank_information(
            id_at_providers="793875019", offerer=offerer)
        repository.save(bank_information)
        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()

        # When
        offerer_bank_information_provider.updateObjects()

        # Then
        updated_bank_information = BankInformation.query.one()
        assert updated_bank_information.applicationId == 1
        assert updated_bank_information.iban == "FR7630006000011234567890189"
        assert updated_bank_information.bic == "BDFEFR2LCCB"

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_bank_information_fields_are_cleared_when_application_status_change(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1]
        get_application_details.side_effect = [
            demarche_simplifiee_application_detail_response(
                siren="793875019", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", state=DmsApplicationStates.initiated.name),
        ]

        offerer = create_offerer(siren='793875019')
        bank_information = create_bank_information(
            id_at_providers="793875019", offerer=offerer)
        repository.save(bank_information)
        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()

        # When
        offerer_bank_information_provider.updateObjects()

        # Then
        updated_bank_information = BankInformation.query.one()
        assert updated_bank_information.applicationId == 1
        assert updated_bank_information.iban == None
        assert updated_bank_information.bic == None

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_update_bank_information_based_on_application_id(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = [3, 2]
        get_application_details.side_effect = [
            demarche_simplifiee_application_detail_response(
                siren="793875018", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=3, state=DmsApplicationStates.refused.name),
            demarche_simplifiee_application_detail_response(
                siren="793875019", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=2, state=DmsApplicationStates.refused.name),
        ]

        offerer1 = create_offerer(siren='793875018')
        offerer2 = create_offerer(siren='793875019')
        bank_information_witness = create_bank_information(
            id_at_providers="793875018", offerer=offerer1, application_id=1)
        bank_information = create_bank_information(
            id_at_providers="793875019", offerer=offerer2, application_id=2)
        repository.save(bank_information, bank_information_witness)
        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()

        # When
        offerer_bank_information_provider.updateObjects()

        # Then
        bank_information_witness = BankInformation.query.filter_by(
            idAtProviders="793875018").one()
        bank_information = BankInformation.query.filter_by(
            idAtProviders="793875019").one()
        assert bank_information_witness.status == "ACCEPTED"
        assert bank_information.status == "REJECTED"

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_update_bank_information_based_on_status(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = [
            1, 2, 3, 4]
        get_application_details.side_effect = [
            demarche_simplifiee_application_detail_response(
                siren="793875016", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=1, state=DmsApplicationStates.closed.name),
            demarche_simplifiee_application_detail_response(
                siren="793875017", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=2, state=DmsApplicationStates.closed.name),
            demarche_simplifiee_application_detail_response(
                siren="793875018", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=3, state=DmsApplicationStates.received.name),
            demarche_simplifiee_application_detail_response(
                siren="793875019", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=4, state=DmsApplicationStates.refused.name),
        ]

        offerer1 = create_offerer(siren='793875016')
        offerer2 = create_offerer(siren='793875017')
        offerer3 = create_offerer(siren='793875018')
        offerer4 = create_offerer(siren='793875019')
        bank_information1 = create_bank_information(
            id_at_providers="793875016", offerer=offerer1, application_id=5, status="REJECTED")
        bank_information2 = create_bank_information(
            id_at_providers="793875017", offerer=offerer2, application_id=6, status="DRAFT")
        bank_information3 = create_bank_information(
            id_at_providers="793875018", offerer=offerer3, application_id=7, status="ACCEPTED")
        bank_information4 = create_bank_information(
            id_at_providers="793875019", offerer=offerer4, application_id=8, status="DRAFT")
        repository.save(bank_information1, bank_information2,
                        bank_information3, bank_information4)
        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()

        # When
        offerer_bank_information_provider.updateObjects()

        # Then
        bank_information1 = BankInformation.query.filter_by(
            idAtProviders="793875016").one()
        bank_information2 = BankInformation.query.filter_by(
            idAtProviders="793875017").one()
        bank_information3 = BankInformation.query.filter_by(
            idAtProviders="793875018").one()
        bank_information4 = BankInformation.query.filter_by(
            idAtProviders="793875019").one()
        assert bank_information1.status == "ACCEPTED"
        assert bank_information2.status == "ACCEPTED"
        assert bank_information3.status == "ACCEPTED"
        assert bank_information4.status == "DRAFT"

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_update_bank_information_based_on_last_date(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1, 2]
        get_application_details.side_effect = [
            demarche_simplifiee_application_detail_response(
                siren="793875016", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=1, state=DmsApplicationStates.closed.name, updated_at=datetime(2020, 1, 1).strftime(DATE_ISO_FORMAT)),
            demarche_simplifiee_application_detail_response(
                siren="793875017", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189", idx=2, state=DmsApplicationStates.closed.name, updated_at=datetime(2020, 1, 3).strftime(DATE_ISO_FORMAT)),
        ]

        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()
        offerer1 = create_offerer(siren='793875016')
        offerer2 = create_offerer(siren='793875017')
        bank_information1 = create_bank_information(
            id_at_providers="793875016", offerer=offerer1, application_id=1, status="DRAFT", date_modified_at_last_provider=datetime(2020, 1, 2), last_provider_id=offerer_bank_information_provider.provider.id)
        bank_information2 = create_bank_information(
            id_at_providers="793875017", offerer=offerer2, application_id=2, status="DRAFT", date_modified_at_last_provider=datetime(2020, 1, 2), last_provider_id=offerer_bank_information_provider.provider.id)
        repository.save(bank_information1, bank_information2)

        # When
        offerer_bank_information_provider.updateObjects()

        # Then
        bank_information1 = BankInformation.query.filter_by(
            idAtProviders="793875016").one()
        bank_information2 = BankInformation.query.filter_by(
            idAtProviders="793875017").one()
        assert bank_information1.status == "ACCEPTED"
        assert bank_information2.status == "DRAFT"

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_does_not_save_bank_information_if_wrong_bic_or_iban_but_continues_flow(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1, 2]
        get_application_details.side_effect = [
            demarche_simplifiee_application_detail_response(
                siren="793875019", bic="wrongbic", iban="wrongiban", idx=1),
            demarche_simplifiee_application_detail_response(
                siren="793875030", bic="SOGEFRPP", iban="FR7630007000111234567890144", idx=2),
        ]
        offerer_ko = create_offerer(siren='793875019')
        offerer_ok = create_offerer(siren="793875030")
        repository.save(offerer_ko, offerer_ok)
        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()

        # When
        offerer_bank_information_provider.updateObjects()

        # then
        bank_information = BankInformation.query.one()
        assert bank_information.applicationId == 2
        local_provider_event = LocalProviderEvent.query.filter_by(
            type=LocalProviderEventType.SyncError).one()
        assert local_provider_event.payload == 'ApiErrors'

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_calls_get_all_application_ids_with_1900_01_01_when_table_bank_information_is_empty(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1]
        get_application_details.return_value = demarche_simplifiee_application_detail_response(
            siren="793875030", bic="BdFefr2LCCB", iban="FR76 3000 6000  0112 3456 7890 189")
        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()

        # When
        offerer_bank_information_provider.updateObjects()

        # then
        get_all_application_ids_for_demarche_simplifiee.assert_called_with(ANY, ANY,
                                                                           datetime(1900, 1, 1))

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_calls_get_all_application_ids_with_last_update_from_table_bank_information(
            self,
            get_application_details,
            get_all_application_ids_for_demarche_simplifiee,
            app):
        # given
        get_all_application_ids_for_demarche_simplifiee.return_value = [1]
        get_application_details.return_value = demarche_simplifiee_application_detail_response(
            siren="793875030", bic="BdFefr2LCCB", iban="FR76 3000 6000  0112 3456 7890 189")

        offerer = create_offerer(siren='793875019')

        bank_information = create_bank_information(id_at_providers='79387501900056',
                                                   date_modified_at_last_provider=datetime(
                                                       2019, 1, 1),
                                                   last_provider_id=get_provider_by_local_class(
                                                       'OffererBankInformationProvider').id,
                                                   offerer=offerer)
        repository.save(bank_information)
        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()

        # When
        offerer_bank_information_provider.updateObjects()

        # then
        get_all_application_ids_for_demarche_simplifiee.assert_called_with(ANY, ANY,
                                                                           datetime(2019, 1, 1))

    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_RIB_OFFERER_PROCEDURE_ID': 'procedure_id'})
    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_TOKEN': 'token'})
    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_request_application_ids_using_correct_date(self,
                                                                 get_application_details,
                                                                 get_all_application_ids_for_demarche_simplifiee,
                                                                 app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = []
        offerer = create_offerer(siren='793875030')
        offerer2 = create_offerer(siren='793875019')
        bank_information = create_bank_information(id_at_providers='793875030',
                                                   date_modified_at_last_provider=datetime(
                                                       2019, 1, 1),
                                                   last_provider_id=get_provider_by_local_class(
                                                       'OffererBankInformationProvider').id,
                                                   offerer=offerer)
        bank_information2 = create_bank_information(id_at_providers='793875019',
                                                    date_modified_at_last_provider=datetime(
                                                        2020, 1, 1),
                                                    last_provider_id=get_provider_by_local_class(
                                                        'OffererBankInformationProvider').id,
                                                    offerer=offerer2)
        repository.save(bank_information, bank_information2)
        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()

        # When
        offerer_bank_information_provider.updateObjects()

        # Then
        get_all_application_ids_for_demarche_simplifiee.assert_called_once_with(
            'procedure_id',
            'token',
            datetime(
                2020, 1, 1)
        )

    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_RIB_OFFERER_PROCEDURE_ID': 'procedure_id'})
    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_TOKEN': 'token'})
    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_request_application_ids_using_given_date(self,
                                                               get_application_details,
                                                               get_all_application_ids_for_demarche_simplifiee,
                                                               app):
        # Given
        get_all_application_ids_for_demarche_simplifiee.return_value = []
        offerer = create_offerer(siren='793875030')
        offerer2 = create_offerer(siren='793875019')
        bank_information = create_bank_information(id_at_providers='793875030',
                                                   date_modified_at_last_provider=datetime(
                                                       2019, 1, 1),
                                                   last_provider_id=get_provider_by_local_class(
                                                       'OffererBankInformationProvider').id,
                                                   offerer=offerer)
        bank_information2 = create_bank_information(id_at_providers='793875019',
                                                    date_modified_at_last_provider=datetime(
                                                        2020, 1, 1),
                                                    last_provider_id=get_provider_by_local_class(
                                                        'OffererBankInformationProvider').id,
                                                    offerer=offerer2)
        repository.save(bank_information, bank_information2)

        # When
        provider_object = OffererBankInformationProvider(
            minimum_requested_datetime=datetime(2019, 6, 1))
        provider_object.provider.isActive = True
        repository.save(provider_object.provider)
        provider_object.updateObjects()

        # Then
        get_all_application_ids_for_demarche_simplifiee.assert_called_once_with(
            'procedure_id',
            'token',
            datetime(2019, 6, 1)
        )


class RetrieveBankInformationTest:
    @clean_database
    def when_rib_affiliation_is_on_siren(self, app):
        # Given
        application_details = demarche_simplifiee_application_detail_response(
            siren="793875019", bic="BDFEFR2LCCB", iban="FR7630006000011234567890189")
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

    @patch(
        'local_providers.demarches_simplifiees_offerer_bank_information.get_all_application_ids_for_demarche_simplifiee')
    @patch('local_providers.demarches_simplifiees_offerer_bank_information.get_application_details')
    @clean_database
    def test_provider_updates_one_bank_information_when_bank_information_from_another_provider_exists(self,
                                                                                                      get_application_details,
                                                                                                      get_all_application_ids_for_demarche_simplifiee,
                                                                                                      app):
        # Given
        date_updated = datetime(2020, 4, 15)
        get_all_application_ids_for_demarche_simplifiee.return_value = [1]
        get_application_details.return_value = demarche_simplifiee_application_detail_response(
            siren="793875030", bic="BDFEFR2LCCB", iban="DE89370400440532013000", updated_at=date_updated.strftime(DATE_ISO_FORMAT))

        offerer = create_offerer(siren='793875030')
        bank_information = create_bank_information(id_at_providers='793875030',
                                                   iban='FR7630006000011234567890189',
                                                   date_modified_at_last_provider=datetime(
                                                       2018, 1, 1),
                                                   offerer=offerer)
        repository.save(bank_information)

        offerer_id = offerer.id
        provider_id = get_provider_by_local_class(
            'OffererBankInformationProvider').id
        activate_provider('OffererBankInformationProvider')
        offerer_bank_information_provider = OffererBankInformationProvider()

        # When
        offerer_bank_information_provider.updateObjects()

        # Then
        bank_information = BankInformation.query.one()
        assert bank_information.iban == 'DE89370400440532013000'
        assert bank_information.bic == 'BDFEFR2LCCB'
        assert bank_information.applicationId == 1
        assert bank_information.offererId == offerer_id
        assert bank_information.idAtProviders == '793875030'
        assert bank_information.lastProviderId == provider_id
        assert bank_information.dateModifiedAtLastProvider == date_updated
