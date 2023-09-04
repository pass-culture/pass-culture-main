from pcapi import settings
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.users.fraud_emails import _send_fraud_mail


class FraudEmailTest:
    def test_send_fraud_email(self):
        _send_fraud_mail("Subject", "Header", "Body")
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["To"] == settings.FRAUD_EMAIL_ADDRESS
        assert mails_testing.outbox[0].sent_data["subject"] == "Subject"
        assert "Header" in mails_testing.outbox[0].sent_data["html_content"]
        assert "Body" in mails_testing.outbox[0].sent_data["html_content"]
