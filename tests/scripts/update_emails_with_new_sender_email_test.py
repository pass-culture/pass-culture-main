from datetime import datetime

import pytest

from models import PcObject
from models.db import db
from scripts.update_emails_with_new_sender_email import update_emails_with_new_sender_email
from tests.conftest import clean_database
from tests.test_utils import create_email


@pytest.mark.standalone
class UpdateEmailsWithNewSenderEmailTest:
    @clean_database
    def test_update_emails_with_new_sender_email(self, app):
        # Given
        email_content1 = {
            'FromEmail': 'test1@email.fr',
            'FromName': 'Test From',
            'Subject': 'Test subject',
            'Text-Part': 'Hello world',
            'Html-part': '<html><body>Hello World</body></html>'
        }
        email_content2 = {
            'FromEmail': 'test2@email.fr',
            'FromName': 'Test From',
            'Subject': 'Test subject',
            'Text-Part': 'Hello world',
            'Html-part': '<html><body>Hello World</body></html>'
        }

        email1 = create_email(email_content1, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))
        email2 = create_email(email_content2, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))

        PcObject.check_and_save(email1, email2)

        # When
        update_emails_with_new_sender_email()

        # Then
        db.session.refresh(email1)
        db.session.refresh(email2)
        assert email1.content['FromEmail'] == 'support@passculture.app'
        assert email1.content['FromName'] == 'Test From'
        assert email1.content['Subject'] == 'Test subject'
        assert email1.content['Text-Part'] == 'Hello world'
        assert email1.content['Html-part'] == '<html><body>Hello World</body></html>'

        assert email2.content['FromEmail'] == 'support@passculture.app'
        assert email2.content['FromName'] == 'Test From'
        assert email2.content['Subject'] == 'Test subject'
        assert email2.content['Text-Part'] == 'Hello world'
        assert email2.content['Html-part'] == '<html><body>Hello World</body></html>'

    @clean_database
    def test_no_update_emails_with_new_sender_email_when_no_error_emails(self, app):
        # Given
        email_content1 = {
            'FromEmail': 'test1@email.fr',
            'FromName': 'Test From',
            'Subject': 'Test subject',
            'Text-Part': 'Hello world',
            'Html-part': '<html><body>Hello World</body></html>'
        }

        email1 = create_email(email_content1, status='SENT', time=datetime(2018, 12, 1, 12, 0, 0))

        PcObject.check_and_save(email1)

        # When
        update_emails_with_new_sender_email()

        # Then
        db.session.refresh(email1)
        assert email1.content['FromEmail'] == 'test1@email.fr'

    @clean_database
    def test_update_emails_with_new_sender_email_when_no_text_part(self, app):
        # Given
        email_content1 = {
            'FromEmail': 'test1@email.fr',
            'FromName': 'Test From',
            'Subject': 'Test subject',
            'Html-part': '<html><body>Hello World</body></html>'
        }

        email1 = create_email(email_content1, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))

        PcObject.check_and_save(email1)

        # When
        update_emails_with_new_sender_email()

        # Then
        db.session.refresh(email1)
        assert email1.content['FromEmail'] == 'support@passculture.app'

    @clean_database
    def test_update_emails_with_new_sender_email_when_no_html_part(self, app):
        # Given
        email_content1 = {
            'FromEmail': 'test1@email.fr',
            'FromName': 'Test From',
            'Subject': 'Test subject',
            'Text-Part': 'Hello world',
        }

        email1 = create_email(email_content1, status='ERROR', time=datetime(2018, 12, 1, 12, 0, 0))

        PcObject.check_and_save(email1)

        # When
        update_emails_with_new_sender_email()

        # Then
        db.session.refresh(email1)
        assert email1.content['FromEmail'] == 'support@passculture.app'
