from dataclasses import asdict
from datetime import date

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro import offerer_closed
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories


@pytest.mark.usefixtures("db_session")
class SendOffererClosedEmailTest:
    def test_send_mail(self):
        offerer = offerers_factories.OffererFactory()
        user_offerer_1 = offerers_factories.UserOffererFactory(offerer=offerer)
        user_offerer_2 = offerers_factories.UserOffererFactory(offerer=offerer)
        offerers_factories.NotValidatedUserOffererFactory(offerer=offerer)
        offerers_factories.RejectedUserOffererFactory(offerer=offerer)

        offerer_closed.send_offerer_closed_email_to_pro(offerer, date(2025, 3, 7))

        assert len(mails_testing.outbox) == 2
        for mail, user_offerer in zip(mails_testing.outbox, (user_offerer_1, user_offerer_2)):
            assert mail["To"] == user_offerer.user.email
            assert mail["template"] == asdict(TransactionalEmail.OFFERER_CLOSED.value)
            assert mail["params"] == {
                "OFFERER_NAME": offerer.name,
                "SIREN": offerer.siren,
                "END_DATE": "vendredi 7 mars 2025",
                "HAS_THING_BOOKINGS": False,
                "HAS_EVENT_BOOKINGS": False,
            }
