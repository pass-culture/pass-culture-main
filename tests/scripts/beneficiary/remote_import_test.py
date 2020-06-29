from datetime import datetime, timedelta
from unittest.mock import ANY, Mock, patch

from mailjet_rest import Client

from models import ApiErrors, BeneficiaryImport, ImportStatus, UserSQLEntity
from repository import repository
from scripts.beneficiary import remote_import
from scripts.beneficiary.remote_import import parse_beneficiary_information
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user
from tests.scripts.beneficiary.fixture import \
    APPLICATION_DETAIL_STANDARD_RESPONSE, \
    make_new_beneficiary_application_details

NOW = datetime.utcnow()
DATETIME_PATTERN = '%Y-%m-%dT%H:%M:%S.%fZ'
EIGHT_HOURS_AGO = (NOW - timedelta(hours=8)).strftime(DATETIME_PATTERN)
FOUR_HOURS_AGO = (NOW - timedelta(hours=4)).strftime(DATETIME_PATTERN)
TWO_DAYS_AGO = (NOW - timedelta(hours=48)).strftime(DATETIME_PATTERN)
ONE_WEEK_AGO = NOW - timedelta(days=7)


class RunTest:
    @patch('scripts.beneficiary.remote_import.process_beneficiary_application')
    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v2': '6712558'})
    def test_should_retrieve_applications_from_new_procedure_id(self, process_beneficiary_application):
        # given
        get_all_application_ids = Mock(return_value=[123, 456, 789])
        find_applications_ids_to_retry = Mock(return_value=[])

        get_details = Mock()
        get_details.side_effect = [
            make_new_beneficiary_application_details(123, 'closed'),
            make_new_beneficiary_application_details(456, 'closed'),
            make_new_beneficiary_application_details(789, 'closed')
        ]

        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=False)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created
        )

        # then
        assert get_all_application_ids.call_count == 1
        get_all_application_ids.assert_called_with(6712558, ANY, ANY)

    @patch('scripts.beneficiary.remote_import.process_beneficiary_application')
    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v2': '6712558'})
    def test_all_applications_are_processed_once(self, process_beneficiary_application):
        # given
        get_all_application_ids = Mock(return_value=[123, 456, 789])
        find_applications_ids_to_retry = Mock(return_value=[])

        get_details = Mock()
        get_details.side_effect = [
            make_new_beneficiary_application_details(123, 'closed'),
            make_new_beneficiary_application_details(456, 'closed'),
            make_new_beneficiary_application_details(789, 'closed')
        ]

        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=False)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created
        )

        # then
        assert process_beneficiary_application.call_count == 3

    @patch('scripts.beneficiary.remote_import.process_beneficiary_application')
    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v2': '6712558'})
    def test_applications_to_retry_are_processed(self, process_beneficiary_application):
        # given
        get_all_application_ids = Mock(return_value=[123])
        find_applications_ids_to_retry = Mock(return_value=[456, 789])

        get_details = Mock()
        get_details.side_effect = [
            make_new_beneficiary_application_details(123, 'closed'),
            make_new_beneficiary_application_details(456, 'closed'),
            make_new_beneficiary_application_details(789, 'closed')
        ]

        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=False)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created
        )

        # then
        assert process_beneficiary_application.call_count == 3

    @patch('scripts.beneficiary.remote_import.parse_beneficiary_information')
    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_ENROLLMENT_REPORT_RECIPIENTS': 'send@example.com'})
    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v2': '6712558'})
    @clean_database
    def test_an_error_status_is_saved_when_an_application_is_not_parsable(
            self,
            mocked_parse_beneficiary_information,
            app
    ):
        # given
        get_all_application_ids = Mock(return_value=[123])
        find_applications_ids_to_retry = Mock(return_value=[])

        get_details = Mock(side_effect=[make_new_beneficiary_application_details(123, 'closed')])
        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=False)
        mocked_parse_beneficiary_information.side_effect = [Exception()]

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created
        )

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.currentStatus == ImportStatus.ERROR
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.detail == 'Le dossier 123 contient des erreurs et a été ignoré - Procedure 6712558'

    @patch('scripts.beneficiary.remote_import.process_beneficiary_application')
    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v2': '6712558'})
    def test_application_with_known_application_id_are_not_processed(self,
                                                                     process_beneficiary_application
                                                                     ):
        # given
        get_all_application_ids = Mock(return_value=[123, 456])
        find_applications_ids_to_retry = Mock(return_value=[])

        get_details = Mock(return_value=make_new_beneficiary_application_details(123, 'closed'))
        user = UserSQLEntity()
        user.email = 'john.doe@example.com'
        has_already_been_imported = Mock(return_value=True)
        has_already_been_created = Mock(return_value=False)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created
        )

        # then
        process_beneficiary_application.assert_not_called()

    @patch('scripts.beneficiary.remote_import.process_beneficiary_application')
    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v2': '6712558'})
    @clean_database
    def test_application_with_known_email_are_saved_as_rejected(self,
                                                                process_beneficiary_application,
                                                                app):
        # given
        get_all_application_ids = Mock(return_value=[123])
        find_applications_ids_to_retry = Mock(return_value=[])

        get_details = Mock(return_value=make_new_beneficiary_application_details(123, 'closed'))
        user = UserSQLEntity()
        user.email = 'john.doe@example.com'
        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=True)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created
        )

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.currentStatus == ImportStatus.REJECTED
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.detail == 'Compte existant avec cet email'
        process_beneficiary_application.assert_not_called()

    @patch('scripts.beneficiary.remote_import.process_beneficiary_application')
    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_ENROLLMENT_PROCEDURE_ID_v2': '2567158'})
    @clean_database
    def test_beneficiary_is_created_with_procedure_id(
            self,
            process_beneficiary_application,
            app
    ):
        # given
        get_all_application_ids = Mock(return_value=[123])
        find_applications_ids_to_retry = Mock(return_value=[])

        get_details = Mock(side_effect=[make_new_beneficiary_application_details(123, 'closed')])
        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=False)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            get_all_applications_ids=get_all_application_ids,
            get_applications_ids_to_retry=find_applications_ids_to_retry,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_existing_user=has_already_been_created
        )

        # then
        process_beneficiary_application.assert_called_with(
            information={
                'last_name': 'Doe',
                'first_name': 'John',
                'civility': 'Mme',
                'email': 'john.doe@test.com',
                'application_id': 123,
                'department': '67',
                'phone': '0123456789',
                'birth_date': datetime(2000, 5, 1, 0, 0),
                'activity': 'Étudiant',
                'postal_code': '67200'
            },
            error_messages=[],
            new_beneficiaries=[],
            retry_ids=[],
            procedure_id=2567158
        )


