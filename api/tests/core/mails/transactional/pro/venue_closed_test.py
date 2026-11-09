from dataclasses import asdict

import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.history import constants as history_constants
from pcapi.core.history import factories as history_factories
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.pro import venue_closed
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.permissions import api as perm_api
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
class SendVenueClosedEmailToAuthorTest:
    @pytest.mark.parametrize(
        "is_bo_user,has_booking_email",
        (
            pytest.param(False, False, id="pro_author"),
            pytest.param(True, True, id="bo_author_with_booking_email"),
            pytest.param(True, False, id="bo_author_without_booking_email"),
        ),
    )
    def test_send_mail(self, is_bo_user, has_booking_email):
        author = users_factories.UserFactory()
        if is_bo_user:
            perm_api.create_backoffice_profile(author)
        venue = offerers_factories.VenueFactory(bookingEmail=("venue1@nowhere" if has_booking_email else None))
        offerers_factories.VenueFactory(bookingEmail="venue2@nowhere", managingOfferer=venue.managingOfferer)
        offerers_factories.VenueFactory(bookingEmail="venue3@nowhere", managingOfferer=venue.managingOfferer)
        offerers_factories.VenueFactory(bookingEmail=None, managingOfferer=venue.managingOfferer)
        history_event = history_factories.ActionHistoryFactory(
            authorUser=author, venue=venue, actionType=history_constants.ActionType.VENUE_CLOSED
        )

        venue_closed.send_venue_closed_email(venue.id)

        assert len(mails_testing.outbox) == 1

        mail = mails_testing.outbox[0]
        if is_bo_user:
            if has_booking_email:
                assert mail["To"] == "venue1@nowhere"
            else:
                assert set(mail["To"].split(", ")) == {"venue2@nowhere", "venue3@nowhere"}
        else:
            assert mail["To"] == author.email
        assert mail["template"] == asdict(TransactionalEmail.VENUE_CLOSED_CONFIRMATION.value)
        params = {
            "VENUE_NAME": venue.publicName,
            "SIRET": venue.siret,
            "OFFERER_NAME": venue.managingOfferer.name,
            "USER_FIRST_NAME": None,
            "USER_LAST_NAME": None,
            "USER_EMAIL": None,
            "REQUEST_DATE": history_event.actionDate.date(),
            "REQUEST_TIME": history_event.actionDate.time(),
        }
        if not is_bo_user:
            params.update(
                {
                    "USER_FIRST_NAME": author.firstName,
                    "USER_LAST_NAME": author.lastName,
                    "USER_EMAIL": author.email,
                }
            )
        assert mail["params"] == params

    def test_no_email_sent_if_has_not_been_closed(self):
        venue = offerers_factories.VenueFactory()
        venue_closed.send_venue_closed_email(venue.id)
        assert not mails_testing.outbox

    @pytest.mark.parametrize("has_booking_email", (True, False))
    def test_email_sent_if_closed_event_has_no_author_and_had_booking_email(self, has_booking_email):
        venue = offerers_factories.VenueFactory(bookingEmail=("venue1@nowhere" if has_booking_email else None))
        history_factories.ActionHistoryFactory(
            authorUser=None, venue=venue, actionType=history_constants.ActionType.VENUE_CLOSED
        )

        venue_closed.send_venue_closed_email(venue.id)
        if has_booking_email:
            assert mails_testing.outbox
            assert mails_testing.outbox[0]["To"] == "venue1@nowhere"
        else:
            assert not mails_testing.outbox
