from unittest.mock import patch

from workers.mailing_contacts_job import mailing_contacts_job


@patch('workers.mailing_contacts_job.add_contact_in_eligibility_list.execute')
def test_calls_use_case(mocked_add_contact_in_eligibility_list_use_case):
    # Given
    contact_email= 'passculture@example.com'
    contact_date_of_birth= '01/01/2003'
    contact_department_code = '93800'

    # When
    mailing_contacts_job(contact_email, contact_date_of_birth, contact_department_code)

    # Then
    mocked_add_contact_in_eligibility_list_use_case.assert_called_once_with(contact_email, contact_date_of_birth, contact_department_code)
