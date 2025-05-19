import datetime

import pytest
import time_machine

import pcapi.core.bookings.api as bookings_api
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.finance import api
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.models import db


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.features(WIP_ENABLE_NEW_FINANCE_WORKFLOW=False),
]


def test_integration_full_workflow(css_font_http_request_mock):
    # A booking is manually marked as used. Check the whole workflow
    # until the invoice is generated.
    initial_dt = datetime.datetime.utcnow()
    venue = offerers_factories.VenueFactory(pricing_point="self")
    bank_account = factories.BankAccountFactory(offerer=venue.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(
        venue=venue, bankAccount=bank_account, timespan=(datetime.datetime.utcnow() - datetime.timedelta(days=10),)
    )
    booking = bookings_factories.BookingFactory(stock__offer__venue=venue)

    with time_machine.travel(initial_dt, tick=False) as frozen_time:
        bookings_api.mark_as_used(booking, bookings_models.BookingValidationAuthorType.AUTO)
        assert booking.status == bookings_models.BookingStatus.USED
        event = db.session.query(models.FinanceEvent).one()
        assert event.booking == booking
        assert event.status == models.FinanceEventStatus.READY

        # `price_events()` ignores recently created events (< 1 minute).
        frozen_time.move_to(initial_dt + datetime.timedelta(minutes=1))
        api.price_events()
        assert event.status == models.FinanceEventStatus.PRICED
        pricing = db.session.query(models.Pricing).one()
        assert pricing.event == event
        assert pricing.booking == booking
        assert pricing.status == models.PricingStatus.VALIDATED

    cutoff = datetime.datetime.utcnow()
    batch = api.generate_cashflows_and_payment_files(cutoff)
    assert len(pricing.cashflows) == 1
    cashflow = pricing.cashflows[0]
    assert cashflow.status == models.CashflowStatus.UNDER_REVIEW
    db.session.refresh(pricing)
    assert pricing.status == models.PricingStatus.PROCESSED

    api.generate_invoices_and_debit_notes_legacy(batch)
    db.session.refresh(cashflow)
    assert cashflow.status == models.CashflowStatus.ACCEPTED
    db.session.refresh(pricing)
    assert pricing.status == models.PricingStatus.INVOICED
    assert booking.status == bookings_models.BookingStatus.REIMBURSED
    assert booking.reimbursementDate is not None


def test_integration_partial_auto_mark_as_used():
    # A booking is manually marked as used. Check only until the
    # generation of the pricing.
    now = datetime.datetime.utcnow()
    venue = offerers_factories.VenueFactory(pricing_point="self")
    bank_account = factories.BankAccountFactory(offerer=venue.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
    booking = bookings_factories.BookingFactory(
        stock=offers_factories.EventStockFactory(
            beginningDatetime=now,
            offer__venue=venue,
        ),
    )

    with time_machine.travel(now) as frozen_time:
        # `auto_mark_as_used_after_event()` ignores recently used
        # bookings (< 48 hours).
        now += datetime.timedelta(hours=48, seconds=1)
        frozen_time.move_to(now)
        bookings_api.auto_mark_as_used_after_event()
        assert booking.status == bookings_models.BookingStatus.USED
        event = db.session.query(models.FinanceEvent).one()
        assert event.booking == booking
        assert event.status == models.FinanceEventStatus.READY

        # `price_events()` ignores recently created events (< 1 minute).
        now += datetime.timedelta(minutes=1, seconds=1)
        frozen_time.move_to(now)
        api.price_events()
        assert event.status == models.FinanceEventStatus.PRICED
        pricing = db.session.query(models.Pricing).one()
        assert pricing.event == event
        assert pricing.booking == booking
        assert pricing.status == models.PricingStatus.VALIDATED


def test_integration_partial_used_then_cancelled():
    # A booking is manually marked as used, then cancelled.
    initial_dt = datetime.datetime.utcnow()
    venue = offerers_factories.VenueFactory(pricing_point="self")
    bank_account = factories.BankAccountFactory(offerer=venue.managingOfferer)
    offerers_factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
    booking = bookings_factories.BookingFactory(stock__offer__venue=venue)

    with time_machine.travel(initial_dt, tick=False):
        # Mark as used and price.
        bookings_api.mark_as_used(booking, bookings_models.BookingValidationAuthorType.AUTO)
        assert booking.status == bookings_models.BookingStatus.USED

    # `price_events()` ignores recently created events (< 1 minute).
    with time_machine.travel(initial_dt + datetime.timedelta(minutes=1), tick=False):
        api.price_events()
        assert db.session.query(models.Pricing).count() == 1

        # Now cancel the booking. We should not get a new pricing.
        bookings_api.mark_as_cancelled(booking, bookings_models.BookingCancellationReasons.BENEFICIARY)

    # `price_events()` ignores recently created events (< 1 minute).
    with time_machine.travel(initial_dt + datetime.timedelta(minutes=2), tick=False):
        api.price_events()
        assert db.session.query(models.Pricing).count() == 1  # still only one pricing
