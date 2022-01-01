from datetime import datetime

from dateutil.relativedelta import relativedelta
import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.users.anniversary_to_newly_eligible_user import (
    send_newly_eligible_age_18_user_email,
)
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class MailjetSendNewlyEligibleUserEmailTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_send_anniversary_age_18_email(self):
        # given
        user = users_factories.UserFactory(
            dateOfBirth=(datetime.now() - relativedelta(years=18, days=5)), departementCode="93"
        )

        # when
        send_newly_eligible_age_18_user_email(user)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 2030056
        assert (
            mails_testing.outbox[0].sent_data["Vars"]["nativeAppLink"][:96]
            == "https://passcultureapptestauto.page.link/?link=https%3A%2F%2F"
            "webapp-v2.example.com%2Fid-check%3F"
        )
        assert "email" in mails_testing.outbox[0].sent_data["Vars"]["nativeAppLink"]
        assert mails_testing.outbox[0].sent_data["Vars"]["depositAmount"] == 300


class SendinblueSendNewlyEligibleUserEmailTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_anniversary_age_18_email(self):
        # given
        user = users_factories.UserFactory()

        # when
        send_newly_eligible_age_18_user_email(user)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["template"] == {
            "id_prod": 78,
            "id_not_prod": 32,
            "tags": ["anniversaire_18_ans"],
            "use_priority_queue": False,
        }
