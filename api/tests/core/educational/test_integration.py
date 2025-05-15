import datetime

import pytest
import time_machine

from pcapi.core.bookings import api as bookings_api
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class EducationalWorkflowTest:
    def test_collective_workflow(self, db_session):
        now = datetime.datetime.utcnow()
        start_datetime = now + datetime.timedelta(days=1)

        venue = offerers_factories.VenueFactory(pricing_point="self")
        bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
        offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)

        collective_offer = educational_factories.CollectiveOfferFactory(
            venue=venue,
        )

        collective_booking = educational_factories.ConfirmedCollectiveBookingFactory(
            collectiveStock__startDatetime=start_datetime,
            collectiveStock__collectiveOffer=collective_offer,
        )

        assert collective_offer.displayedStatus == educational_models.CollectiveOfferDisplayedStatus.BOOKED
        assert collective_booking.status == educational_models.CollectiveBookingStatus.CONFIRMED

        now = start_datetime + datetime.timedelta(days=3)
        with time_machine.travel(now) as frozen_time:
            # We change the status of the offer (but not the booking)
            assert collective_offer.displayedStatus == educational_models.CollectiveOfferDisplayedStatus.ENDED
            assert collective_booking.status == educational_models.CollectiveBookingStatus.CONFIRMED

            # We need to expire all the objects to ensure the test session is in sync with the database when auto_mark_as_used_after_event is called
            db.session.expire_all()

            # Mark the booking as used
            bookings_api.auto_mark_as_used_after_event()

            assert collective_offer.displayedStatus == educational_models.CollectiveOfferDisplayedStatus.ENDED
            assert collective_booking.status == educational_models.CollectiveBookingStatus.USED

            # Generate the Reimbursement
            now += datetime.timedelta(days=1)
            frozen_time.move_to(now)

            finance_event = collective_booking.finance_events[0]
            finance_api.price_event(finance_event)
            batch = finance_api.generate_cashflows(now)
            finance_api.generate_payment_files(batch)  # mark cashflows as UNDER_REVIEW
            cashflow_ids = [c.id for c in db.session.query(finance_models.Cashflow)]

            bank_account_id = bank_account.id
            finance_api._generate_invoice_legacy(
                bank_account_id=bank_account_id,
                cashflow_ids=cashflow_ids,
            )

            assert collective_offer.displayedStatus == educational_models.CollectiveOfferDisplayedStatus.REIMBURSED
            assert collective_booking.status == educational_models.CollectiveBookingStatus.REIMBURSED
