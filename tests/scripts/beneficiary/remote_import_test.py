from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, ANY

import pytest
from mailjet_rest import Client

from models import User, ApiErrors
from models.beneficiary_import import BeneficiaryImport, ImportStatus
from scripts.beneficiary import remote_import
from scripts.beneficiary.remote_import import parse_beneficiary_information, create_beneficiary_from_application, \
    DuplicateBeneficiaryError
from tests.conftest import clean_database
from tests.scripts.beneficiary.fixture import make_application_detail, \
    APPLICATION_DETAIL_STANDARD_RESPONSE
from tests.test_utils import create_user

NOW = datetime.utcnow()
datetime_pattern = '%Y-%m-%dT%H:%M:%S.%fZ'
EIGHT_HOURS_AGO = (NOW - timedelta(hours=8)).strftime(datetime_pattern)
FOUR_HOURS_AGO = (NOW - timedelta(hours=4)).strftime(datetime_pattern)
TWO_DAYS_AGO = (NOW - timedelta(hours=48)).strftime(datetime_pattern)
ONE_WEEK_AGO = NOW - timedelta(days=7)


class RunTest:
    @patch('scripts.beneficiary.remote_import.send_remote_beneficiaries_import_report_email')
    @patch('scripts.beneficiary.remote_import.process_beneficiary_application')
    def test_only_closed_applications_are_processed(self, process_beneficiary_application, send_report_email):
        # given
        get_all_application_ids = Mock(return_value=[123, 456, 789])
        get_details = Mock()
        get_details.side_effect = [
            make_application_detail(123, 'closed'),
            make_application_detail(456, 'closed'),
            make_application_detail(789, 'closed')
        ]

        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=False)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            get_all_applications_ids=get_all_application_ids,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_created=has_already_been_created
        )

        # then
        assert process_beneficiary_application.call_count == 3

    @patch('scripts.beneficiary.remote_import.send_remote_beneficiaries_import_report_email')
    @patch('scripts.beneficiary.remote_import.process_beneficiary_application')
    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_ENROLLMENT_REPORT_RECIPIENTS': 'send@report.to'})
    def test_a_report_email_is_sent(self, process_beneficiary_application, send_report_email):
        # given
        get_all_application_ids = Mock(return_value=[123])
        get_details = Mock(side_effect=[make_application_detail(123, 'closed')])
        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=False)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            get_all_applications_ids=get_all_application_ids,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_created=has_already_been_created
        )

        # then
        send_report_email.assert_called_with([], [], 'send@report.to', ANY)

    @patch('scripts.beneficiary.remote_import.send_remote_beneficiaries_import_report_email')
    @patch('scripts.beneficiary.remote_import.process_beneficiary_application')
    @patch('scripts.beneficiary.remote_import.parse_beneficiary_information')
    @patch.dict('os.environ', {'DEMARCHES_SIMPLIFIEES_ENROLLMENT_REPORT_RECIPIENTS': 'send@report.to'})
    def test_a_report_email_is_sent_even_if_an_application_is_not_parsable(
            self,
            parse_beneficiary_information,
            process_beneficiary_application,
            send_report_email
    ):
        # given
        get_all_application_ids = Mock(return_value=[123])
        get_details = Mock(side_effect=[make_application_detail(123, 'closed')])
        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=False)
        parse_beneficiary_information.side_effect = [Exception()]

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            get_all_applications_ids=get_all_application_ids,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_created=has_already_been_created
        )

        # then
        error = 'Le dossier 123 contient des erreurs et a été ignoré'
        send_report_email.assert_called_with([], [error], 'send@report.to', ANY)

    @patch('scripts.beneficiary.remote_import.send_remote_beneficiaries_import_report_email')
    @patch('scripts.beneficiary.remote_import.process_beneficiary_application')
    def test_application_with_known_demarche_simplifiee_application_id_are_not_processed(self,
                                                                                         process_beneficiary_application,
                                                                                         send_report_email):
        # given
        get_all_application_ids = Mock(return_value=[123, 456])
        get_details = Mock(return_value=make_application_detail(123, 'closed'))
        user = User()
        user.email = 'john.doe@test.com'
        user.demarcheSimplifieeApplicationId = 123
        has_already_been_imported = Mock()
        has_already_been_created = Mock(return_value=False)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            get_all_applications_ids=get_all_application_ids,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_created=has_already_been_created
        )

        # then
        process_beneficiary_application.assert_not_called()

    @patch('scripts.beneficiary.remote_import.send_remote_beneficiaries_import_report_email')
    @patch('scripts.beneficiary.remote_import.process_beneficiary_application')
    @clean_database
    def test_application_with_known_email_are_saved_as_rejected(self,
                                                                process_beneficiary_application,
                                                                send_report_email, app):
        # given
        get_all_application_ids = Mock(return_value=[123, 456])
        get_details = Mock(return_value=make_application_detail(123, 'closed'))
        user = User()
        user.email = 'john.doe@test.com'
        user.demarcheSimplifieeApplicationId = 123
        has_already_been_imported = Mock(return_value=False)
        has_already_been_created = Mock(return_value=True)

        # when
        remote_import.run(
            ONE_WEEK_AGO,
            get_all_applications_ids=get_all_application_ids,
            get_details=get_details,
            already_imported=has_already_been_imported,
            already_created=has_already_been_created
        )

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.status == ImportStatus.REJECTED
        assert beneficiary_import.demarcheSimplifieeApplicationId == 123
        assert beneficiary_import.detail == 'Compte existant avec cet email'
        process_beneficiary_application.assert_not_called()


