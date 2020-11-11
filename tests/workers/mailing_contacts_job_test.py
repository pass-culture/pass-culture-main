from unittest.mock import MagicMock

from pcapi.infrastructure.container import add_contact_in_eligibility_list
from pcapi.workers.mailing_contacts_job import mailing_contacts_job


def test_calls_use_case():
    # Given
    add_contact_in_eligibility_list.execute = MagicMock()
    contact_email = "passculture@example.com"
    contact_date_of_birth = "2003-01-01"
    contact_department_code = "93800"

    # When
    mailing_contacts_job(contact_email, contact_date_of_birth, contact_department_code)

    # Then
    add_contact_in_eligibility_list.execute.assert_called_once_with(
        contact_email, contact_date_of_birth, contact_department_code
    )
