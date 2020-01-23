from datetime import datetime
from unittest.mock import MagicMock

from freezegun import freeze_time

from models.db import db
from models.email import EmailStatus
from repository import repository
from scripts.send_remedial_emails import send_remedial_emails
from tests.conftest import clean_database, mocked_mail
from tests.model_creators.generic_creators import create_email


@clean_database
@freeze_time('2019-01-01 12:00:00')
@mocked_mail
def test_send_remedial_emails_sets_status_to_sent_and_datetime_to_now_only_to_emails_in_error_when_successfully_sent(
        app):
    # given
    email_content1 = {'Html-part': '<html><body></body></html>', 'To': ['recipient@email']}
    email1 = create_email(email_content1, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))
    email_content2 = {'Html-part': '<html><body>Hello</body></html>', 'To': ['recipient2@email']}
    email2 = create_email(email_content2, status='SENT', time=datetime(2018, 12, 1, 12, 0, 0))
    email_content3 = {'Html-part': '<html><body>Hello</body></html>', 'To': ['recipient2@email']}
    email3 = create_email(email_content3, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))
    repository.save(email1, email2, email3)
    mocked_response = MagicMock()
    mocked_response.status_code = 200
    app.mailjet_client.send.create.return_value = mocked_response

    # when
    send_remedial_emails()

    # then
    assert app.mailjet_client.send.create.call_count == 2
    db.session.refresh(email1)
    db.session.refresh(email2)
    db.session.refresh(email3)
    assert email1.status == EmailStatus.SENT
    assert email1.datetime == datetime(2019, 1, 1, 12, 0, 0)
    assert email2.datetime == datetime(2018, 12, 1, 12, 0, 0)
    assert email3.status == EmailStatus.SENT
    assert email3.datetime == datetime(2019, 1, 1, 12, 0, 0)


@clean_database
@freeze_time('2019-01-01 12:00:00')
@mocked_mail
def test_send_remedial_emails_does_not_change_email_when_unsuccessfully_sent_and_calls_mailing_api_once(app):
    # given
    email_content1 = {'Html-part': '<html><body></body></html>', 'To': ['recipient@email']}
    email1 = create_email(email_content1, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))
    email_content2 = {'Html-part': '<html><body>Hello</body></html>', 'To': ['recipient2@email']}
    email2 = create_email(email_content2, status='SENT', time=datetime(2018, 12, 1, 12, 0, 0))
    email_content3 = {'Html-part': '<html><body>Hello</body></html>', 'To': ['recipient2@email']}
    email3 = create_email(email_content3, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))
    repository.save(email1, email2, email3)
    mocked_response = MagicMock()
    mocked_response.status_code = 500
    app.mailjet_client.send.create.return_value = mocked_response

    # when
    send_remedial_emails()

    # then
    assert app.mailjet_client.send.create.call_count == 1
    db.session.refresh(email1)
    db.session.refresh(email2)
    db.session.refresh(email3)
    assert email1.status == EmailStatus.ERROR
    assert email1.datetime == datetime(2018, 12, 1, 12, 0, 0)
    assert email2.datetime == datetime(2018, 12, 1, 12, 0, 0)
    assert email3.status == EmailStatus.ERROR
    assert email3.datetime == datetime(2018, 12, 1, 12, 0, 0)