class ProcessBeneficiaryApplicationTest:
    @clean_database
    def test_new_beneficiaries_are_recorded_with_deposit(self, app):
        # given
        app.mailjet_client = Mock(spec=Client)
        app.mailjet_client.send = Mock()
        information = {
            'department': '67',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@test.com',
            'phone': '0612345678',
            'postal_code': '67200',
            'application_id': 123
        }

        # when
        remote_import.process_beneficiary_application(information, [], [])

        # then
        first = User.query.first()
        assert first.email == 'jane.doe@test.com'
        assert first.wallet_balance == 500

    @clean_database
    def test_an_import_status_is_saved_if_beneficiary_is_created(self, app):
        # given
        app.mailjet_client = Mock(spec=Client)
        app.mailjet_client.send = Mock()
        information = {
            'department': '67',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@test.com',
            'phone': '0612345678',
            'postal_code': '67200',
            'application_id': 123
        }

        # when
        remote_import.process_beneficiary_application(information, [], [])

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.beneficiary.email == 'jane.doe@test.com'
        assert beneficiary_import.status == ImportStatus.CREATED
        assert beneficiary_import.demarcheSimplifieeApplicationId == 123

    @patch('scripts.beneficiary.remote_import.create_beneficiary_from_application')
    @patch('scripts.beneficiary.remote_import.PcObject')
    @patch('scripts.beneficiary.remote_import.send_activation_notification_email')
    def test_account_activation_email_is_sent(self, send_activation_notification_email, PcObject,
                                              create_beneficiary_from_application):
        # given
        information = {
            'department': '67',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@test.com',
            'phone': '0612345678',
            'postal_code': '67200',
            'application_id': 123
        }

        create_beneficiary_from_application.return_value = create_user()

        # when
        remote_import.process_beneficiary_application(information, [], [])

        # then
        send_activation_notification_email.assert_called()

    @patch('scripts.beneficiary.remote_import.create_beneficiary_from_application')
    @patch('scripts.beneficiary.remote_import.PcObject')
    @patch('scripts.beneficiary.remote_import.send_activation_notification_email')
    def test_error_is_collected_if_beneficiary_could_not_be_saved(self,
                                                                  send_activation_notification_email, PcObject,
                                                                  create_beneficiary_from_application):
        # given
        information = {
            'department': '67',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@test.com',
            'phone': '0612345678',
            'postal_code': '67200',
            'application_id': 123
        }
        create_beneficiary_from_application.side_effect = [User()]
        PcObject.save.side_effect = [ApiErrors({'postalCode': ['baaaaad value']})]
        new_beneficiaries = []
        error_messages = []

        # when
        remote_import.process_beneficiary_application(information, error_messages, new_beneficiaries)

        # then
        send_activation_notification_email.assert_not_called()
        assert error_messages == ['{\n  "postalCode": [\n    "baaaaad value"\n  ]\n}']
        assert not new_beneficiaries

    @patch('scripts.beneficiary.remote_import.create_beneficiary_from_application')
    @patch('scripts.beneficiary.remote_import.PcObject')
    @patch('scripts.beneficiary.remote_import.send_activation_notification_email')
    def test_beneficiary_is_not_created_if_duplicates_are_found(self,
                                                                send_activation_notification_email, PcObject,
                                                                create_beneficiary_from_application):
        # given
        information = {
            'department': '67',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@test.com',
            'phone': '0612345678',
            'postal_code': '67200',
            'application_id': 123
        }
        create_beneficiary_from_application.side_effect = DuplicateBeneficiaryError(123, [User()])

        # when
        remote_import.process_beneficiary_application(information, [], [])

        # then
        send_activation_notification_email.assert_not_called()
        PcObject.assert_not_called()

    @clean_database
    def test_an_import_status_is_saved_if_beneficiary_is_a_duplicate(self, app):
        # given
        information = {
            'department': '67',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@test.com',
            'phone': '0612345678',
            'postal_code': '67200',
            'application_id': 123
        }
        duplicates = [create_user(idx=11), create_user(idx=22)]
        mocked_query = Mock(side_effect=DuplicateBeneficiaryError(123, duplicates))

        # when
        remote_import.process_beneficiary_application(information, [], [], find_duplicate_users=mocked_query)

        # then
        beneficiary_import = BeneficiaryImport.query.first()
        assert beneficiary_import.status == ImportStatus.DUPLICATE
        assert beneficiary_import.demarcheSimplifieeApplicationId == 123
        assert beneficiary_import.detail == "Utilisateur en doublon : 11, 22"


