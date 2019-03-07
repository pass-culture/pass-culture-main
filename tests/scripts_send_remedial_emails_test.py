from datetime import datetime

import pytest
from freezegun import freeze_time
from unittest.mock import call, patch, MagicMock

from models import PcObject
from models.db import db
from scripts.send_remedial_emails import send_remedial_emails
from tests.conftest import clean_database, mocked_mail
from tests.test_utils import create_email


@pytest.mark.standalone
@clean_database
@freeze_time('2019-01-01 12:00:00')
@mocked_mail
def test_send_remedial_emails_sets_status_to_sent_and_datetime_to_now_only_to_emails_in_error_when_successfully_sent(app):
    # given
    email_content1 = {'Html-part': '<html><body></body></html>', 'To': ['recipient@email']}
    email1 = create_email(email_content1, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))
    email_content2 = {'Html-part': '<html><body>Hello</body></html>', 'To': ['recipient2@email']}
    email2 = create_email(email_content2, status='SENT', time=datetime(2018, 12, 1, 12, 0, 0))
    email_content3 = {'Html-part': '<html><body>Hello</body></html>', 'To': ['recipient2@email']}
    email3 = create_email(email_content3, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))
    PcObject.check_and_save(email1, email2, email3)
    mocked_response = MagicMock()
    mocked_response.status_code = 200
    app.mailjet_client.send.create.return_value = mocked_response

    # when
    send_remedial_emails()

    # then
    db.session.refresh(email1)
    db.session.refresh(email2)
    db.session.refresh(email3)
    assert email1.status == 'SENT'
    assert email1.datetime == datetime(2019, 1, 1, 12, 0, 0)
    assert email2.datetime == datetime(2018, 12, 1, 12, 0, 0)
    assert email3.status == 'SENT'
    assert email3.datetime == datetime(2019, 1, 1, 12, 0, 0)


@pytest.mark.standalone
@clean_database
@freeze_time('2019-01-01 12:00:00')
@mocked_mail
def test_send_remedial_emails_does_not_change_email_when_unsuccessfully_sent(app):
    # given
    email_content1 = {'Html-part': '<html><body></body></html>', 'To': ['recipient@email']}
    email1 = create_email(email_content1, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))
    email_content2 = {'Html-part': '<html><body>Hello</body></html>', 'To': ['recipient2@email']}
    email2 = create_email(email_content2, status='SENT', time=datetime(2018, 12, 1, 12, 0, 0))
    email_content3 = {'Html-part': '<html><body>Hello</body></html>', 'To': ['recipient2@email']}
    email3 = create_email(email_content3, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))
    PcObject.check_and_save(email1, email2, email3)
    mocked_response = MagicMock()
    mocked_response.status_code = 500
    app.mailjet_client.send.create.return_value = mocked_response

    # when
    send_remedial_emails()

    # then
    db.session.refresh(email1)
    db.session.refresh(email2)
    db.session.refresh(email3)
    assert email1.status == 'ERROR'
    assert email1.datetime == datetime(2018, 12, 1, 12, 0, 0)
    assert email2.datetime == datetime(2018, 12, 1, 12, 0, 0)
    assert email3.status == 'ERROR'
    assert email3.datetime == datetime(2018, 12, 1, 12, 0, 0)
