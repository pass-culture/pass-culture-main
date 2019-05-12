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
        assert email1.content['FromEmail'] == 'test1@passculture.app'
        assert email2.content['FromEmail'] == 'test2@passculture.app'