class ProcessBeneficiaryApplicationTest:
    @clean_database
    def test_new_beneficiaries_are_recorded_with_deposit(self, app):
        # given
        app.mailjet_client = Mock(spec=Client)
        app.mailjet_client.send = Mock()
        information = {
            'department': '93',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@example.com',
            'phone': '0612345678',
            'postal_code': '93130',
            'application_id': 123,
            'civility': 'Mme',
            'activity': 'Étudiant'
        }

        # when
        remote_import.process_beneficiary_application(information, error_messages=[], new_beneficiaries=[],
                                                      retry_ids=[], procedure_id=123456)

        # then
        first = UserSQLEntity.query.first()
        assert first.email == 'jane.doe@example.com'
        assert first.wallet_balance == 500
        assert first.civility == 'Mme'
        assert first.activity == 'Étudiant'

    @clean_database
    def test_an_import_status_is_saved_if_beneficiary_is_created(self, app):
        # given
        app.mailjet_client = Mock(spec=Client)
        app.mailjet_client.send = Mock()
        information = {
            'department': '93',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@example.com',
            'phone': '0612345678',
            'postal_code': '93130',
            'application_id': 123,
            'civility': 'Mme',
            'activity': 'Étudiant'
        }

        # when
        remote_import.process_beneficiary_application(information, error_messages=[], new_beneficiaries=[],
                                                      retry_ids=[], procedure_id=123456)

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.beneficiary.email == 'jane.doe@example.com'
        assert beneficiary_import.currentStatus == ImportStatus.CREATED
        assert beneficiary_import.applicationId == 123

    @patch('scripts.beneficiary.remote_import.create_beneficiary_from_application')
    @patch('scripts.beneficiary.remote_import.repository')
    @patch('scripts.beneficiary.remote_import.send_activation_email')
    @clean_database
    def test_account_activation_email_is_sent(self, send_activation_email, mock_repository,
                                              create_beneficiary_from_application, app):
        # given
        information = {
            'department': '93',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@example.com',
            'phone': '0612345678',
            'postal_code': '93130',
            'application_id': 123,
            'civility': 'Mme',
            'activity': 'Étudiant'
        }

        create_beneficiary_from_application.return_value = create_user()

        # when
        remote_import.process_beneficiary_application(information, error_messages=[], new_beneficiaries=[],
                                                      retry_ids=[], procedure_id=123456)

        # then
        send_activation_email.assert_called()

    @patch('scripts.beneficiary.remote_import.create_beneficiary_from_application')
    @patch('scripts.beneficiary.remote_import.repository')
    @patch('scripts.beneficiary.remote_import.send_activation_email')
    @clean_database
    def test_error_is_collected_if_beneficiary_could_not_be_saved(self,
                                                                  send_activation_email, mock_repository,
                                                                  create_beneficiary_from_application, app):
        # given
        information = {
            'department': '93',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@example.com',
            'phone': '0612345678',
            'postal_code': '93130',
            'application_id': 123,
            'civility': 'Mme',
            'activity': 'Étudiant'
        }
        create_beneficiary_from_application.side_effect = [UserSQLEntity()]
        mock_repository.save.side_effect = [ApiErrors({'postalCode': ['baaaaad value']})]
        new_beneficiaries = []
        error_messages = []

        # when
        remote_import.process_beneficiary_application(information, error_messages, new_beneficiaries, retry_ids=[],
                                                      procedure_id=123456)

        # then
        send_activation_email.assert_not_called()
        assert error_messages == ['{\n  "postalCode": [\n    "baaaaad value"\n  ]\n}']
        assert not new_beneficiaries

    @patch('scripts.beneficiary.remote_import.repository')
    @patch('scripts.beneficiary.remote_import.send_activation_email')
    @clean_database
    def test_beneficiary_is_not_created_if_duplicates_are_found(self, send_activation_email, mock_repository,
                                                                app):
        # given
        information = {
            'department': '93',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@example.com',
            'phone': '0612345678',
            'postal_code': '93130',
            'application_id': 123,
            'civility': 'Mme',
            'activity': 'Étudiant'
        }
        existing_user = create_user(date_of_birth=datetime(2000, 5, 1), first_name='Jane', last_name='Doe')
        repository.save(existing_user)

        # when
        remote_import.process_beneficiary_application(information, error_messages=[], new_beneficiaries=[],
                                                      retry_ids=[], procedure_id=123456)

        # then
        send_activation_email.assert_not_called()
        mock_repository.save.assert_not_called()
        beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=123).first()
        assert beneficiary_import.currentStatus == ImportStatus.DUPLICATE

    @patch('scripts.beneficiary.remote_import.send_activation_email')
    @clean_database
    def test_beneficiary_is_created_if_duplicates_are_found_but_id_is_in_retry_list(self, send_activation_email, app):
        # given
        information = {
            'department': '93',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@example.com',
            'phone': '0612345678',
            'postal_code': '93130',
            'application_id': 123,
            'civility': 'Mme',
            'activity': 'Étudiant'
        }
        existing_user = create_user(date_of_birth=datetime(2000, 5, 1), first_name='Jane', last_name='Doe')
        repository.save(existing_user)
        retry_ids = [123]

        # when
        remote_import.process_beneficiary_application(information, error_messages=[], new_beneficiaries=[],
                                                      retry_ids=retry_ids, procedure_id=123456)

        # then
        send_activation_email.assert_called()
        beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=123).first()
        assert beneficiary_import.currentStatus == ImportStatus.CREATED

    @patch('scripts.beneficiary.remote_import.get_beneficiary_duplicates')
    @clean_database
    def test_an_import_status_is_saved_if_beneficiary_is_a_duplicate(self, mock_get_beneficiary_duplicates, app):
        # given
        information = {
            'department': '93',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@example.com',
            'phone': '0612345678',
            'postal_code': '93130',
            'application_id': 123,
            'civility': 'Mme',
            'activity': 'Étudiant'
        }
        mock_get_beneficiary_duplicates.return_value = [create_user(idx=11), create_user(idx=22)]

        # when
        remote_import.process_beneficiary_application(information, error_messages=[], new_beneficiaries=[],
                                                      retry_ids=[], procedure_id=123456)

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.currentStatus == ImportStatus.DUPLICATE
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.detail == "Utilisateur en doublon : 11, 22"


