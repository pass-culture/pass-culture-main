from dataclasses import asdict

import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.factories as users_factories
from pcapi.core import token as token_utils
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.users import constants
from pcapi.utils import date as date_utils
from pcapi.utils.date import get_date_formatted_for_email
from pcapi.utils.date import get_time_formatted_for_email
from pcapi.utils.date import utc_datetime_to_department_timezone


pytestmark = pytest.mark.usefixtures("db_session")


class BrevoSendCheckDoubleSignupProEmailTest:
    def test_send_email(self) -> None:
        user = users_factories.UserFactory()
        token = token_utils.Token.create(
            token_utils.TokenType.RESET_PASSWORD, constants.RESET_PASSWORD_TOKEN_LIFE_TIME, user.id
        )
        now = utc_datetime_to_department_timezone(date_utils.get_naive_utc_now(), user.departementCode)
        date = get_date_formatted_for_email(now)
        hour = get_time_formatted_for_email(now)
        transactional_mails.send_double_signup_to_pro_email(user, token)

        assert len(mails_testing.outbox) == 1

        reset_password_link = mails_testing.outbox[0]["params"]["LIEN_NOUVEAU_MDP"]
        assert token.encoded_token in reset_password_link
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.CHECK_DOUBLE_SIGNUP_TO_PRO.value)
        assert mails_testing.outbox[0]["To"] == user.email
        assert mails_testing.outbox[0]["params"]["DATE"] == date
        assert mails_testing.outbox[0]["params"]["HOUR"] == hour
