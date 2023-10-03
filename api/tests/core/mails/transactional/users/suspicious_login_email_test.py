from datetime import datetime
from urllib.parse import urlencode

from freezegun import freeze_time
import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.suspicious_login_email import get_suspicious_login_email_data
from pcapi.core.mails.transactional.users.suspicious_login_email import send_suspicious_login_email
import pcapi.core.users.factories as users_factories
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
    account_suspension_token = "suspicious_login_email_token"

    def setup_method(self):
        self.user = users_factories.UserFactory()
        self.reset_password_token = users_factories.PasswordResetTokenFactory()
        self.ACCOUNT_SECURING_LINK = "https://passcultureapptestauto.page.link/?" + urlencode(
            {
                "link": f"https://webapp-v2.example.com/securisation-compte?token={self.account_suspension_token}&reset_password_token={self.reset_password_token.value}&reset_token_expiration_timestamp={int(self.reset_password_token.expirationDate.timestamp())}&"
                + urlencode({"email": self.user.email})
            }
        )

    def should_return_sendinblue_template_data(self):
        suspicious_email_data = get_suspicious_login_email_data(
            self.user, self.login_info, self.account_suspension_token, self.reset_password_token
        )

        assert suspicious_email_data.template == TransactionalEmail.SUSPICIOUS_LOGIN.value
        assert suspicious_email_data.params == {
            "LOCATION": "Paris",
            "SOURCE": "iPhone 13",
            "OS": "iOS",
            "LOGIN_DATE": "29/05/2023",
            "LOGIN_TIME": "19h05",
            "ACCOUNT_SECURING_LINK": self.ACCOUNT_SECURING_LINK,
        }

    def should_send_suspicious_login_email(self):
        send_suspicious_login_email(
            self.user, self.login_info, self.account_suspension_token, self.reset_password_token
        )

        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__
        assert mails_testing.outbox[0].sent_data["To"] == self.user.email
        assert mails_testing.outbox[0].sent_data["params"] == {
            "LOCATION": "Paris",
            "SOURCE": "iPhone 13",
            "OS": "iOS",
            "LOGIN_DATE": "29/05/2023",
            "LOGIN_TIME": "19h05",
            "ACCOUNT_SECURING_LINK": self.ACCOUNT_SECURING_LINK,
        }

    @freeze_time("2023-06-08 14:10:00")
    def should_send_suspicious_login_email_with_date_when_no_login_info(self):
        send_suspicious_login_email(
            self.user,
            login_info=None,
            account_suspension_token=self.account_suspension_token,
            reset_password_token=self.reset_password_token,
        )

        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__
        assert mails_testing.outbox[0].sent_data["To"] == self.user.email
        assert mails_testing.outbox[0].sent_data["params"] == {
            "LOGIN_DATE": "08/06/2023",
            "LOGIN_TIME": "16h10",
            "ACCOUNT_SECURING_LINK": self.ACCOUNT_SECURING_LINK,
        }

    def should_send_suspicious_login_email_for_user_living_in_domtom(self):
        self.user.departementCode = "987"
        send_suspicious_login_email(
            self.user, self.login_info, self.account_suspension_token, self.reset_password_token
        )

        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__
        assert mails_testing.outbox[0].sent_data["To"] == self.user.email
        assert mails_testing.outbox[0].sent_data["params"] == {
            "LOCATION": "Paris",
            "SOURCE": "iPhone 13",
            "OS": "iOS",
            "LOGIN_DATE": "29/05/2023",
            "LOGIN_TIME": "07h05",
            "ACCOUNT_SECURING_LINK": self.ACCOUNT_SECURING_LINK,
        }

    @freeze_time("2023-06-08 3:15:00")
    def should_send_suspicious_login_email_for_user_living_in_domtom_with_date_when_no_login_info(self):
        self.user.departementCode = "972"
        send_suspicious_login_email(
            self.user,
            login_info=None,
            account_suspension_token=self.account_suspension_token,
            reset_password_token=self.reset_password_token,
        )

        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__
        assert mails_testing.outbox[0].sent_data["To"] == self.user.email
        assert mails_testing.outbox[0].sent_data["params"] == {
            "LOGIN_DATE": "07/06/2023",
            "LOGIN_TIME": "23h15",
            "ACCOUNT_SECURING_LINK": self.ACCOUNT_SECURING_LINK,
        }
