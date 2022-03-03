import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.factories as users_factories
from pcapi.domain.user_emails import send_activation_email


pytestmark = pytest.mark.usefixtures("db_session")


# FIXME (dbaty, 2020-02-01): I am not sure what we are really testing
# here. We seem to mock way too much. (At least, we could remove a few
# duplicate tests that check what happens when there is a bookingEmail
# and when there is none. We use a function for that in the
# implementation, there is no need to test it again and again here.)
#
# We should probably rewrite all tests and turn them into light
# integration tests that:
# - do NOT mock the functions that return data to be injected into
#   Mailjet (e.g. make_beneficiary_booking_cancellation_email_data)
# - check the recipients
# - ... and that's all.


class SendActivationEmailTest:
    def test_send_activation_email(self):
        # given
        beneficiary = users_factories.BeneficiaryGrant18Factory.build()

        # when
        send_activation_email(beneficiary)

        # then
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0].sent_data["Mj-TemplateID"] == 994771