class ParseBeneficiaryInformationTest:
    def test_personal_information_of_beneficiary_are_parsed_from_application_detail(self):
        # when
        information = parse_beneficiary_information(APPLICATION_DETAIL_STANDARD_RESPONSE)

        # then
        assert information['last_name'] == 'Doe'
        assert information['first_name'] == 'John'
        assert information['birth_date'] == datetime(2000, 5, 1)
        assert information['civility'] == 'M.'
        assert information['email'] == 'john.doe@test.com'
        assert information['phone'] == '0123456789'
        assert information['postal_code'] == '93130'
        assert information['application_id'] == 123

    def test_handles_two_digits_department_code(self):
        # given
        application_detail = make_new_beneficiary_application_details(1, 'closed', department_code='67 - Bas-Rhin')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['department'] == '67'

    def test_handles_three_digits_department_code(self):
        # given
        application_detail = make_new_beneficiary_application_details(1, 'closed', department_code='973 - Guyane')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['department'] == '973'

    def test_handles_uppercased_mixed_digits_and_letter_department_code(self):
        # given
        application_detail = make_new_beneficiary_application_details(1, 'closed', department_code='2B - Haute-Corse')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['department'] == '2B'

    def test_handles_lowercased_mixed_digits_and_letter_department_code(self):
        # given
        application_detail = make_new_beneficiary_application_details(1, 'closed', department_code='2a - Haute-Corse')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['department'] == '2a'

    def test_handles_department_code_with_another_label(self):
        # given
        application_detail = make_new_beneficiary_application_details(1, 'closed', department_code='67 - Bas-Rhin')
        for field in application_detail['dossier']['champs']:
            label = field['type_de_champ']['libelle']
            if label == 'Veuillez indiquer votre département':
                field['type_de_champ']['libelle'] = "Veuillez indiquer votre département de résidence"

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['department'] == '67'

    def test_handles_postal_codes_wrapped_with_spaces(self):
        # given
        application_detail = make_new_beneficiary_application_details(1, 'closed', postal_code='  93130  ')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['postal_code'] == '93130'

    def test_handles_postal_codes_containing_spaces(self):
        # given
        application_detail = make_new_beneficiary_application_details(1, 'closed', postal_code='67 200')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['postal_code'] == '67200'

    def test_handles_postal_codes_containing_city_name(self):
        # given
        application_detail = make_new_beneficiary_application_details(1, 'closed', postal_code='67 200 Strasbourg ')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['postal_code'] == '67200'

    def test_handles_civility_parsing(self):
        # given
        application_detail = make_new_beneficiary_application_details(1, 'closed', civility='M.')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['civility'] == 'M.'

    def test_handles_activity_parsing(self):
        # given
        application_detail = make_new_beneficiary_application_details(1, 'closed')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['activity'] == 'Étudiant'

    def test_handles_activity_even_if_activity_is_not_filled(self):
        # given
        application_detail = make_new_beneficiary_application_details(1, 'closed', activity=None)

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['activity'] is None
