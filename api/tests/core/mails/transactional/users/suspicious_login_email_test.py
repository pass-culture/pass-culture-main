from datetime import datetime

from freezegun import freeze_time
import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.suspicious_login_email import get_suspicious_login_email_data
from pcapi.core.mails.transactional.users.suspicious_login_email import send_suspicious_login_email
from pcapi.core.users.models import LoginDeviceHistory


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueSuspiciousLoginEmailTest:
    login_info = LoginDeviceHistory(
        deviceId="2E429592-2446-425F-9A62-D6983F375B3B",
        source="iPhone 13",
        os="iOS",
        location="Paris",
        dateCreated=datetime(2023, 5, 29, 17, 5, 0),
    )
    token = "suspicious_login_email_token"
    ACCOUNT_SECURING_LINK = f"https://passcultureapptestauto.page.link/?link=https%3A%2F%2Fwebapp-v2.example.com%2Fsecurisation-compte%3Ftoken%3D{token}"

    def test_should_return_sendinblue_template_data(self):
        suspicious_email_data = get_suspicious_login_email_data(
            self.login_info,
            self.token,
        )

        assert suspicious_email_data.template == TransactionalEmail.SUSPICIOUS_LOGIN.value
        assert suspicious_email_data.params == {
            "LOCATION": "Paris",
            "SOURCE": "iPhone 13",
            "OS": "iOS",
            "LOGIN_DATE": "29/05/2023",
            "LOGIN_TIME": "17h05",
            "ACCOUNT_SECURING_LINK": self.ACCOUNT_SECURING_LINK,
        }

    def test_should_send_suspicious_login_email(self):
        email = "123@test.com"
        send_suspicious_login_email(email, self.login_info, self.token)

        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__
        assert mails_testing.outbox[0].sent_data["To"] == email
        assert mails_testing.outbox[0].sent_data["params"] == {
            "LOCATION": "Paris",
            "SOURCE": "iPhone 13",
            "OS": "iOS",
            "LOGIN_DATE": "29/05/2023",
            "LOGIN_TIME": "17h05",
            "ACCOUNT_SECURING_LINK": self.ACCOUNT_SECURING_LINK,
        }

    @freeze_time("2023-05-29 17:05:00")
    def test_should_send_suspicious_login_email_with_date_when_no_login_info(self):
        email = "123@test.com"
        send_suspicious_login_email(email, login_info=None, token=self.token)

        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__
        assert mails_testing.outbox[0].sent_data["To"] == email
        assert mails_testing.outbox[0].sent_data["params"] == {
            "LOGIN_DATE": "29/05/2023",
            "LOGIN_TIME": "17h05",
            "ACCOUNT_SECURING_LINK": self.ACCOUNT_SECURING_LINK,
        }
