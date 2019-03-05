import pytest
from unittest.mock import call

from models import PcObject
from scripts.send_remedial_emails import send_remedial_emails
from tests.conftest import mocked_mail, clean_database
from tests.test_utils import create_email_failed


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_send_remedial_emails_should_send_one_email_if_email_failed_has_one_entry_in_error(app):
    # given
    email = {'Html-part': '<html><body></body></html>', 'To': ['recipient@email']}
    email_failed = create_email_failed(email, status='ERROR')
    PcObject.check_and_save(email_failed)

    # when
    send_remedial_emails()

    # then
    app.mailjet_client.send.create.assert_called_once_with(data=email)


@pytest.mark.standalone
@mocked_mail
@clean_database
def test_send_remedial_emails_should_send_two_emails_if_email_failed_has_two_entry_in_error(app):
    # given
    email1 = {'Html-part': '<html><body></body></html>', 'To': ['recipient@email']}
    email_failed1 = create_email_failed(email1, status='ERROR')    # given
    email2 = {'Html-part': '<html><body>Hello</body></html>', 'To': ['recipient2@email']}
    email_failed2 = create_email_failed(email2, status='ERROR')
    PcObject.check_and_save(email_failed1, email_failed2)
    calls = [call(data=email1), call(data=email2)]

    # when
    send_remedial_emails()

    # then
    app.mailjet_client.send.create.assert_has_calls(calls)
