from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from models import User
from scripts.beneficiary import remote_import
from scripts.beneficiary.remote_import import parse_beneficiary_information, process_beneficiary_application, \
    DuplicateBeneficiaryError
from tests.scripts.beneficiary.fixture import make_application_detail, \
    make_applications_list, APPLICATION_DETAIL_STANDARD_RESPONSE

NOW = datetime.utcnow()
datetime_pattern = '%Y-%m-%dT%H:%M:%SZ'
EIGHT_HOURS_AGO = (NOW - timedelta(hours=8)).strftime(datetime_pattern)
FOUR_HOURS_AGO = (NOW - timedelta(hours=4)).strftime(datetime_pattern)
TWO_DAYS_AGO = (NOW - timedelta(hours=48)).strftime(datetime_pattern)


@pytest.mark.standalone
class RunTest:
    @patch('scripts.beneficiary.remote_import.process_beneficiary_application')
    def test_only_closed_applications_are_processed(self, process_beneficiary_application):
        # given
        get_all_applications = Mock()
        get_all_applications.return_value = make_applications_list(
            [
                (123, 'closed', FOUR_HOURS_AGO),
                (456, 'initiated', EIGHT_HOURS_AGO),
                (789, 'closed', TWO_DAYS_AGO)
            ]
        )
        get_details = Mock()
        get_details.side_effect = [
            make_application_detail(123, 'closed'),
            make_application_detail(456, 'initiated'),
            make_application_detail(789, 'closed')
        ]

        # when
        remote_import.run(get_all_applications, get_details)

        # then
        assert process_beneficiary_application.call_count == 2


@pytest.mark.standalone
class ParseBeneficiaryInformationTest:
    def test_personal_information_of_beneficiary_are_parsed_from_application_detail(self):
        # when
        information = parse_beneficiary_information(APPLICATION_DETAIL_STANDARD_RESPONSE)

        # then
        assert information['department'] == '67'
        assert information['last_name'] == 'Doe'
        assert information['first_name'] == 'Jane'
        assert information['birth_date'] == datetime(2000, 5, 1)
        assert information['email'] == 'jane.doe@test.com'
        assert information['phone'] == '0612345678'
        assert information['postal_code'] == '67200'
        assert information['application_id'] == 123


@pytest.mark.standalone
class ProcessBeneficiaryApplicationTest:
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
        beneficiary = process_beneficiary_application(beneficiary_information, find_duplicate_users)

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

    def test_raise_an_error_with_duplicate_users_if_any_are_found(self):
        # given
        find_duplicate_users = Mock()
        find_duplicate_users.return_value = [
            User(), User()
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
            process_beneficiary_application(beneficiary_information, find_duplicate_users)

        # then
        assert e.value.message == '2 utilisateur(s) en doublon pour le dossier 123'
