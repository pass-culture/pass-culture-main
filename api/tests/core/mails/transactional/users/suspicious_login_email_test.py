from datetime import datetime
from unittest import mock
from urllib.parse import urlencode

import fakeredis
import pytest
import time_machine

import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.factories as users_factories
from pcapi.core import token as token_utils
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.suspicious_login_email import get_suspicious_login_email_data
from pcapi.core.mails.transactional.users.suspicious_login_email import send_suspicious_login_email
from pcapi.core.users import constants
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
    mock_redis_client = fakeredis.FakeStrictRedis()

    def setup_method(self):
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            self.user = users_factories.UserFactory()
            current_time = datetime.utcnow()
            with time_machine.travel(current_time):
                self.account_suspension_token = token_utils.Token.create(
                    token_utils.TokenType.SUSPENSION_SUSPICIOUS_LOGIN,
                    constants.SUSPICIOUS_LOGIN_EMAIL_TOKEN_LIFE_TIME,
                    self.user.id,
                )
                self.reset_password_token = token_utils.Token.create(
                    token_utils.TokenType.RESET_PASSWORD, constants.RESET_PASSWORD_TOKEN_LIFE_TIME, self.user.id
                )

    def should_return_sendinblue_template_data(self):
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            suspicious_email_data = get_suspicious_login_email_data(
                self.user, self.login_info, self.account_suspension_token, self.reset_password_token
            )

            assert suspicious_email_data.template == TransactionalEmail.SUSPICIOUS_LOGIN.value
            assert suspicious_email_data.params["LOCATION"] == "Paris"
            assert suspicious_email_data.params["SOURCE"] == "iPhone 13"
            assert suspicious_email_data.params["OS"] == "iOS"
            assert suspicious_email_data.params["LOGIN_DATE"] == "29/05/2023"
            assert suspicious_email_data.params["LOGIN_TIME"] == "19h05"

    def should_return_sendinblue_template_data_account_securing_link(self):
        reset_password_token = token_utils.Token.create(
            token_utils.TokenType.RESET_PASSWORD, constants.RESET_PASSWORD_TOKEN_LIFE_TIME, self.user.id
        )

        ACCOUNT_SECURING_LINK = "https://passcultureapptestauto.page.link/?" + urlencode(
            {
                "link": f"https://webapp-v2.example.com/securisation-compte?token={self.account_suspension_token.encoded_token}&reset_password_token={reset_password_token.encoded_token}&reset_token_expiration_timestamp={int(reset_password_token.get_expiration_date_from_token().timestamp())}&"
                + urlencode({"email": self.user.email})
            }
        )
        suspicious_email_data = get_suspicious_login_email_data(
            self.user, self.login_info, self.account_suspension_token, reset_password_token
        )
        assert suspicious_email_data.params["ACCOUNT_SECURING_LINK"] == ACCOUNT_SECURING_LINK

    def should_send_suspicious_login_email(self):
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            send_suspicious_login_email(
                self.user, self.login_info, self.account_suspension_token, self.reset_password_token
            )

            assert mails_testing.outbox[0]["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__
            assert mails_testing.outbox[0]["To"] == self.user.email
            assert mails_testing.outbox[0]["params"]["LOCATION"] == "Paris"
            assert mails_testing.outbox[0]["params"]["SOURCE"] == "iPhone 13"
            assert mails_testing.outbox[0]["params"]["OS"] == "iOS"
            assert mails_testing.outbox[0]["params"]["LOGIN_DATE"] == "29/05/2023"
            assert mails_testing.outbox[0]["params"]["LOGIN_TIME"] == "19h05"

    def should_send_suspicious_login_email_account_securing_link(self):
        reset_password_token = token_utils.Token.create(
            token_utils.TokenType.RESET_PASSWORD, constants.RESET_PASSWORD_TOKEN_LIFE_TIME, self.user.id
        )

        ACCOUNT_SECURING_LINK = "https://passcultureapptestauto.page.link/?" + urlencode(
            {
                "link": f"https://webapp-v2.example.com/securisation-compte?token={self.account_suspension_token.encoded_token}&reset_password_token={reset_password_token.encoded_token}&reset_token_expiration_timestamp={int(reset_password_token.get_expiration_date_from_token().timestamp())}&"
                + urlencode({"email": self.user.email})
            }
        )
        send_suspicious_login_email(self.user, self.login_info, self.account_suspension_token, reset_password_token)
        assert mails_testing.outbox[0]["params"]["ACCOUNT_SECURING_LINK"] == ACCOUNT_SECURING_LINK

    @time_machine.travel("2023-06-08 14:10:00")
    def should_send_suspicious_login_email_with_date_when_no_login_info(self):
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            send_suspicious_login_email(
                self.user,
                login_info=None,
                account_suspension_token=self.account_suspension_token,
                reset_password_token=self.reset_password_token,
            )

            assert mails_testing.outbox[0]["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__
            assert mails_testing.outbox[0]["To"] == self.user.email
            assert mails_testing.outbox[0]["params"]["LOGIN_DATE"] == "08/06/2023"
            assert mails_testing.outbox[0]["params"]["LOGIN_TIME"] == "16h10"

    def should_send_suspicious_login_email_for_user_living_in_domtom(self):
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            self.user.departementCode = "987"
            send_suspicious_login_email(
                self.user, self.login_info, self.account_suspension_token, self.reset_password_token
            )

            assert mails_testing.outbox[0]["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__
            assert mails_testing.outbox[0]["To"] == self.user.email
            assert mails_testing.outbox[0]["params"]["LOCATION"] == "Paris"
            assert mails_testing.outbox[0]["params"]["SOURCE"] == "iPhone 13"
            assert mails_testing.outbox[0]["params"]["OS"] == "iOS"
            assert mails_testing.outbox[0]["params"]["LOGIN_DATE"] == "29/05/2023"
            assert mails_testing.outbox[0]["params"]["LOGIN_TIME"] == "07h05"

    @time_machine.travel("2023-06-08 3:15:00")
    def should_send_suspicious_login_email_for_user_living_in_domtom_with_date_when_no_login_info(self):
        with mock.patch("flask.current_app.redis_client", self.mock_redis_client):
            self.user.departementCode = "972"
            send_suspicious_login_email(
                self.user,
                login_info=None,
                account_suspension_token=self.account_suspension_token,
                reset_password_token=self.reset_password_token,
            )

            assert mails_testing.outbox[0]["template"] == TransactionalEmail.SUSPICIOUS_LOGIN.value.__dict__
            assert mails_testing.outbox[0]["To"] == self.user.email
            assert mails_testing.outbox[0]["params"]["LOGIN_DATE"] == "07/06/2023"
            assert mails_testing.outbox[0]["params"]["LOGIN_TIME"] == "23h15"