class ParseBeneficiaryInformationTest:
    def test_personal_information_of_beneficiary_are_parsed_from_application_detail(self):
        # when
        information = parse_beneficiary_information(APPLICATION_DETAIL_STANDARD_RESPONSE)

        # then
        assert information['last_name'] == 'Doe'
        assert information['first_name'] == 'Jane'
        assert information['birth_date'] == datetime(2000, 5, 1)
        assert information['email'] == 'jane.doe@test.com'
        assert information['phone'] == '0123456789'
        assert information['postal_code'] == '67200'
        assert information['application_id'] == 123

    def test_handles_two_digits_department_code(self):
        # given
        application_detail = make_application_detail(1, 'closed', department_code='67 - Bas-Rhin')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['department'] == '67'

    def test_handles_postal_codes_wrapped_with_spaces(self):
        # given
        application_detail = make_application_detail(1, 'closed', postal_code='  67200  ')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['postal_code'] == '67200'

    def test_handles_postal_codes_containing_spaces(self):
        # given
        application_detail = make_application_detail(1, 'closed', postal_code='67 200')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['postal_code'] == '67200'

    def test_handles_postal_codes_containing_city_name(self):
        # given
        application_detail = make_application_detail(1, 'closed', postal_code='67 200 Strasbourg ')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['postal_code'] == '67200'

    def test_handles_three_digits_department_code(self):
        # given
        application_detail = make_application_detail(1, 'closed', department_code='973 - Guyane')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['department'] == '973'

    def test_handles_uppercased_mixed_digits_and_letter_department_code(self):
        # given
        application_detail = make_application_detail(1, 'closed', department_code='2B - Haute-Corse')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['department'] == '2B'

    def test_handles_lowercased_mixed_digits_and_letter_department_code(self):
        # given
        application_detail = make_application_detail(1, 'closed', department_code='2a - Haute-Corse')

        # when
        information = parse_beneficiary_information(application_detail)

        # then
        assert information['department'] == '2a'


class CreateBeneficiaryFromApplicationTest:
    def test_return_newly_created_user_if_no_duplicate_are_found(self):
        # given
        THIRTY_DAYS_FROM_NOW = (datetime.utcnow() + timedelta(days=30)).date()
        find_duplicate_users = Mock()
        find_duplicate_users.return_value = []

        beneficiary_information = {
            'department': '67',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@test.com',
            'phone': '0612345678',
            'postal_code': '67200',
            'application_id': 123
        }

        # when
        beneficiary = create_beneficiary_from_application(beneficiary_information, find_duplicate_users)

        # then
        assert beneficiary.lastName == 'Doe'
        assert beneficiary.firstName == 'Jane'
        assert beneficiary.publicName == 'Jane Doe'
        assert beneficiary.email == 'jane.doe@test.com'
        assert beneficiary.phoneNumber == '0612345678'
        assert beneficiary.departementCode == '67'
        assert beneficiary.postalCode == '67200'
        assert beneficiary.dateOfBirth == datetime(2000, 5, 1)
        assert beneficiary.canBookFreeOffers == True
        assert beneficiary.isAdmin == False
        assert beneficiary.password is not None
        assert beneficiary.resetPasswordToken is not None
        assert beneficiary.resetPasswordTokenValidityLimit.date() == THIRTY_DAYS_FROM_NOW

    def test_a_deposit_is_made_for_the_new_beneficiary(self):
        # given
        find_duplicate_users = Mock()
        find_duplicate_users.return_value = []

        beneficiary_information = {
            'department': '67',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@test.com',
            'phone': '0612345678',
            'postal_code': '67200',
            'application_id': 123
        }
        # when
        beneficiary = create_beneficiary_from_application(beneficiary_information, find_duplicate_users)

        # then
        assert len(beneficiary.deposits) == 1
        assert beneficiary.deposits[0].amount == Decimal(500)
        assert beneficiary.deposits[0].source == 'démarches simplifiées dossier [123]'

    def test_raise_an_error_with_duplicate_users_if_any_are_found(self):
        # given
        user1 = User()
        user1.id = 123
        user2 = User()
        user2.id = 456
        find_duplicate_users = Mock()
        find_duplicate_users.return_value = [
            user1, user2
        ]
        beneficiary_information = {
            'department': '67',
            'last_name': 'Doe',
            'first_name': 'Jane',
            'birth_date': datetime(2000, 5, 1),
            'email': 'jane.doe@test.com',
            'phone': '0612345678',
            'postal_code': '67200',
            'application_id': 123
        }
        # when
        with pytest.raises(DuplicateBeneficiaryError) as e:
            create_beneficiary_from_application(beneficiary_information, find_duplicate_users)

        # then
        assert e.value.message == '2 utilisateur(s) en doublons (123, 456) pour le dossier 123'
