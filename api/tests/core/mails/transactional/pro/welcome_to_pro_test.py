from dataclasses import asdict

import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.users.factories as users_factories
from pcapi.core.mails.transactional.pro.welcome_to_pro import send_welcome_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.settings import PRO_URL


pytestmark = pytest.mark.usefixtures("db_session")


class SendWelcomeToProEmailTest:
    def test_sends_email_to_pro_user(self):
        # Given
        user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory()

        # When
        send_welcome_to_pro_email(user, venue)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["To"] == user.email
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.WELCOME_TO_PRO.value)
        assert mails_testing.outbox[0]["params"] == {
            "PC_PRO_VENUE_LINK": f"{PRO_URL}/structures/{venue.managingOffererId}/lieux/{venue.id}",
        }
