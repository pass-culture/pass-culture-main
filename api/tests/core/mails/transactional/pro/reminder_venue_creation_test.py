import dataclasses

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro.reminder_venue_creation import get_reminder_venue_creation_email_data
from pcapi.core.mails.transactional.pro.reminder_venue_creation import send_reminder_venue_creation_to_pro
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories
from pcapi.settings import PRO_URL
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class ProReminderVenueCreationEmailTest:
    def test_email_data(self):
        # given
        offerer = offerers_factories.OffererFactory()
        # when
        mail_data = get_reminder_venue_creation_email_data(offerer)
        # then
        assert mail_data.template == TransactionalEmail.REMINDER_VENUE_CREATION_TO_PRO.value
        assert mail_data.params == {"PRO_URL": PRO_URL, "OFFERER_ID": humanize(offerer.id)}

    def test_send_email(self):
        # given
        offerer = offerers_factories.OffererFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)
        # when
        send_reminder_venue_creation_to_pro(offerer)
        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.REMINDER_VENUE_CREATION_TO_PRO.value
        )
        assert mails_testing.outbox[0].sent_data["To"] == user_offerer.user.email
        assert mails_testing.outbox[0].sent_data["params"]["PRO_URL"] == PRO_URL
        assert mails_testing.outbox[0].sent_data["params"]["OFFERER_ID"] == humanize(offerer.id)
