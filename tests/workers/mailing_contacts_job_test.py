import datetime
from unittest import mock

from requests import Response

from pcapi.workers.mailing_contacts_job import mailing_contacts_job


def _make_response(status_code):
    response = Response()
    response.status_code = status_code
    return response


@mock.patch("pcapi.core.mails.create_contact", return_value=_make_response(201))
@mock.patch("pcapi.core.mails.update_contact", return_value=_make_response(200))
@mock.patch("pcapi.core.mails.add_contact_to_list", return_value=_make_response(201))
def test_calls_use_case(mocked_add_contact_to_list, mocked_update_contact, mocked_create_contact):
    # Given
    email = "contact@example.com"
    birth_date = "2003-01-01"
    department = "93800"

    # When
    mailing_contacts_job(email, birth_date, department)

    # Then
    mocked_create_contact.assert_called_once_with(email)
    mocked_update_contact.assert_called_once_with(email, birth_date=datetime.date(2003, 1, 1), department=department)
    mocked_add_contact_to_list(email, 10210094)
