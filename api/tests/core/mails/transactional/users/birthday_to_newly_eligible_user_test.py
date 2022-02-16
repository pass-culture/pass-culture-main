import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.birthday_to_newly_eligible_user import (
    send_birthday_age_18_email_to_newly_eligible_user,
)
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueSendNewlyEligibleUserEmailTest:
    def test_send_anniversary_age_18_email(self):
        # given
        user = users_factories.UserFactory()

        # when
        send_birthday_age_18_email_to_newly_eligible_user(user)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.BIRTHDAY_AGE_18_TO_NEWLY_ELIGIBLE_USER.value.__dict__
        )
