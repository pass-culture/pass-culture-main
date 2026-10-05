from dataclasses import asdict

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.pro import venue_closed
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
class SendVenueClosedEmailToAuthorTest:
    def test_send_mail(self):
        author = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        history_event = history_factories.ActionHistoryFactory(
            authorUser=author, venue=venue, actionType=history_models.ActionType.VENUE_CLOSED
        )

        venue_closed.send_venue_closed_email_to_author(venue.id)

        assert len(mails_testing.outbox) == 1

        mail = mails_testing.outbox[0]
        assert mail["To"] == author.email
        assert mail["template"] == asdict(TransactionalEmail.VENUE_CLOSED_CONFIRMATION.value)
        assert mail["params"] == {
            "VENUE_NAME": venue.publicName,
            "SIRET": venue.siret,
            "OFFERER_NAME": venue.managingOfferer.name,
            "USER_FIRST_NAME": author.firstName,
            "USER_LAST_NAME": author.lastName,
            "USER_EMAIL": author.email,
            "REQUEST_DATE": history_event.actionDate.date(),
            "REQUEST_TIME": history_event.actionDate.time(),
        }

    def test_no_email_sent_if_has_not_been_closed(self):
        venue = offerers_factories.VenueFactory()
        venue_closed.send_venue_closed_email_to_author(venue.id)
        assert not mails_testing.outbox

    def test_no_email_sent_if_closed_event_has_no_author(self):
        venue = offerers_factories.VenueFactory()
        history_factories.ActionHistoryFactory(
            authorUser=None, venue=venue, actionType=history_models.ActionType.VENUE_CLOSED
        )

        venue_closed.send_venue_closed_email_to_author(venue.id)
        assert not mails_testing.outbox
