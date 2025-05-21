import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.factories as users_factories
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.birthday_to_newly_eligible_user import (
    send_birthday_age_17_email_to_newly_eligible_user,
)
from pcapi.core.mails.transactional.users.birthday_to_newly_eligible_user import (
    send_birthday_age_18_email_to_newly_eligible_user_v3,
)


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueSendNewlyEligibleUserEmailTest:
    def test_send_anniversary_age_17_email(self):
        user = users_factories.UserFactory(age=17)

        send_birthday_age_17_email_to_newly_eligible_user(user)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"] == {"DEPOSITS_COUNT": 0}
        assert (
            mails_testing.outbox[0]["template"]
            == TransactionalEmail.BIRTHDAY_AGE_17_TO_NEWLY_ELIGIBLE_USER.value.__dict__
        )

    def test_send_anniversary_age_18_email_v3(self):
        user = users_factories.UserFactory()

        send_birthday_age_18_email_to_newly_eligible_user_v3(user)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"] == {"CREDIT": None, "DEPOSITS_COUNT": 0}
        assert (
            mails_testing.outbox[0]["template"]
            == TransactionalEmail.BIRTHDAY_AGE_18_TO_NEWLY_ELIGIBLE_USER_V3.value.__dict__
        )
