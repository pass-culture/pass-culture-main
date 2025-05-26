"""Finance-related functions.

Dependent pricings
==================

The reimbursement rule to be applied for each booking depends on the
yearly revenue to date. For this to be reproducible, we must price
bookings in a specific, stable order: more or less (*), the order in
which bookings are used (see `_get_event_pricing_ordering_date()` for
details).

- When a booking B is priced, we should delete all pricings of
  bookings that have been marked as used later than booking B. It
  could happen if two HTTP requests ask to mark two bookings as used,
  and the COMMIT that updates the "first" one is delayed and we try to
  price the second one first. This is why we have a grace period in
  `price_bookings` that avoids pricing bookings that have been very
  recently marked as used.

- When a pricing is cancelled, we should delete all dependent pricings
  (since the revenue will be different), so that related booking can
  be priced again. That happens only if we mark a booking as unused,
  which should be rare.
"""

import csv
import datetime
import decimal
import itertools
import logging
import math
import pathlib
import secrets
import tempfile
import time
import typing
import zipfile
from collections import defaultdict

import pytz
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql.functions as sa_func
from flask import current_app as app
from flask import render_template

import pcapi.core.bookings.models as bookings_models
import pcapi.core.educational.models as educational_models
import pcapi.core.history.models as history_models
import pcapi.core.mails.transactional as transactional_mails
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.reference.models as reference_models
import pcapi.core.users.models as users_models
import pcapi.utils.date as date_utils
import pcapi.utils.db as db_utils
import pcapi.utils.pdf as pdf_utils
from pcapi import settings
from pcapi.connectors import googledrive
from pcapi.core.educational.api import booking as educational_api_booking
from pcapi.core.finance import deposit_api
from pcapi.core.history import api as history_api
from pcapi.core.logging import log_elapsed
from pcapi.core.mails.transactional import send_booking_cancellation_by_pro_to_beneficiary_email
from pcapi.core.mails.transactional.finance_incidents.finance_incident_notification import send_commercial_gesture_email
from pcapi.core.mails.transactional.finance_incidents.finance_incident_notification import send_finance_incident_emails
from pcapi.core.object_storage import store_public_object
from pcapi.domain import reimbursement
from pcapi.models import db
from pcapi.models import feature
from pcapi.models.pc_object import BaseQuery
from pcapi.repository import transaction
from pcapi.repository.session_management import is_managed_transaction
from pcapi.repository.session_management import mark_transaction_as_invalid
from pcapi.utils import human_ids
from pcapi.utils.chunks import get_chunks

from . import conf
from . import exceptions
from . import models
from . import utils
from . import validation


logger = logging.getLogger(__name__)

# When used through the cron, only price bookings that were used in 2022.
# Prior bookings have been priced manually.
MIN_DATE_TO_PRICE = datetime.datetime(2021, 12, 31, 23, 0)  # UTC
PRICE_EVENTS_BATCH_SIZE = 100
CASHFLOW_BATCH_LABEL_PREFIX = "VIR"
ORIGIN_OF_CREDIT_CASE: sa.sql.elements.Case = sa.case(
    (
        bookings_models.Booking.usedRecreditType == bookings_models.BookingRecreditType.RECREDIT_17,
        "PR18-",
    ),
    (
        bookings_models.Booking.usedRecreditType == bookings_models.BookingRecreditType.RECREDIT_18,
        "PR18+",
    ),
    (
        sa.or_(
            sa.and_(
                bookings_models.Booking.usedRecreditType == None,
                models.Deposit.type == models.DepositType.GRANT_17_18,
            ),
            models.Deposit.type == models.DepositType.GRANT_15_17,
        ),
        "AR18-",
    ),
    (
        models.Deposit.type == models.DepositType.GRANT_18,
        "AR18+",
    ),
    else_="",
)


def get_pricing_ordering_date(
    booking: bookings_models.Booking | educational_models.CollectiveBooking,
) -> datetime.datetime:
    if isinstance(booking, bookings_models.Booking):
        eventDatetime = booking.stock.beginningDatetime
    else:
        eventDatetime = booking.collectiveStock.endDatetime
    # IMPORTANT: if you change this, you must also adapt the SQL query
    # in `core.offerers.api.link_venue_to_pricing_point()`
    return max(
        get_pricing_point_link(booking).timespan.lower,
        eventDatetime or booking.dateUsed,
        booking.dateUsed,
    )


def add_event(
    motive: models.FinanceEventMotive,
    booking: bookings_models.Booking | educational_models.CollectiveBooking | None = None,
    booking_incident: models.BookingFinanceIncident | None = None,
    incident_validation_date: datetime.datetime | None = None,
) -> models.FinanceEvent:
    status = None
    value_date = None
    pricing_point_id = None
    pricing_ordering_date = None
    if booking_incident:
        booking = booking_incident.booking or booking_incident.collectiveBooking

    assert booking

    if motive in (
        models.FinanceEventMotive.BOOKING_USED,
        models.FinanceEventMotive.BOOKING_USED_AFTER_CANCELLATION,
    ):
        assert booking.dateUsed
        value_date = booking.dateUsed

        pricing_point_id = booking.venue.current_pricing_point_id
        if pricing_point_id:
            pricing_ordering_date = get_pricing_ordering_date(booking)
            status = models.FinanceEventStatus.READY
        else:
            pricing_ordering_date = None
            status = models.FinanceEventStatus.PENDING

    elif motive == models.FinanceEventMotive.BOOKING_UNUSED:
        # The value is irrelevant because the event won't be priced.
        value_date = datetime.datetime.utcnow()

        status = models.FinanceEventStatus.NOT_TO_BE_PRICED
        pricing_point_id = None
        pricing_ordering_date = None

    elif motive == models.FinanceEventMotive.BOOKING_CANCELLED_AFTER_USE:
        if booking.cancellationDate is None:
            raise ValueError(f"Cannot create FinanceEvent with motive {motive}. booking.cancellationDate is missing")
        value_date = booking.cancellationDate

        status = models.FinanceEventStatus.NOT_TO_BE_PRICED
        pricing_point_id = None
        pricing_ordering_date = None

    elif motive in (
        models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT,
        models.FinanceEventMotive.INCIDENT_NEW_PRICE,
        models.FinanceEventMotive.INCIDENT_COMMERCIAL_GESTURE,
    ):
        if incident_validation_date is None:
            raise ValueError(f"Cannot create FinanceEvent with motive {motive}. `incident_validation_date` is missing")
        value_date = incident_validation_date

        pricing_point_id = booking.venue.current_pricing_point_id
        if pricing_point_id:
            pricing_ordering_date = incident_validation_date
            status = models.FinanceEventStatus.READY
        else:
            pricing_ordering_date = None
            status = models.FinanceEventStatus.PENDING

    else:
        raise ValueError(f"Unexpected FinanceEventMotive: {motive}")

    assert value_date is not None

    event = models.FinanceEvent(
        booking=booking if isinstance(booking, bookings_models.Booking) and not booking_incident else None,  # type: ignore[arg-type]
        collectiveBooking=(
            booking  # type: ignore[arg-type]
            if isinstance(booking, educational_models.CollectiveBooking) and not booking_incident
            else None
        ),
        bookingFinanceIncident=booking_incident,  # type: ignore[arg-type]
        status=status,
        motive=motive,
        valueDate=value_date,
        venue=booking.venue,
        pricingPointId=pricing_point_id,
        pricingOrderingDate=pricing_ordering_date,
    )
    db.session.add(event)
    db.session.flush()

    return event


def cancel_latest_event(
    booking: bookings_models.Booking | educational_models.CollectiveBooking,
) -> models.FinanceEvent | None:
    """Cancel latest used-related finance event, if there is one."""
    event = (
        db.session.query(models.FinanceEvent)
        .filter(
            (
                (models.FinanceEvent.booking == booking)
                if isinstance(booking, bookings_models.Booking)
                else (models.FinanceEvent.collectiveBooking == booking)
            ),
            models.FinanceEvent.motive.in_(
                (
                    models.FinanceEventMotive.BOOKING_USED,
                    models.FinanceEventMotive.BOOKING_USED_AFTER_CANCELLATION,
                )
            ),
            models.FinanceEvent.status.in_(models.CANCELLABLE_FINANCE_EVENT_STATUSES),
        )
        .one_or_none()
    )
    if not event:
        # Once we have switched to event pricing, there MUST be an
        # event if a used booking is being cancelled. If no event can
        # be found, something is wrong somewhere (probably a bug).
        if booking.dateUsed:
            logger.error("No finance event to cancel", extra={"booking": booking.id})
        return None
    pricing = _cancel_event_pricing(event, models.PricingLogReason.MARK_AS_UNUSED)
    event.status = models.FinanceEventStatus.CANCELLED
    db.session.flush()
    logger.info(
        "Cancelled finance event and its pricing",
        extra={
            "booking": booking.id,
            "event": event.id,
            "pricing": pricing.id if pricing else None,
        },
    )
    return event


def price_events(
    min_date: datetime.datetime = MIN_DATE_TO_PRICE,
    batch_size: int = PRICE_EVENTS_BATCH_SIZE,
) -> None:
    """Price finance events that are ready to be priced.

    This function is normally called by a cron job.
    """
    # The upper bound on `pricingOrderingDate` avoids selecting a very
    # recent event that may have been COMMITed to the database just
    # before another event with a slightly older date (see note in
    # module docstring).
    threshold = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
    window = (min_date, threshold)

    errored_pricing_point_ids = set()

    # This is a quick hack to avoid fetching all events at once,
    # resulting in a very large session that is updated on each
    # commit, which takes a lot of time (up to 1 or 2 seconds per
    # commit).
    event_query = _get_events_to_price(window)
    loops = math.ceil(event_query.count() / batch_size)

    def _get_loop_query(
        query: BaseQuery,
        last_event: models.FinanceEvent | None,
    ) -> BaseQuery:
        # We cannot use OFFSET and LIMIT because the loop "consumes"
        # events that have been priced (so the query will not return
        # them in the next loop), but keeps events that cannot be
        # priced (so the query WILL return them in the next loop).
        if last_event:
            clause = sa.func.ROW(
                models.FinanceEvent.pricingOrderingDate,
                models.FinanceEvent.id,
            ) > sa.func.ROW(last_event.pricingOrderingDate, last_event.id)
            query = query.filter(clause)
        return query.limit(batch_size)

    last_event = None
    while loops > 0:
        with log_elapsed(logger, "Fetched batch of events to price"):
            events = list(_get_loop_query(event_query, last_event))
        for event in events:
            last_event = event
            try:
                if event.pricingPointId in errored_pricing_point_ids:
                    continue
                extra = {
                    "event": event.id,
                    "pricing_point": event.pricingPointId,
                }
                with log_elapsed(logger, "Priced event", extra):
                    price_event(event)
            except Exception as exc:
                errored_pricing_point_ids.add(event.pricingPointId)
                logger.info(
                    "Ignoring further events from pricing point",
                    extra={"pricing_point": event.pricingPointId},
                )
                logger.exception(
                    "Could not price event",
                    extra={
                        "event": event.id,
                        "pricing_point": event.pricingPointId,
                        "exc": str(exc),
                    },
                )
        loops -= 1
        # Keep last event in the session, we'll need it when calling
        # `_get_loop_query()` for the next loop.
        with log_elapsed(logger, "Expunged priced events from session"):
            for event in events:
                if event != last_event:
                    db.session.expunge(event)


def get_pricing_point_link(
    booking: bookings_models.Booking | educational_models.CollectiveBooking,
) -> offerers_models.VenuePricingPointLink:
    """Return the venue-pricing point link to use at the time the
    booking was marked as used.
    """
    timestamp = booking.dateUsed
    links = booking.venue.pricing_point_links

    # Look for a link that was active at the requested date.
    for link in links:
        if timestamp < link.timespan.lower:
            continue
        if not link.timespan.upper or timestamp < link.timespan.upper:
            return link

    # If a link was added after and it's still active, we can use it.
    # On the other hand, if there are two links, and the second one is
    # inactive, and the booking has been used before the *first* link,
    # it's not clear what we should do (and we'll raise below).
    links_after = [link for link in links if timestamp < link.timespan.lower]
    if len(links_after) == 1 and links_after[0].timespan.upper is None:
        return links_after[0]

    # Otherwise, it's not clear what we should do. Raise an error so
    # that we can investigate.
    raise ValueError(f"Could not find pricing point for booking {booking.id}")


def _get_events_to_price(window: tuple[datetime.datetime, datetime.datetime]) -> BaseQuery:
    return (
        db.session.query(models.FinanceEvent)
        .filter(
            models.FinanceEvent.pricingPointId.is_not(None),
            models.FinanceEvent.status == models.FinanceEventStatus.READY,
            models.FinanceEvent.pricingOrderingDate.between(*window),
        )
        .outerjoin(models.Pricing, models.Pricing.eventId == models.FinanceEvent.id)
        .filter(
            models.Pricing.id.is_(None) | (models.Pricing.status == models.PricingStatus.CANCELLED),
        )
        .order_by(models.FinanceEvent.pricingOrderingDate, models.FinanceEvent.id)
        .options(
            sa_orm.joinedload(models.FinanceEvent.booking),
            sa_orm.joinedload(models.FinanceEvent.collectiveBooking),
        )
    )


def lock_pricing_point(pricing_point_id: int) -> None:
    """Lock a pricing point (a venue) while we are doing some work that
    cannot be done while there are other running operations on the
    same pricing point.

    IMPORTANT: This must only be used within a transaction.

    The lock is automatically released at the end of the transaction.
    """
    return db_utils.acquire_lock(f"pricing-point-{pricing_point_id}")


def lock_bank_account(bank_account_id: int) -> None:
    """Lock a bank account while we are doing some
    work that cannot be done while there are other running operations
    on the same bank account.

    IMPORTANT: This must only be used within a transaction.

    The lock is automatically released at the end of the transaction.
    """
    return db_utils.acquire_lock(f"bank-account-{bank_account_id}")


def price_event(event: models.FinanceEvent) -> models.Pricing | None:
    assert event.pricingPointId  # helps mypy
    with transaction():
        lock_pricing_point(event.pricingPointId)

        # Now that we have acquired a lock, fetch the event from the
        # database again so that we can make some final checks before
        # actually pricing it.
        if event.bookingId:
            event = (
                db.session.query(models.FinanceEvent)
                .filter_by(id=event.id)
                .options(
                    sa_orm.joinedload(models.FinanceEvent.booking, innerjoin=True)
                    .joinedload(bookings_models.Booking.stock, innerjoin=True)
                    .joinedload(
                        offers_models.Stock.offer,
                        innerjoin=True,
                    ),
                    sa_orm.joinedload(models.FinanceEvent.booking, innerjoin=True)
                    .joinedload(bookings_models.Booking.venue, innerjoin=True)
                    .joinedload(offerers_models.Venue.pricing_point_links, innerjoin=True)
                    .joinedload(offerers_models.VenuePricingPointLink.venue, innerjoin=True),
                )
                .one()
            )
        elif event.collectiveBookingId:
            event = (
                db.session.query(models.FinanceEvent)
                .filter_by(id=event.id)
                .options(
                    sa_orm.joinedload(models.FinanceEvent.collectiveBooking, innerjoin=True)
                    .joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True)
                    .joinedload(educational_models.CollectiveStock.collectiveOffer, innerjoin=True),
                    sa_orm.joinedload(models.FinanceEvent.collectiveBooking, innerjoin=True)
                    .joinedload(educational_models.CollectiveBooking.venue, innerjoin=True)
                    .joinedload(offerers_models.Venue.pricing_point_links, innerjoin=True)
                    .joinedload(offerers_models.VenuePricingPointLink.venue, innerjoin=True),
                )
                .one()
            )
        elif event.bookingFinanceIncidentId:
            event = (
                db.session.query(models.FinanceEvent)
                .filter_by(id=event.id)
                .options(
                    sa_orm.joinedload(models.FinanceEvent.bookingFinanceIncident, innerjoin=True),
                )
                .one()
            )
        else:
            raise ValueError(
                "Finance event should be linked to an individual booking, a collectiveBooking or a booking finance incident."
            )

        # Perhaps the event has been cancelled (because the booking
        # has been marked as unused) after we acquired the lock?
        if event.status != models.FinanceEventStatus.READY:
            return None

        # Pricing the same event twice is not allowed (and would be
        # rejected by a database constraint, anyway), unless the
        # existing pricing has been cancelled.
        pricing = (
            db.session.query(models.Pricing)
            .filter(
                models.Pricing.event == event,
                models.Pricing.status != models.PricingStatus.CANCELLED,
            )
            .one_or_none()
        )
        if pricing:
            return pricing

        _delete_dependent_pricings(event, "Deleted pricings priced too early")

        pricing = _price_event(event)
        db.session.add(pricing)
        event.status = models.FinanceEventStatus.PRICED
        db.session.commit()
    return pricing


def _get_revenue_period(value_date: datetime.datetime) -> tuple[datetime.datetime, datetime.datetime]:
    """Return a datetime (year) period for the given value date, i.e. the
    first and last seconds of the year of the ``value_date``.
    """
    year = value_date.replace(tzinfo=pytz.utc).astimezone(utils.ACCOUNTING_TIMEZONE).year
    first_second = utils.ACCOUNTING_TIMEZONE.localize(
        datetime.datetime.combine(
            datetime.date(year, 1, 1),
            datetime.time.min,
        )
    ).astimezone(pytz.utc)
    last_second = utils.ACCOUNTING_TIMEZONE.localize(
        datetime.datetime.combine(
            datetime.date(year, 12, 31),
            datetime.time.max,
        )
    ).astimezone(pytz.utc)
    return first_second, last_second


def _get_current_revenue(event: models.FinanceEvent) -> int:
    """Return the current year revenue for the pricing point of an
    event, NOT including the given event.
    """
    revenue_period = _get_revenue_period(event.valueDate)
    # Collective bookings must not be included in revenue.
    current_revenue = (
        db.session.query(bookings_models.Booking)
        .join(models.Pricing)
        .filter(
            models.Pricing.pricingPointId == event.pricingPointId,
            # The following filter is not strictly necessary, because
            # this function is called before we create the pricing for
            # this event.
            models.Pricing.bookingId != event.bookingId,
            models.Pricing.valueDate.between(*revenue_period),
            models.Pricing.status != models.PricingStatus.CANCELLED,
        )
        .with_entities(sa.func.sum(bookings_models.Booking.amount * bookings_models.Booking.quantity))
        .scalar()
    )
    return utils.to_cents(current_revenue or 0)


def _price_event(event: models.FinanceEvent) -> models.Pricing:
    new_revenue = _get_current_revenue(event)
    individual_booking = event.bookingFinanceIncident.booking if event.bookingFinanceIncident else event.booking
    collective_booking = (
        event.bookingFinanceIncident.collectiveBooking if event.bookingFinanceIncident else event.collectiveBooking
    )
    booking = individual_booking or collective_booking
    assert booking  # helps mypy
    rule = None
    amount: int
    pricing_booking_id = None
    pricing_collective_booking_id = None

    if not collective_booking:  # Collective bookings are not included in revenue
        if event.motive in (
            models.FinanceEventMotive.BOOKING_USED,
            models.FinanceEventMotive.BOOKING_USED_AFTER_CANCELLATION,
        ):
            new_revenue += utils.to_cents(booking.total_amount)
        elif event.motive in (
            models.FinanceEventMotive.INCIDENT_NEW_PRICE,
            models.FinanceEventMotive.INCIDENT_COMMERCIAL_GESTURE,
        ):
            assert event.bookingFinanceIncident  # helps mypy
            new_revenue += event.bookingFinanceIncident.newTotalAmount

    if event.motive in (
        models.FinanceEventMotive.BOOKING_USED,
        models.FinanceEventMotive.BOOKING_USED_AFTER_CANCELLATION,
    ):
        rule_finder = reimbursement.CustomRuleFinder()
        rule = reimbursement.get_reimbursement_rule(booking, rule_finder, new_revenue)
        amount = -rule.apply(booking)  # outgoing, thus negative
        offerer_revenue_amount = -utils.to_cents(booking.total_amount)
        pricing_booking_id = individual_booking.id if individual_booking else None
        pricing_collective_booking_id = collective_booking.id if collective_booking else None
        lines = [
            models.PricingLine(
                amount=offerer_revenue_amount,
                category=models.PricingLineCategory.OFFERER_REVENUE,
            ),
            models.PricingLine(
                amount=amount - offerer_revenue_amount,
                category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
            ),
        ]
    elif event.motive == models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT:
        original_pricing = booking.invoiced_pricing
        assert original_pricing  # helps mypy
        rule = find_reimbursement_rule(original_pricing.customRuleId or original_pricing.standardRule)
        amount = -original_pricing.amount  # reverse the original pricing amount (positive)
        pricing_booking_id = None
        pricing_collective_booking_id = None
        lines = [
            models.PricingLine(category=original_line.category, amount=-original_line.amount)
            for original_line in original_pricing.lines
        ]
    elif event.motive == models.FinanceEventMotive.INCIDENT_NEW_PRICE:
        assert event.bookingFinanceIncident and event.bookingFinanceIncident.newTotalAmount  # helps mypy
        original_pricing = booking.invoiced_pricing
        assert original_pricing  # helps mypy
        rule = find_reimbursement_rule(original_pricing.customRuleId or original_pricing.standardRule)
        amount = -rule.apply(booking, event.bookingFinanceIncident.newTotalAmount)  # outgoing, thus negative
        offerer_revenue_amount = -event.bookingFinanceIncident.newTotalAmount
        pricing_booking_id = None
        pricing_collective_booking_id = None
        lines = [
            models.PricingLine(
                amount=offerer_revenue_amount,
                category=models.PricingLineCategory.OFFERER_REVENUE,
            ),
            models.PricingLine(
                amount=amount - offerer_revenue_amount,
                category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
            ),
        ]
    elif event.motive == models.FinanceEventMotive.INCIDENT_COMMERCIAL_GESTURE:
        assert event.bookingFinanceIncident and event.bookingFinanceIncident.due_amount_by_offerer  # helps mypy
        rule = reimbursement.CommercialGestureReimbursementRule()
        amount = -event.bookingFinanceIncident.due_amount_by_offerer  # outgoing, thus negative
        offerer_revenue_amount = -event.bookingFinanceIncident.due_amount_by_offerer
        pricing_booking_id = None
        pricing_collective_booking_id = None
        lines = [
            models.PricingLine(
                amount=amount,
                category=models.PricingLineCategory.COMMERCIAL_GESTURE,
            ),
            models.PricingLine(
                amount=0,
                category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
            ),
        ]
    else:
        # Unhandled motives from FinanceEventMotive enum: BOOKING_UNUSED, BOOKING_CANCELLED_AFTER_USE
        raise ValueError(f"Unexpected FinanceEventMotive: {event.motive}")

    # `Pricing.amount` equals the sum of the amount of all lines.
    return models.Pricing(
        status=_get_initial_pricing_status(booking),
        pricingPointId=event.pricingPointId,
        valueDate=event.valueDate,
        amount=amount,
        standardRule=rule.description if not isinstance(rule, models.CustomReimbursementRule) else "",
        customRuleId=rule.id if isinstance(rule, models.CustomReimbursementRule) else None,
        revenue=new_revenue,
        lines=lines,  # type: ignore[arg-type]
        bookingId=pricing_booking_id,
        collectiveBookingId=pricing_collective_booking_id,
        eventId=event.id,
        venueId=booking.venueId,  # denormalized for performance in `_generate_cashflows()`
    )


def _get_initial_pricing_status(
    booking: bookings_models.Booking | educational_models.CollectiveBooking,
) -> models.PricingStatus:
    # In the future, we may set the pricing as "pending" (as in
    # "pending validation") for example if the pricing point is new,
    # or if the offer or offerer has particular characteristics. For
    # now, we'll automatically mark it as validated, i.e. payable.
    return models.PricingStatus.VALIDATED


def force_event_repricing(
    event: models.FinanceEvent,
    reason: models.PricingLogReason,
) -> None:
    """Cancel the pricing of the event and force it to be priced again.

    This is needed when the finance event is linked to a booking whose
    price has been changed, or when the date of the booked offer event
    has changed.
    """
    _cancel_event_pricing(event=event, reason=reason)
    event.status = models.FinanceEventStatus.READY
    db.session.add(event)


def _cancel_event_pricing(
    event: models.FinanceEvent,
    reason: models.PricingLogReason,
) -> models.Pricing | None:
    if not event.pricingPointId:
        return None

    try:
        lock_pricing_point(event.pricingPointId)

        pricing = (
            db.session.query(models.Pricing)
            .filter(
                models.Pricing.event == event,
                models.Pricing.status != models.PricingStatus.CANCELLED,
            )
            .one_or_none()
        )

        if not pricing:
            return None

        if pricing.status != models.PricingStatus.VALIDATED:
            # That should never happen, because we should never try to
            # cancel an event after it has been reimbursed.
            raise exceptions.NonCancellablePricingError()

        # We need to *cancel* the pricing of the requested event AND
        # *delete* all pricings that depended on it (i.e. all pricings
        # for events that were priced after the requested event), so
        # that we can price them again.
        _delete_dependent_pricings(
            event,
            "Deleted pricings that depended on cancelled pricing",
        )

        db.session.add(
            models.PricingLog(
                pricing=pricing,
                statusBefore=pricing.status,
                statusAfter=models.PricingStatus.CANCELLED,
                reason=reason,
            )
        )
        pricing.status = models.PricingStatus.CANCELLED
        db.session.add(pricing)
        db.session.flush()
        logger.info(
            "Cancelled pricing",
            extra={"event": event.id, "pricing": pricing.id},
        )
    except Exception:
        if is_managed_transaction():
            mark_transaction_as_invalid()
        else:
            db.session.rollback()
        raise
    return pricing


def _delete_dependent_pricings(
    event: models.FinanceEvent, log_message: str, pricing_points_overriding_pricing_ordering: typing.Iterable[int] = ()
) -> None:
    """Delete pricings for events that should be priced after the
    requested ``event``.

    See note in the module docstring for further details.

    pricing_points_overriding_pricing_ordering : a list of pricing point ids.
    In a script, you might have to add new pricings to a cutoff period that already
    has reimbursed pricings that can't be deleted (and so you can't compute the new
    pricing order). But sometimes, the order would not change the pricing value (because
    there is a custom reimbursement rule, or the pricing point's revenue would not change enough to
    change the reimbursement rule, etc), so you can add the pricing point to the list, and the pricings will be moved as you needed.
    """
    revenue_period_start, revenue_period_end = _get_revenue_period(event.valueDate)

    pricings = (
        db.session.query(models.Pricing)
        .filter(
            models.Pricing.pricingPoint == event.pricingPoint,
        )
        .join(models.Pricing.event)
        .filter(
            models.Pricing.valueDate.between(revenue_period_start, revenue_period_end),
            sa.func.ROW(models.FinanceEvent.pricingOrderingDate, models.FinanceEvent.id)
            > sa.func.ROW(event.pricingOrderingDate, event.id),
        )
    )

    pricings = pricings.all()
    if not pricings:
        return
    pricing_ids = {pricing.id for pricing in pricings}
    events_already_priced = {pricing.eventId for pricing in pricings}
    for pricing in pricings:
        if pricing.status not in models.DELETABLE_PRICING_STATUSES:
            assert event.pricingPointId  # helps mypy
            if event.pricingPointId in (
                pricing_points_overriding_pricing_ordering
                or settings.FINANCE_OVERRIDE_PRICING_ORDERING_ON_PRICING_POINTS
            ):
                pricing_ids.remove(pricing.id)
                events_already_priced.remove(pricing.eventId)
                logger.info(
                    "Found non-deletable pricing for a pricing point that has an older event to price or cancel (special case for problematic pricing points)",
                    extra={
                        "event_being_priced_or_cancelled": event.id,
                        "older_pricing": pricing.id,
                        "older_pricing_status": pricing.status,
                        "pricing_point": event.pricingPointId,
                    },
                )
                continue
            logger.error(
                "Found non-deletable pricing for a pricing point that has an older event to price or cancel",
                extra={
                    "event_being_priced_or_cancelled": event.id,
                    "older_pricing": pricing.id,
                    "older_pricing_status": pricing.status,
                    "pricing_point": event.pricingPointId,
                },
            )
            raise exceptions.NonCancellablePricingError()

    if not pricing_ids:
        return

    # Do not reuse the `pricings` query. It should not have changed
    # since the beginning of the function (since we should have an
    # exclusive lock on the pricing point to avoid that)... but let's
    # be defensive.
    lines = db.session.query(models.PricingLine).filter(models.PricingLine.pricingId.in_(pricing_ids))
    lines.delete(synchronize_session=False)
    logs = db.session.query(models.PricingLog).filter(models.PricingLog.pricingId.in_(pricing_ids))
    logs.delete(synchronize_session=False)
    pricings = db.session.query(models.Pricing).filter(models.Pricing.id.in_(pricing_ids))
    pricings.delete(synchronize_session=False)

    db.session.query(models.FinanceEvent).filter(
        models.FinanceEvent.id.in_(events_already_priced),
        models.FinanceEvent.status == models.FinanceEventStatus.PRICED,
    ).update(
        {"status": models.FinanceEventStatus.READY},
        synchronize_session=False,
    )
    logger.info(
        log_message,
        extra={
            "event_being_priced_or_cancelled": event.id,
            "events_already_priced": events_already_priced,
            "pricing_point": event.pricingPointId,
        },
    )


def update_finance_event_pricing_date(stock: offers_models.Stock) -> None:
    """Update pricing ordering date of finance events linked to a stock when its date is modified.

    `FinanceEvent.pricingOrderingDate` is calculated from the date of the stock (for event offers).
    When this date changes, the `pricingOrderingDate` must be updated and subsequent finance
    events must be repriced.
    """
    pricing_point_id = stock.offer.venue.current_pricing_point_id
    finance_events_from_pricing_point = (
        db.session.query(models.FinanceEvent)
        .options(sa_orm.joinedload(models.FinanceEvent.pricings))
        .filter(models.FinanceEvent.pricingPointId == pricing_point_id)
    )
    bookings_of_this_stock = (
        db.session.query(bookings_models.Booking)
        .with_entities(bookings_models.Booking.id)
        .filter(bookings_models.Booking.stockId == stock.id)
    )
    finance_events_from_stock = (
        finance_events_from_pricing_point.filter(models.FinanceEvent.bookingId.in_(bookings_of_this_stock))
        .filter(models.FinanceEvent.status != models.FinanceEventStatus.NOT_TO_BE_PRICED)
        .order_by(models.FinanceEvent.pricingOrderingDate)
        .all()
    )

    if finance_events_from_stock:
        oldest_pricing_ordering_date = finance_events_from_stock[0].pricingOrderingDate
        for finance_event in finance_events_from_stock:
            finance_event.pricingOrderingDate = get_pricing_ordering_date(finance_event.booking)
            oldest_pricing_ordering_date = min(oldest_pricing_ordering_date, finance_event.pricingOrderingDate)
            db.session.add(finance_event)
        first_event = (
            db.session.query(models.FinanceEvent)
            .filter(
                models.FinanceEvent.pricingPointId == pricing_point_id,
                models.FinanceEvent.pricingOrderingDate >= oldest_pricing_ordering_date,
                models.FinanceEvent.status.in_([models.FinanceEventStatus.READY, models.FinanceEventStatus.PRICED]),
            )
            .order_by(models.FinanceEvent.pricingOrderingDate, models.FinanceEvent.id)
            .first()
        )
        force_event_repricing(first_event, models.PricingLogReason.CHANGE_DATE)


def generate_cashflows_and_payment_files(cutoff: datetime.datetime) -> models.CashflowBatch:
    batch = generate_cashflows(cutoff)
    generate_payment_files(batch)
    return batch


def _get_next_cashflow_batch_label() -> str:
    """Return the label of the next CashflowBatch."""
    latest_batch = (
        db.session.query(models.CashflowBatch).order_by(models.CashflowBatch.cutoff.desc()).limit(1).one_or_none()
    )
    if latest_batch is None:
        latest_number = 0
    else:
        latest_number = int(latest_batch.label[len(CASHFLOW_BATCH_LABEL_PREFIX) :])

    next_number = latest_number + 1
    return CASHFLOW_BATCH_LABEL_PREFIX + str(next_number)


def generate_cashflows(cutoff: datetime.datetime) -> models.CashflowBatch:
    """Generate a new CashflowBatch and a new cashflow for each
    reimbursement point for which there is money to transfer.
    """
    app.redis_client.set(conf.REDIS_GENERATE_CASHFLOW_LOCK, "1", ex=conf.REDIS_GENERATE_CASHFLOW_LOCK_TIMEOUT)
    batch = models.CashflowBatch(cutoff=cutoff, label=_get_next_cashflow_batch_label())
    db.session.add(batch)
    db.session.commit()
    _generate_cashflows(batch)
    # if the script fail we want to keep the lock to forbid backoffice to modify the data
    app.redis_client.delete(conf.REDIS_GENERATE_CASHFLOW_LOCK)
    return batch


def _generate_cashflows(batch: models.CashflowBatch) -> None:
    """Given an existing CashflowBatch and corresponding cutoff, generate
    a new cashflow for each bank account for which there is money to transfer.

    This is a private function that you should never call directly,
    unless the cashflow generation stopped before its end and you want
    to proceed with an **existing** CashflowBatch.
    """
    # Store now otherwise SQLAlchemy will make a SELECT to fetch the
    # id again after each COMMIT.
    batch_id = batch.id
    logger.info("Started to generate cashflows for batch %d", batch_id)
    filters = (
        models.Pricing.status == models.PricingStatus.VALIDATED,
        models.Pricing.valueDate < batch.cutoff,
        # We should not have any validated pricing with a cashflow,
        # this is a safety belt.
        models.CashflowPricing.pricingId.is_(None),
        # Bookings can now be priced even if BankAccount is not ACCEPTED,
        # but to generate cashflows we definitely need it.
        models.BankAccount.status == models.BankAccountApplicationStatus.ACCEPTED,
        # Even if a booking is marked as used prematurely, we should
        # wait for the event to happen.
        sa.or_(
            sa.and_(
                models.Pricing.bookingId.is_not(None),
                sa.or_(
                    offers_models.Stock.beginningDatetime.is_(None),
                    offers_models.Stock.beginningDatetime < batch.cutoff,
                ),
            ),
            sa.and_(
                models.Pricing.collectiveBookingId.is_not(None),
                educational_models.CollectiveStock.endDatetime < batch.cutoff,
            ),
            models.FinanceEvent.bookingFinanceIncidentId.is_not(None),
        ),
    )

    def _mark_as_processed(pricing_ids: typing.Iterable[int]) -> None:
        db.session.execute(
            sa.text(
                """
                WITH updated AS (
                  UPDATE pricing
                  SET status = :processed
                  WHERE
                    id in :pricing_ids
                  RETURNING id AS pricing_id
                )
                INSERT INTO pricing_log
                ("pricingId", "statusBefore", "statusAfter", reason)
                SELECT updated.pricing_id, :validated, :processed, :log_reason from updated
            """
            ),
            {
                "validated": models.PricingStatus.VALIDATED.value,
                "processed": models.PricingStatus.PROCESSED.value,
                "log_reason": models.PricingLogReason.GENERATE_CASHFLOW.value,
                "pricing_ids": tuple(pricing_ids),
            },
        )

    bank_account_infos = (
        db.session.query(models.Pricing)
        .filter(*filters)
        .outerjoin(models.Pricing.booking)
        .outerjoin(bookings_models.Booking.stock)
        .outerjoin(models.Pricing.collectiveBooking)
        .outerjoin(educational_models.CollectiveBooking.collectiveStock)
        .join(models.Pricing.event)
        .join(
            offerers_models.VenueBankAccountLink,
            offerers_models.VenueBankAccountLink.venueId == models.Pricing.venueId,
        )
        .filter(offerers_models.VenueBankAccountLink.timespan.contains(batch.cutoff))
        .join(models.BankAccount, models.BankAccount.id == offerers_models.VenueBankAccountLink.bankAccountId)
        .outerjoin(models.CashflowPricing)
        .with_entities(
            models.BankAccount.id,
            sa_func.array_agg(models.Pricing.venueId.distinct()),
        )
        .group_by(
            models.BankAccount.id,
        )
    )

    for bank_account_id, venue_ids in bank_account_infos:
        log_extra = {
            "batch": batch_id,
            "bank_account": bank_account_id,
        }
        start = time.perf_counter()
        logger.info("Generating cashflow", extra=log_extra)
        try:
            with transaction():
                pricings = (
                    db.session.query(models.Pricing)
                    .outerjoin(models.Pricing.booking)
                    .outerjoin(bookings_models.Booking.stock)
                    .outerjoin(models.Pricing.collectiveBooking)
                    .outerjoin(educational_models.CollectiveBooking.collectiveStock)
                    .join(models.Pricing.event)
                    .join(
                        models.BankAccount,
                        models.BankAccount.id == bank_account_id,
                    )
                    .outerjoin(models.CashflowPricing)
                    .filter(
                        models.Pricing.venueId.in_(venue_ids),
                        *filters,
                    )
                )

                # Don't generate cashflows if ever all of the priced bookings are free → avoid creating empty invoices
                pricings_with_lines_amount = (
                    pricings.join(models.Pricing.lines)
                    .with_entities(
                        models.Pricing.id,
                        sa_func.count(models.PricingLine.id).label("lines_count"),
                        sa_func.sum(sa.case((models.PricingLine.amount == 0, 1), else_=0)).label("free_lines_count"),
                    )
                    .group_by(models.Pricing.id)
                    .all()
                )
                pricing_ids = {e.id for e in pricings_with_lines_amount}
                free_pricing_ids = {e.id for e in pricings_with_lines_amount if e.lines_count == e.free_lines_count}
                if pricing_ids and (len(pricing_ids) == len(free_pricing_ids)):
                    logger.info(
                        "Found only free pricings, skip cashflow creation but mark pricings as processed",
                        extra={
                            "pricing_ids": pricing_ids,
                            "bank_account": bank_account_id,
                        },
                    )
                    _mark_as_processed(pricing_ids)
                    continue

                # Check integrity by looking for bookings whose amount
                # has been changed after they have been priced.
                diff = (
                    pricings.join(models.Pricing.lines)
                    .filter(
                        models.PricingLine.category == models.PricingLineCategory.OFFERER_REVENUE,
                        models.PricingLine.amount
                        != -100
                        * sa.case(
                            (
                                bookings_models.Booking.id.is_not(None),
                                bookings_models.Booking.amount * bookings_models.Booking.quantity,
                            ),
                            else_=educational_models.CollectiveStock.price,
                        ),
                    )
                    .with_entities(models.Pricing.id)
                )
                diff = {_pricing_id for (_pricing_id,) in diff.all()}
                if diff:
                    logger.error(
                        "Found integrity error on booking prices vs. pricing lines",
                        extra={
                            "pricing_lines": diff,
                            "bank_account": bank_account_id,
                        },
                    )
                    continue
                total = pricings.with_entities(sa.func.sum(models.Pricing.amount)).scalar() or 0

                # The total is positive if the pro owes us more than we do.
                if total > 0:
                    all_current_incidents = (
                        db.session.query(models.FinanceIncident)
                        .join(models.FinanceIncident.booking_finance_incidents)
                        .join(models.BookingFinanceIncident.finance_events)
                        .join(models.FinanceEvent.pricings)
                        .outerjoin(models.Pricing.cashflows)
                        .filter(
                            models.FinanceIncident.venueId.in_(venue_ids),
                            models.FinanceIncident.status == models.IncidentStatus.VALIDATED,
                            models.Cashflow.id.is_(None),  # exclude incidents that already have a cashflow
                            models.Pricing.status == models.PricingStatus.VALIDATED,
                            models.Pricing.valueDate < batch.cutoff,
                        )
                        .all()
                    )

                    override_incident_debit_note = any(incident.forceDebitNote for incident in all_current_incidents)
                    # Last cashflow where we effectively paid (successfully or not) the pro
                    last_cashflow = (
                        db.session.query(models.Cashflow)
                        .filter(
                            models.Cashflow.bankAccountId == bank_account_id,
                            models.Cashflow.status == models.CashflowStatus.ACCEPTED,
                        )
                        .order_by(models.Cashflow.creationDate.desc())
                        .first()
                    )
                    if last_cashflow:
                        last_cashflow_age = (datetime.datetime.utcnow() - last_cashflow.creationDate).days
                    else:
                        last_cashflow_age = 0

                    if (
                        last_cashflow_age < conf.DEBIT_NOTE_AGE_THRESHOLD_FOR_CASHFLOW
                        and not override_incident_debit_note
                    ):
                        for incident in all_current_incidents:
                            history_api.add_action(
                                history_models.ActionType.FINANCE_INCIDENT_WAIT_FOR_PAYMENT,
                                author=None,
                                finance_incident=incident,
                                comment="Le montant de l’incident est supérieur au montant total des réservations validées. Donc aucun justificatif n’est généré, on attend la prochaine échéance",
                            )

                        continue

                    for incident in all_current_incidents:
                        history_api.add_action(
                            history_models.ActionType.FINANCE_INCIDENT_GENERATE_DEBIT_NOTE,
                            author=None,
                            finance_incident=incident,
                            comment="Une note de débit sera générée dans quelques jours",
                        )

                cashflow = models.Cashflow(
                    batchId=batch_id,
                    bankAccountId=bank_account_id,
                    status=models.CashflowStatus.PENDING,
                    amount=total,
                )
                db.session.add(cashflow)
                db.session.flush()
                links = [
                    models.CashflowPricing(
                        cashflowId=cashflow.id,
                        pricingId=pricing.id,
                    )
                    for pricing in pricings
                ]
                db.session.bulk_save_objects(links)
                # It's possible (but unlikely) that new pricings have
                # been added (1) between the calculation of `total`
                # and the creation of the `CashflowPricing`s; or (2)
                # between the creation of `CashflowPricing` and now.
                # If (1): the cashflow amount will be wrong, which is
                # why we check it below.
                # If (2): calling `mark_as_processed()` on `pricings`
                # would be wrong because it would include pricings
                # that are not linked to any `CashflowPricing`. These
                # pricings would then stay "processed" and never move
                # to "invoiced".
                cashflowed_pricings = db.session.query(models.CashflowPricing).filter_by(cashflowId=cashflow.id)
                _mark_as_processed(
                    {
                        pricing_id
                        for (pricing_id,) in cashflowed_pricings.with_entities(models.CashflowPricing.pricingId)
                    }
                )
                total_from_pricings = (
                    cashflowed_pricings.join(models.Pricing).with_entities(sa.func.sum(models.Pricing.amount)).scalar()
                    or 0
                )
                if cashflow.amount != total_from_pricings:
                    # We rollback (because we would not want such an
                    # inconsistency in the database) so there is
                    # nothing to fix... but the error is quite
                    # unlikely to happen (see comment above), so it
                    # warrants an analysis (hence the ERROR log level
                    # and not INFO).
                    logger.error(
                        "Cashflow amount is different from the sum of its pricings, changes have been rolled back",
                        extra={
                            "cashflow_id": cashflow.id,
                            "cashflow_amount": cashflow.amount,
                            "total_from_pricings": total_from_pricings,
                        }
                        | log_extra,
                    )
                    db.session.rollback()
                    continue
                db.session.commit()
                elapsed = time.perf_counter() - start
                logger.info("Generated cashflow", extra=log_extra | {"elapsed": elapsed})
        except Exception:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception("Could not generate cashflow for bank account %d", bank_account_id, extra=log_extra)


def generate_payment_files(batch: models.CashflowBatch) -> None:
    """Generate all payment files that are related to the requested
    CashflowBatch and mark all related Cashflow as ``UNDER_REVIEW``.
    """
    logger.info("Generating payment files")
    not_pending_cashflows = (
        db.session.query(models.Cashflow)
        .filter(
            models.Cashflow.batchId == batch.id,
            models.Cashflow.status != models.CashflowStatus.PENDING,
        )
        .count()
    )
    if not_pending_cashflows:
        raise ValueError(
            f"Refusing to generate payment files for {batch.id}, "
            f"because {not_pending_cashflows} cashflows are not pending",
        )

    file_paths = {}
    logger.info("Generating bank accounts file")
    file_paths["bank_accounts"] = _generate_bank_accounts_file(batch.cutoff)

    logger.info("Generating legacy bank accounts file")
    file_paths["legacy_bank_accounts"] = _generate_legacy_bank_accounts_file(batch.cutoff)

    logger.info("Generating payments file")
    file_paths["payments"] = _generate_payments_file(batch)

    logger.info(
        "Finance files have been generated",
        extra={"paths": [str(path) for path in file_paths.values()]},
    )
    drive_folder_name = _get_drive_folder_name(batch)
    _upload_files_to_google_drive(drive_folder_name, file_paths.values())

    logger.info("Updating cashflow status")
    db.session.execute(
        sa.text(
            """
        WITH updated AS (
          UPDATE cashflow
          SET status = :under_review
          WHERE "batchId" = :batch_id AND status = :pending
          RETURNING id AS cashflow_id
        )
        INSERT INTO cashflow_log
            ("cashflowId", "statusBefore", "statusAfter")
            SELECT updated.cashflow_id, 'pending', 'under review' FROM updated
    """
        ),
        params={
            "batch_id": batch.id,
            "pending": models.CashflowStatus.PENDING.value,
            "under_review": models.CashflowStatus.UNDER_REVIEW.value,
        },
    )
    db.session.commit()
    logger.info("Updated cashflow status")


def _get_drive_folder_name(batch: models.CashflowBatch) -> str:
    """Return the name of the directory (on Google Drive) that holds
    finance files for the requested cashflow batch.

    Looks like "2022-03 - jusqu'au 15 mars".
    """
    last_day = pytz.utc.localize(batch.cutoff).astimezone(utils.ACCOUNTING_TIMEZONE).date() - datetime.timedelta(days=1)
    return "{year}-{month:02} - jusqu'au {day} {month_name}".format(
        year=last_day.year,
        month=last_day.month,
        day=last_day.day,
        month_name=date_utils.MONTHS_IN_FRENCH[last_day.month],
    )


def _upload_files_to_google_drive(folder_name: str, paths: typing.Iterable[pathlib.Path]) -> None:
    """Upload finance files (linked to cashflow generation) to a new
    directory on Google Drive.
    """
    gdrive_api = googledrive.get_backend()
    try:
        parent_folder_id = gdrive_api.get_or_create_folder(
            parent_folder_id=settings.FINANCE_GOOGLE_DRIVE_ROOT_FOLDER_ID,
            name=folder_name,
        )
    except Exception as exc:
        logger.exception(
            "Could not create folder and upload finance files to Google Drive",
            extra={"exc": exc},
        )
        return
    for path in paths:
        try:
            gdrive_api.create_file(parent_folder_id, path.name, path)
        except Exception as exc:
            logger.exception(
                "Could not upload finance file to Google Drive",
                extra={
                    "path": str(path),
                    "exc": str(exc),
                },
            )
        else:
            logger.info("Finance file has been uploaded to Google Drive", extra={"path": str(path)})


def _write_csv(
    filename_base: str,
    header: typing.Iterable,
    rows: typing.Iterable,
    row_formatter: typing.Callable[[typing.Iterable], typing.Iterable] = lambda row: row,
    compress: bool = False,
) -> pathlib.Path:
    local_now = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(utils.ACCOUNTING_TIMEZONE)
    filename = filename_base + local_now.strftime("_%Y%m%d_%H%M") + ".csv"
    # Store file in a dedicated directory within "/tmp". It's easier
    # to clean files in tests that way.
    path = pathlib.Path(tempfile.mkdtemp()) / filename
    with open(path, "w+", encoding="utf-8") as fp:
        writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(header)
        if rows is not None:
            writer.writerows(row_formatter(row) for row in rows)
    if compress:
        compressed_path = pathlib.Path(str(path) + ".zip")
        with zipfile.ZipFile(
            compressed_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as zfile:
            zfile.write(path, arcname=path.name)
        path = compressed_path
    return path


def _row_formatter(row: typing.Any) -> tuple:
    return (
        "",
        "True",
        "False",
        str(row.id),
        _clean_for_accounting(f"{row.offerer_name} - {row.label}"),
        "A",
        "ACTEURCULT",
        "30J",
        "15J",
        "EUR",
        "SPOT",
        "",
        "",
        "",
        "",
        "",
        "fr-FR",
        _clean_for_accounting(row.offerer_street),
        "",
        _clean_for_accounting(row.offerer_city),
        "FR",
        "",
        _clean_for_accounting(row.offerer_postal_code),
        "VSEPA",
        _clean_for_accounting(row.iban),
        "",
        "",
        _clean_for_accounting(row.bic),
        _clean_for_accounting(row.offerer_siren),
        "",
        "EXO",
    )


def _generate_bank_accounts_file(cutoff: datetime.datetime) -> pathlib.Path:
    header = (
        "Numéro",
        "Actif",
        "Traité",
        "Identifiant des coordonnées bancaires",
        "Nom du fournisseur - Libellé des coordonnées bancaires",
        "Statut",
        "Famille de fournisseurs",
        "Condition de règlement",
        "Cycle du relevé",
        "Devise",
        "Type de taux de change",
        "Courriel",
        "Site web",
        "Téléphone 1",
        "Téléphone 2",
        "Fax",
        "Langue",
        "Adresse 1",
        "Adresse 2",
        "Ville",
        "Pays",
        "Département",
        "Code postal",
        "Mode de règlement bis",
        "IBAN",
        "Compte de trésorerie",
        "Nature économique",
        "BIC",
        "SIREN",
        "Numéro de TVA Intracom",
        "Zone de taxes",
    )
    query = (
        db.session.query(models.BankAccount)
        .filter(
            models.BankAccount.id.in_(
                db.session.query(offerers_models.VenueBankAccountLink)
                .filter(offerers_models.VenueBankAccountLink.timespan.contains(cutoff))
                .with_entities(offerers_models.VenueBankAccountLink.bankAccountId)
            )
        )
        .join(models.BankAccount.offerer)
        .join(models.BankAccount.venueLinks)
        .group_by(
            models.BankAccount.id,
            models.BankAccount.label,
            models.BankAccount.iban,
            models.BankAccount.bic,
            offerers_models.Offerer.name,
            offerers_models.Offerer.siren,
            offerers_models.Offerer.street,
            offerers_models.Offerer.city,
            offerers_models.Offerer.postalCode,
        )
        .order_by(models.BankAccount.id)
    ).with_entities(
        models.BankAccount.id,
        offerers_models.Offerer.name.label("offerer_name"),
        offerers_models.Offerer.siren.label("offerer_siren"),
        offerers_models.Offerer.street.label("offerer_street"),  # type: ignore[attr-defined]
        offerers_models.Offerer.city.label("offerer_city"),
        offerers_models.Offerer.postalCode.label("offerer_postal_code"),
        models.BankAccount.label.label("label"),
        models.BankAccount.iban.label("iban"),
        models.BankAccount.bic.label("bic"),
    )

    return _write_csv("bank_accounts", header, rows=query, row_formatter=_row_formatter)


def _row_formatter_legacy(row: typing.Any) -> tuple:
    return (
        ", ".join(str(venue_id) for venue_id in sorted(row.venue_ids)),
        human_ids.humanize(row.id),
        str(row.id),
        _clean_for_accounting(row.offerer_siren),
        _clean_for_accounting(f"{row.offerer_name} - {row.label}"),
        _clean_for_accounting(row.iban),
        _clean_for_accounting(row.bic),
    )


def _generate_legacy_bank_accounts_file(cutoff: datetime.datetime) -> pathlib.Path:
    header = (
        "Lieux liés au compte bancaire",
        "Identifiant humanisé des coordonnées bancaires",
        "Identifiant des coordonnées bancaires",
        "SIREN de la structure",
        "Nom de la structure - Libellé des coordonnées bancaires",
        "IBAN",
        "BIC",
    )
    query = (
        db.session.query(models.BankAccount)
        .filter(
            models.BankAccount.id.in_(
                db.session.query(offerers_models.VenueBankAccountLink)
                .filter(offerers_models.VenueBankAccountLink.timespan.contains(cutoff))
                .with_entities(offerers_models.VenueBankAccountLink.bankAccountId)
            )
        )
        .join(models.BankAccount.offerer)
        .join(models.BankAccount.venueLinks)
        .group_by(
            models.BankAccount.id,
            models.BankAccount.label,
            models.BankAccount.iban,
            models.BankAccount.bic,
            offerers_models.Offerer.name,
            offerers_models.Offerer.siren,
        )
        .order_by(models.BankAccount.id)
    ).with_entities(
        models.BankAccount.id,
        sa_func.array_agg(offerers_models.VenueBankAccountLink.venueId.distinct()).label("venue_ids"),
        offerers_models.Offerer.name.label("offerer_name"),
        offerers_models.Offerer.siren.label("offerer_siren"),
        models.BankAccount.label.label("label"),
        models.BankAccount.iban.label("iban"),
        models.BankAccount.bic.label("bic"),
    )

    return _write_csv("legacy_bank_accounts", header, rows=query, row_formatter=_row_formatter_legacy)


def _clean_for_accounting(value: str) -> str:
    if not isinstance(value, str):
        return value
    # Accounting software can't read CSV files properly
    return value.strip().replace('"', "").replace(";", "").replace("\n", "")


def _generate_payments_file(batch: models.CashflowBatch) -> pathlib.Path:
    batch_id = batch.id
    header = [
        "Identifiant humanisé des coordonnées bancaires",
        "Identifiant des coordonnées bancaires",
        "SIREN de la structure",
        "Nom de la structure - Libellé des coordonnées bancaires",
        "Type de réservation",
        "Ministère",
        "Montant net offreur",
    ]

    def get_individual_data(query: BaseQuery) -> BaseQuery:
        individual_data_query = (
            query.filter(bookings_models.Booking.amount != 0)
            .join(bookings_models.Booking.deposit)
            .join(models.Pricing.cashflows)
            .join(
                models.BankAccount,
                models.BankAccount.id == models.Cashflow.bankAccountId,
            )
            .join(models.BankAccount.offerer)
            .filter(models.Cashflow.batchId == batch_id)
            .group_by(
                models.BankAccount.id,
                offerers_models.Offerer.id,
                ORIGIN_OF_CREDIT_CASE,
            )
            .with_entities(
                models.BankAccount.id.label("bank_account_id"),
                models.BankAccount.label.label("bank_account_label"),
                offerers_models.Offerer.name.label("offerer_name"),
                sa.case(
                    (offerers_models.Offerer.is_caledonian == True, offerers_models.Offerer.rid7),
                    else_=offerers_models.Offerer.siren,
                ).label("offerer_siren"),
                ORIGIN_OF_CREDIT_CASE.label("origin_of_credit"),
                sa.case((offerers_models.Offerer.is_caledonian == True, "NC"), else_=None).label("caledonian_label"),
                sa_func.sum(models.Pricing.amount).label("pricing_amount"),
            )
        )

        return individual_data_query

    def get_collective_data(query: BaseQuery) -> BaseQuery:
        return (
            query.join(educational_models.CollectiveBooking.collectiveStock)
            .join(models.Pricing.cashflows)
            .join(
                models.BankAccount,
                models.BankAccount.id == models.Cashflow.bankAccountId,
            )
            .join(models.BankAccount.offerer)
            .join(educational_models.CollectiveBooking.educationalInstitution)
            .join(
                educational_models.EducationalDeposit,
                sa.and_(
                    educational_models.EducationalDeposit.educationalYearId
                    == educational_models.CollectiveBooking.educationalYearId,
                    educational_models.EducationalDeposit.educationalInstitutionId
                    == educational_models.EducationalInstitution.id,
                ),
            )
            # max 1 program because of unique constraint on EducationalInstitutionProgramAssociation.institutionId
            .outerjoin(
                educational_models.EducationalInstitutionProgramAssociation,
                sa.and_(
                    educational_models.EducationalInstitutionProgramAssociation.institutionId
                    == educational_models.EducationalInstitution.id,
                    educational_models.EducationalInstitutionProgramAssociation.timespan.contains(
                        educational_models.CollectiveStock.startDatetime
                    ),
                ),
            )
            .outerjoin(educational_models.EducationalInstitutionProgramAssociation.program)
            .filter(models.Cashflow.batchId == batch_id)
            .group_by(
                models.BankAccount.id,
                offerers_models.Offerer.id,
                educational_models.EducationalDeposit.ministry,
                educational_models.EducationalInstitutionProgram.id,
            )
            .with_entities(
                models.BankAccount.id.label("bank_account_id"),
                models.BankAccount.label.label("bank_account_label"),
                offerers_models.Offerer.name.label("offerer_name"),
                offerers_models.Offerer.siren.label("offerer_siren"),
                sa.func.coalesce(
                    educational_models.EducationalInstitutionProgram.label,
                    educational_models.EducationalInstitutionProgram.name,
                    educational_models.EducationalDeposit.ministry.cast(sa.String),
                ).label("ministry"),
                sa_func.sum(models.Pricing.amount).label("pricing_amount"),
            )
        )

    indiv_query = get_individual_data(
        db.session.query(models.Pricing).filter_by(status=models.PricingStatus.PROCESSED).join(models.Pricing.booking)
    )

    indiv_incident_query = get_individual_data(
        db.session.query(models.Pricing)
        .filter_by(status=models.PricingStatus.PROCESSED)
        .join(models.Pricing.event)
        .join(models.FinanceEvent.bookingFinanceIncident)
        .join(models.BookingFinanceIncident.booking)
    )

    indiv_data = (
        indiv_query.union_all(indiv_incident_query)
        .group_by(
            sa.column("bank_account_id"),
            sa.column("bank_account_label"),
            sa.column("offerer_name"),
            sa.column("offerer_siren"),
            sa.column("origin_of_credit"),
            sa.column("caledonian_label"),
        )
        .with_entities(
            sa.column("bank_account_id"),
            sa.column("bank_account_label"),
            sa.column("offerer_name"),
            sa.column("offerer_siren"),
            sa.column("origin_of_credit"),
            sa.column("caledonian_label"),
            sa_func.sum(sa.column("pricing_amount")).label("pricing_amount"),
        )
        .all()
    )

    collective_query = get_collective_data(
        db.session.query(models.Pricing)
        .filter_by(status=models.PricingStatus.PROCESSED)
        .join(models.Pricing.collectiveBooking)
    )

    collective_incident_query = get_collective_data(
        db.session.query(models.Pricing)
        .filter_by(status=models.PricingStatus.PROCESSED)
        .join(models.Pricing.event)
        .join(models.FinanceEvent.bookingFinanceIncident)
        .join(models.BookingFinanceIncident.collectiveBooking)
    )

    collective_data = (
        collective_query.union_all(collective_incident_query)
        .group_by(
            sa.column("bank_account_id"),
            sa.column("bank_account_label"),
            sa.column("offerer_name"),
            sa.column("offerer_siren"),
            sa.column("ministry"),
        )
        .with_entities(
            sa.column("bank_account_id"),
            sa.column("bank_account_label"),
            sa.column("offerer_name"),
            sa.column("offerer_siren"),
            sa.column("ministry"),
            sa_func.sum(sa.column("pricing_amount")).label("pricing_amount"),
        )
        .all()
    )

    return _write_csv(
        f"down_payment_{batch.label}",
        header,
        rows=itertools.chain(indiv_data, collective_data),
        row_formatter=_payment_details_row_formatter,
    )


def _payment_details_row_formatter(sql_row: typing.Any) -> tuple:
    if hasattr(sql_row, "ministry"):
        booking_type = "EACC"
    elif hasattr(sql_row, "origin_of_credit"):
        booking_type = sql_row.origin_of_credit
    else:
        raise ValueError("Unknown booking type (not educational nor individual)")

    ministry = getattr(sql_row, "caledonian_label", getattr(sql_row, "ministry", ""))
    net_amount = utils.cents_to_full_unit(-sql_row.pricing_amount)

    return (
        human_ids.humanize(sql_row.bank_account_id),
        str(sql_row.bank_account_id),
        _clean_for_accounting(sql_row.offerer_siren),
        _clean_for_accounting(f"{sql_row.offerer_name} - {sql_row.bank_account_label}"),
        booking_type,
        ministry,
        net_amount,
    )


def find_reimbursement_rule(rule_reference: str | int) -> models.ReimbursementRule:
    # regular rule description
    if isinstance(rule_reference, str):
        for regular_rule in reimbursement.REGULAR_RULES:
            if rule_reference == regular_rule.description:
                return regular_rule
    # CustomReimbursementRule.id
    return db.session.query(models.CustomReimbursementRule).get(rule_reference)


def _make_invoice_lines(
    group: models.RuleGroup, pricings: list, line_rate: decimal.Decimal | None
) -> list[models.InvoiceLine]:
    totals = {
        "bookings": {
            "offerer_contribution": 0,
            "offerer_revenue": 0,
            "pass_culture_commission": 0,
        },
        "commercial_gestures": {
            "offerer_contribution": 0,
            "offerer_revenue": 0,
            "pass_culture_commission": 0,
        },
        "incidents": {
            "offerer_contribution": 0,
            "offerer_revenue": 0,
            "pass_culture_commission": 0,
        },
    }
    titles = {"bookings": "Réservations", "commercial_gestures": "Gestes commerciaux", "incidents": "Incidents"}
    for pricing in pricings:
        for line in pricing.lines:
            if line.category == models.PricingLineCategory.OFFERER_CONTRIBUTION:
                if pricing.event.bookingFinanceIncidentId:
                    totals["incidents"]["offerer_contribution"] += line.amount
                else:
                    totals["bookings"]["offerer_contribution"] += line.amount
            elif line.category == models.PricingLineCategory.OFFERER_REVENUE:
                if pricing.event.bookingFinanceIncidentId:
                    totals["incidents"]["offerer_revenue"] += line.amount
                else:
                    totals["bookings"]["offerer_revenue"] += line.amount
            elif line.category == models.PricingLineCategory.PASS_CULTURE_COMMISSION:
                if pricing.event.bookingFinanceIncidentId:
                    totals["incidents"]["pass_culture_commission"] += line.amount
                else:
                    totals["bookings"]["pass_culture_commission"] += line.amount
            elif line.category == models.PricingLineCategory.COMMERCIAL_GESTURE:
                totals["commercial_gestures"]["offerer_revenue"] += line.amount
            else:
                raise ValueError(f"Unknown value for pricing line category: {line.category}")

    lines = []
    for label, totals_for_label in totals.items():
        if all(amount == 0 for amount in totals_for_label.values()):
            continue
        reimbursed_amount = sum(totals_for_label.values())
        if offerer_revenue := totals_for_label["offerer_revenue"]:
            # A rate is calculated for this line if we are using a
            # CustomRule with an amount instead of a rate.
            rate = line_rate or (decimal.Decimal(reimbursed_amount) / decimal.Decimal(offerer_revenue)).quantize(
                decimal.Decimal("0.0001")
            )
        else:
            rate = decimal.Decimal(0)

        invoice_line = models.InvoiceLine(
            label=titles[label],
            group=group.value,
            contributionAmount=totals_for_label["offerer_contribution"],
            reimbursedAmount=reimbursed_amount,
            rate=rate,
        )
        lines.append(invoice_line)

    return lines


def _filter_invoiceable_cashflows(query: BaseQuery) -> BaseQuery:
    return (
        query.filter(models.Cashflow.status == models.CashflowStatus.UNDER_REVIEW)
        .outerjoin(
            models.InvoiceCashflow,
            models.InvoiceCashflow.cashflowId == models.Cashflow.id,
        )
        # There should not be any invoice linked to a cashflow that is
        # UNDER_REVIEW, but having a safety belt here is almost free.
        .filter(models.InvoiceCashflow.invoiceId.is_(None))
    )


def _mark_free_pricings_as_invoiced() -> None:
    free_pricings = (
        db.session.query(models.Pricing)
        .outerjoin(models.CashflowPricing)
        # All the PROCESSED pricings without any Cashflow are free pricings
        .filter(
            models.Pricing.status == models.PricingStatus.PROCESSED,
            models.CashflowPricing.pricingId.is_(None),
        )
        .with_entities(models.Pricing.id, models.Pricing.bookingId)
        .all()
    )
    if not free_pricings:
        return

    pricing_ids = {e[0] for e in free_pricings}
    with log_elapsed(logger, "Updating status of free pricings"):
        db.session.execute(
            sa.text(
                """
                WITH updated AS (
                  UPDATE pricing
                  SET status = :invoiced
                  WHERE
                    pricing.id IN :pricing_ids
                  RETURNING id AS pricing_id
                )
                INSERT INTO pricing_log
                ("pricingId", "statusBefore", "statusAfter", reason)
                SELECT updated.pricing_id, :processed, :invoiced, :log_reason from updated
            """
            ),
            {
                "processed": models.PricingStatus.PROCESSED.value,
                "invoiced": models.PricingStatus.INVOICED.value,
                "log_reason": models.PricingLogReason.GENERATE_INVOICE.value,
                "pricing_ids": tuple(pricing_ids),
            },
        )

    # Booking.status: USED -> REIMBURSED (but keep CANCELLED as is)
    with log_elapsed(logger, "Updating status of free individual bookings"):
        booking_ids = [e[1] for e in free_pricings if e[1]]
        for chunk in get_chunks(booking_ids, 1000):
            db.session.execute(
                sa.text(
                    """
                UPDATE booking
                SET
                  status =
                    CASE WHEN booking.status = CAST(:cancelled AS booking_status)
                    THEN CAST(:cancelled AS booking_status)
                    ELSE CAST(:reimbursed AS booking_status)
                    END,
                  "reimbursementDate" = now()
                WHERE
                  booking.id IN :booking_ids
                """
                ),
                {
                    "cancelled": bookings_models.BookingStatus.CANCELLED.value,
                    "reimbursed": bookings_models.BookingStatus.REIMBURSED.value,
                    "booking_ids": tuple(chunk),
                },
            )

    # CollectiveBooking.status: USED -> REIMBURSED (but keep CANCELLED as is)
    with log_elapsed(logger, "Updating status of free collective bookings"):
        db.session.execute(
            sa.text(
                """
            UPDATE collective_booking
            SET
            status =
                CASE WHEN collective_booking.status = CAST(:cancelled AS bookingstatus)
                THEN CAST(:cancelled AS bookingstatus)
                ELSE CAST(:reimbursed AS bookingstatus)
                END,
            "reimbursementDate" = now()
            FROM pricing
            WHERE
                collective_booking.id = pricing."collectiveBookingId"
            AND pricing.id IN :pricing_ids
            """
            ),
            {
                "cancelled": bookings_models.BookingStatus.CANCELLED.value,
                "reimbursed": bookings_models.BookingStatus.REIMBURSED.value,
                "pricing_ids": tuple(pricing_ids),
                "reimbursement_date": datetime.datetime.utcnow(),
            },
        )


def _get_cashflows_by_bank_accounts(batch: models.CashflowBatch, only_debit_notes: bool = False) -> list:
    query = _filter_invoiceable_cashflows(
        db.session.query(
            models.Cashflow.bankAccountId.label("bank_account_id"),
            sa_func.array_agg(models.Cashflow.id).label("cashflow_ids"),
        )
    ).filter(models.Cashflow.batchId == batch.id)

    query = query.filter(models.Cashflow.amount > 0) if only_debit_notes else query.filter(models.Cashflow.amount <= 0)

    rows = query.group_by(models.Cashflow.bankAccountId).all()

    return rows


def generate_invoices_and_debit_notes(batch: models.CashflowBatch) -> None:
    """Generate and store all invoices and debit notes."""
    invoice_rows = [(False, row) for row in _get_cashflows_by_bank_accounts(batch)]
    debit_note_rows = [(True, row) for row in _get_cashflows_by_bank_accounts(batch, only_debit_notes=True)]

    if not invoice_rows and not debit_note_rows:
        raise exceptions.NoInvoiceToGenerate()

    _mark_free_pricings_as_invoiced()

    for is_debit_note, row in invoice_rows + debit_note_rows:
        try:
            with transaction():
                extra = {"bank_account_id": row.bank_account_id}
                message = "Generated and send debit note" if is_debit_note else "Generated and sent invoice"
                with log_elapsed(logger, message, extra):
                    generate_and_store_invoice(
                        bank_account_id=row.bank_account_id,
                        cashflow_ids=row.cashflow_ids,
                        is_debit_note=is_debit_note,
                    )
        except Exception:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not generate debit note" if is_debit_note else "Could not generate invoice",
                extra={
                    "bank_account_id": row.bank_account_id,
                    "cashflow_ids": row.cashflow_ids,
                },
            )

    # TODO: remove csv generation once migration to the new finance tool is finalized
    with log_elapsed(logger, "Generated CSV invoices file"):
        path = generate_invoice_file(batch)
    drive_folder_name = _get_drive_folder_name(batch)
    with log_elapsed(logger, "Uploaded CSV invoices file to Google Drive"):
        _upload_files_to_google_drive(drive_folder_name, [path])


def generate_invoices_and_debit_notes_legacy(batch: models.CashflowBatch) -> None:
    """Generate and store all invoices and debit notes."""
    invoice_rows = [(False, row) for row in _get_cashflows_by_bank_accounts(batch)]
    debit_note_rows = [(True, row) for row in _get_cashflows_by_bank_accounts(batch, only_debit_notes=True)]

    if not invoice_rows and not debit_note_rows:
        raise exceptions.NoInvoiceToGenerate()

    _mark_free_pricings_as_invoiced()

    for is_debit_note, row in invoice_rows + debit_note_rows:
        try:
            with transaction():
                extra = {"bank_account_id": row.bank_account_id}
                with log_elapsed(logger, "Generated and sent invoice", extra):
                    generate_and_store_invoice_legacy(
                        bank_account_id=row.bank_account_id,
                        cashflow_ids=row.cashflow_ids,
                        is_debit_note=is_debit_note,
                    )
        except Exception:
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not generate debit note" if is_debit_note else "Could not generate invoice",
                extra={
                    "bank_account_id": row.bank_account_id,
                    "cashflow_ids": row.cashflow_ids,
                },
            )

    with log_elapsed(logger, "Generated CSV invoices file"):
        path = generate_invoice_file(batch)
    drive_folder_name = _get_drive_folder_name(batch)
    with log_elapsed(logger, "Uploaded CSV invoices file to Google Drive"):
        _upload_files_to_google_drive(drive_folder_name, [path])


def generate_invoice_file(batch: models.CashflowBatch) -> pathlib.Path:
    header = [
        "Identifiant humanisé des coordonnées bancaires",
        "Identifiant des coordonnées bancaires",
        "Date du justificatif",
        "Référence du justificatif",
        "Type de ticket de facturation",
        "Type de réservation",
        "Ministère",
        "Somme des tickets de facturation",
    ]

    def get_data(query: BaseQuery, bank_accounts: typing.Iterable[int]) -> BaseQuery:
        return (
            query.join(models.Pricing.lines)
            .join(bookings_models.Booking.deposit)
            .join(models.Invoice.bankAccount)
            .join(models.BankAccount.offerer)
            .filter(
                models.Cashflow.batchId == batch.id,
                models.Invoice.bankAccountId.in_(bank_accounts),
            )
            .group_by(
                models.Invoice.id,
                models.Invoice.date,
                models.Invoice.reference,
                models.Invoice.bankAccountId,
                models.PricingLine.category,
                offerers_models.Offerer.is_caledonian,
                ORIGIN_OF_CREDIT_CASE,
            )
            .with_entities(
                models.Invoice.id,
                models.Invoice.date.label("invoice_date"),
                models.Invoice.reference.label("invoice_reference"),
                models.Invoice.bankAccountId.label("bank_account_id"),
                models.PricingLine.category.label("pricing_line_category"),
                ORIGIN_OF_CREDIT_CASE.label("origin_of_credit"),
                sa.case((offerers_models.Offerer.is_caledonian == True, "NC"), else_=None).label("ministry"),
                sa_func.sum(models.PricingLine.amount).label("pricing_line_amount"),
            )
        )

    def get_collective_data(query: BaseQuery, bank_accounts: typing.Iterable[int]) -> BaseQuery:
        return (
            query.join(models.Pricing.lines)
            .join(educational_models.CollectiveBooking.collectiveStock)
            .join(educational_models.CollectiveBooking.educationalInstitution)
            .join(
                educational_models.EducationalDeposit,
                sa.and_(
                    educational_models.EducationalDeposit.educationalYearId
                    == educational_models.CollectiveBooking.educationalYearId,
                    educational_models.EducationalDeposit.educationalInstitutionId
                    == educational_models.EducationalInstitution.id,
                ),
            )
            # max 1 program because of unique constraint on EducationalInstitutionProgramAssociation.institutionId
            .outerjoin(
                educational_models.EducationalInstitutionProgramAssociation,
                sa.and_(
                    educational_models.EducationalInstitutionProgramAssociation.institutionId
                    == educational_models.EducationalInstitution.id,
                    educational_models.EducationalInstitutionProgramAssociation.timespan.contains(
                        educational_models.CollectiveStock.startDatetime
                    ),
                ),
            )
            .outerjoin(
                educational_models.EducationalInstitutionProgramAssociation.program,
            )
            .filter(
                models.Cashflow.batchId == batch.id,
                models.Invoice.bankAccountId.in_(bank_accounts),
            )
            .group_by(
                models.Invoice.id,
                models.Invoice.date,
                models.Invoice.reference,
                models.Invoice.bankAccountId,
                models.PricingLine.category,
                educational_models.EducationalDeposit.ministry,
                educational_models.EducationalInstitutionProgram.id,
            )
            .with_entities(
                models.Invoice.id,
                models.Invoice.date.label("invoice_date"),
                models.Invoice.reference.label("invoice_reference"),
                models.Invoice.bankAccountId.label("bank_account_id"),
                models.PricingLine.category.label("pricing_line_category"),
                sa.func.coalesce(
                    educational_models.EducationalInstitutionProgram.label,
                    educational_models.EducationalInstitutionProgram.name,
                    educational_models.EducationalDeposit.ministry.cast(sa.String),
                ).label("ministry"),
                sa_func.sum(models.PricingLine.amount).label("pricing_line_amount"),
            )
        )

    bank_accounts_query = (
        db.session.query(models.Invoice)
        .with_entities(models.Invoice.bankAccountId)
        .join(models.Invoice.cashflows)
        .filter(models.Cashflow.batchId == batch.id)
    )
    bank_accounts = [i.bankAccountId for i in bank_accounts_query]
    indiv_data = []
    collective_data = []
    chunk_size = 100
    for i in range(0, len(bank_accounts), chunk_size):
        bank_accounts_chunk = bank_accounts[i : i + chunk_size]

        indiv_query = get_data(
            db.session.query(models.Invoice)
            .join(models.Invoice.cashflows)
            .join(models.Cashflow.pricings)
            .join(models.Pricing.booking),
            bank_accounts_chunk,
        )
        indiv_incident_query = get_data(
            db.session.query(models.Invoice)
            .join(models.Invoice.cashflows)
            .join(models.Cashflow.pricings)
            .join(models.Pricing.event)
            .join(models.FinanceEvent.bookingFinanceIncident)
            .join(models.BookingFinanceIncident.booking),
            bank_accounts_chunk,
        )

        indiv_data.extend(
            indiv_query.union(indiv_incident_query)
            .group_by(
                sa.column("invoice_date"),
                sa.column("invoice_reference"),
                sa.column("bank_account_id"),
                sa.column("pricing_line_category"),
                sa.column("origin_of_credit"),
                sa.column("ministry"),
            )
            .with_entities(
                sa.column("invoice_date"),
                sa.column("invoice_reference"),
                sa.column("bank_account_id"),
                sa.column("pricing_line_category"),
                sa.column("origin_of_credit"),
                sa.column("ministry"),
                sa_func.sum(sa.column("pricing_line_amount")).label("pricing_line_amount"),
            )
            .all()
        )

        collective_query = get_collective_data(
            db.session.query(models.Invoice)
            .join(models.Invoice.cashflows)
            .join(models.Cashflow.pricings)
            .join(models.Pricing.collectiveBooking),
            bank_accounts_chunk,
        )

        collective_incident_query = get_collective_data(
            db.session.query(models.Invoice)
            .join(models.Invoice.cashflows)
            .join(models.Cashflow.pricings)
            .join(models.Pricing.event)
            .join(models.FinanceEvent.bookingFinanceIncident)
            .join(models.BookingFinanceIncident.collectiveBooking),
            bank_accounts_chunk,
        )

        collective_data.extend(
            collective_query.union(collective_incident_query)
            .group_by(
                sa.column("invoice_date"),
                sa.column("invoice_reference"),
                sa.column("bank_account_id"),
                sa.column("pricing_line_category"),
                sa.column("ministry"),
            )
            .with_entities(
                sa.column("invoice_date"),
                sa.column("invoice_reference"),
                sa.column("bank_account_id"),
                sa.column("pricing_line_category"),
                sa.column("ministry"),
                sa_func.sum(sa.column("pricing_line_amount")).label("pricing_line_amount"),
            )
            .all()
        )

    pricing_line_dict = {}

    for index, category in enumerate(sorted([e.value for e in models.PricingLineCategory], reverse=True)):
        pricing_line_dict[category] = index

    indiv_data = sorted(
        indiv_data,
        key=lambda o: (
            o.invoice_reference,
            o.origin_of_credit,
            pricing_line_dict[o.pricing_line_category],
        ),
    )
    collective_data = sorted(
        collective_data,
        key=lambda o: (o.invoice_reference, o.ministry, pricing_line_dict[o.pricing_line_category]),
    )
    return _write_csv(
        f"invoices_{batch.label}",
        header,
        rows=itertools.chain(indiv_data, collective_data),
        row_formatter=_invoice_row_formatter,
        compress=True,
    )


def _invoice_row_formatter(sql_row: typing.Any) -> tuple:
    if sql_row.ministry and sql_row.ministry != "NC":
        booking_type = "EACC"
    elif hasattr(sql_row, "origin_of_credit"):
        booking_type = sql_row.origin_of_credit
    else:
        raise ValueError("Unknown booking type (not educational nor individual)")

    ministry = getattr(sql_row, "ministry", "")

    return (
        human_ids.humanize(sql_row.bank_account_id),
        str(sql_row.bank_account_id),
        sql_row.invoice_date.date().isoformat(),
        sql_row.invoice_reference,
        sql_row.pricing_line_category,
        booking_type,
        ministry,
        sql_row.pricing_line_amount,
    )


def generate_and_store_invoice(bank_account_id: int, cashflow_ids: list[int], is_debit_note: bool = False) -> None:
    log_extra = {"bank_account": bank_account_id}
    with log_elapsed(logger, "Generated invoice model instance", log_extra):
        invoice = _generate_invoice(
            bank_account_id=bank_account_id, cashflow_ids=cashflow_ids, is_debit_note=is_debit_note
        )
        if not invoice:
            return

    # The cashflows all come from the same cashflow batch,
    # so batch_id should be the same for every cashflow
    batch = (
        db.session.query(models.CashflowBatch)
        .join(models.Cashflow.batch)
        .join(models.Cashflow.invoices)
        .filter(models.Invoice.id == invoice.id)
    ).one()

    with log_elapsed(logger, "Generated invoice HTML", log_extra):
        if is_debit_note:
            invoice_html = _generate_debit_note_html(invoice, batch)
        else:
            invoice_html = _generate_invoice_html(invoice, batch)
    with log_elapsed(logger, "Generated and stored PDF invoice", log_extra):
        _store_invoice_pdf(invoice_storage_id=invoice.storage_object_id, invoice_html=invoice_html)
    with log_elapsed(logger, "Sent invoice", log_extra):
        transactional_mails.send_invoice_available_to_pro_email(invoice, batch)


def generate_and_store_invoice_legacy(
    bank_account_id: int, cashflow_ids: list[int], is_debit_note: bool = False
) -> None:
    log_extra = {"bank_account": bank_account_id}
    with log_elapsed(logger, "Generated invoice model instance", log_extra):
        invoice = _generate_invoice_legacy(
            bank_account_id=bank_account_id, cashflow_ids=cashflow_ids, is_debit_note=is_debit_note
        )
        if not invoice:
            return

    # The cashflows all come from the same cashflow batch,
    # so batch_id should be the same for every cashflow
    batch = (
        db.session.query(models.CashflowBatch)
        .join(models.Cashflow.batch)
        .join(models.Cashflow.invoices)
        .filter(models.Invoice.id == invoice.id)
    ).one()

    with log_elapsed(logger, "Generated invoice HTML", log_extra):
        if is_debit_note:
            invoice_html = _generate_debit_note_html(invoice, batch)
        else:
            invoice_html = _generate_invoice_html(invoice, batch)
    with log_elapsed(logger, "Generated and stored PDF invoice", log_extra):
        _store_invoice_pdf(invoice_storage_id=invoice.storage_object_id, invoice_html=invoice_html)
    with log_elapsed(logger, "Sent invoice", log_extra):
        transactional_mails.send_invoice_available_to_pro_email(invoice, batch)


def _generate_invoice_legacy(
    bank_account_id: int, cashflow_ids: list[int], is_debit_note: bool = False
) -> models.Invoice | None:
    assert not feature.FeatureToggle.WIP_ENABLE_NEW_FINANCE_WORKFLOW
    # Acquire lock to avoid 2 simultaneous calls to this function (on
    # the same bank account) generating 2 duplicate invoices.
    # This is also why we call `_filter_invoiceable_cashflows()` again
    # below : the function will process the requested cashflows only
    # in the first call
    lock_bank_account(bank_account_id)
    invoice = models.Invoice(
        bankAccountId=bank_account_id,
    )
    cashflows = _filter_invoiceable_cashflows(
        db.session.query(models.Cashflow)
        .filter(models.Cashflow.id.in_(cashflow_ids))
        .options(
            sa_orm.joinedload(models.Cashflow.pricings)
            .options(sa_orm.joinedload(models.Pricing.lines))
            .options(sa_orm.joinedload(models.Pricing.customRule))
            .options(
                sa_orm.joinedload(models.Pricing.event, innerjoin=True).joinedload(
                    models.FinanceEvent.bookingFinanceIncident
                )
            )
        )
    ).all()
    if not cashflows:
        # We should not end up here unless another instance of the
        # `generate_invoices` command is being executed simultaneously
        # and it has already processed this bank account.
        return None
    pricings_and_rates_by_rule_group = defaultdict(list)
    pricings_by_custom_rule = defaultdict(list)

    for pricing in sum([cf.pricings for cf in cashflows], []):
        rule_reference = pricing.standardRule or pricing.customRuleId
        rule = find_reimbursement_rule(rule_reference)
        if isinstance(rule, models.CustomReimbursementRule):
            pricings_by_custom_rule[rule].append(pricing)
        else:
            pricings_and_rates_by_rule_group[rule.group].append((pricing, rule.rate))  # type: ignore[attr-defined]

    invoice_lines = []
    for rule_group, pricings_and_rates in pricings_and_rates_by_rule_group.items():
        rates = defaultdict(list)
        for pricing, rate in pricings_and_rates:
            rates[rate].append(pricing)
        for rate, pricings in rates.items():
            invoice_lines += _make_invoice_lines(rule_group, pricings, rate)

    for custom_rule, pricings in pricings_by_custom_rule.items():
        # An InvoiceLine rate will be calculated for a CustomRule with a set reimbursed amount
        invoice_lines += _make_invoice_lines(custom_rule.group, pricings, custom_rule.rate)

    invoice.amount = sum(line.reimbursedAmount for line in invoice_lines)
    invoice.status = models.InvoiceStatus.PAID
    # As of Python 3.9, DEFAULT_ENTROPY is 32 bytes
    invoice.token = secrets.token_urlsafe()
    scheme_name = "invoice.reference" if not is_debit_note else "debit_note.reference"
    scheme = reference_models.ReferenceScheme.get_and_lock(name=scheme_name, year=datetime.date.today().year)
    invoice.reference = scheme.formatted_reference
    scheme.increment_after_use()
    db.session.add(scheme)
    db.session.add(invoice)
    db.session.flush()
    for line in invoice_lines:
        line.invoiceId = invoice.id
    db.session.bulk_save_objects(invoice_lines)
    cf_links = [models.InvoiceCashflow(invoiceId=invoice.id, cashflowId=cashflow.id) for cashflow in cashflows]
    db.session.bulk_save_objects(cf_links)

    # Cashflow.status: UNDER_REVIEW -> ACCEPTED
    with log_elapsed(logger, "Updating status of cashflows"):
        db.session.execute(
            sa.text(
                """
                WITH updated AS (
                  UPDATE cashflow
                  SET status = :accepted
                  WHERE id IN :cashflow_ids
                  RETURNING id AS cashflow_id
                )
                INSERT INTO cashflow_log
                ("cashflowId", "statusBefore", "statusAfter")
                SELECT updated.cashflow_id, :under_review, :accepted FROM updated
                """
            ),
            params={
                "cashflow_ids": tuple(cashflow_ids),
                "accepted": models.CashflowStatus.ACCEPTED.value,
                "under_review": models.CashflowStatus.UNDER_REVIEW.value,
            },
        )

    # Pricing.status: PROCESSED -> INVOICED
    # SQLAlchemy ORM cannot call `update()` if a query has been JOINed.
    with log_elapsed(logger, "Updating status of pricings"):
        db.session.execute(
            sa.text(
                """
                WITH updated AS (
                  UPDATE pricing
                  SET status = :invoiced
                  FROM cashflow_pricing
                  WHERE
                    cashflow_pricing."pricingId" = pricing.id
                    AND cashflow_pricing."cashflowId" IN :cashflow_ids
                  RETURNING id AS pricing_id
                )
                INSERT INTO pricing_log
                ("pricingId", "statusBefore", "statusAfter", reason)
                SELECT updated.pricing_id, :processed, :invoiced, :log_reason from updated
            """
            ),
            {
                "processed": models.PricingStatus.PROCESSED.value,
                "invoiced": models.PricingStatus.INVOICED.value,
                "log_reason": models.PricingLogReason.GENERATE_INVOICE.value,
                "cashflow_ids": tuple(cashflow_ids),
            },
        )

    # Booking.status: USED -> REIMBURSED (but keep CANCELLED as is)
    with log_elapsed(logger, "Updating status of individual bookings"):
        booking_ids = (
            db.session.query(models.Pricing)
            .join(models.Pricing.cashflows)
            .filter(
                models.Cashflow.id.in_(cashflow_ids),
            )
            .with_entities(models.Pricing.bookingId)
            .all()
        )
        booking_ids = [b[0] for b in booking_ids]
        for chunk in get_chunks(booking_ids, 1000):
            db.session.execute(
                sa.text(
                    """
                UPDATE booking
                SET
                  status =
                    CASE WHEN booking.status = CAST(:cancelled AS booking_status)
                    THEN CAST(:cancelled AS booking_status)
                    ELSE CAST(:reimbursed AS booking_status)
                    END,
                  "reimbursementDate" = now()
                WHERE
                  booking.id IN :booking_ids
                """
                ),
                {
                    "cancelled": bookings_models.BookingStatus.CANCELLED.value,
                    "reimbursed": bookings_models.BookingStatus.REIMBURSED.value,
                    "booking_ids": tuple(chunk),
                },
            )

    # CollectiveBooking.status: USED -> REIMBURSED (but keep CANCELLED as is)
    with log_elapsed(logger, "Updating status of collective bookings"):
        db.session.execute(
            sa.text(
                """
            UPDATE collective_booking
            SET
            status =
                CASE WHEN collective_booking.status = CAST(:cancelled AS bookingstatus)
                THEN CAST(:cancelled AS bookingstatus)
                ELSE CAST(:reimbursed AS bookingstatus)
                END,
            "reimbursementDate" = now()
            FROM pricing, cashflow_pricing
            WHERE
                collective_booking.id = pricing."collectiveBookingId"
            AND pricing.id = cashflow_pricing."pricingId"
            AND cashflow_pricing."cashflowId" IN :cashflow_ids
            """
            ),
            {
                "cancelled": bookings_models.BookingStatus.CANCELLED.value,
                "reimbursed": bookings_models.BookingStatus.REIMBURSED.value,
                "cashflow_ids": tuple(cashflow_ids),
                "reimbursement_date": datetime.datetime.utcnow(),
            },
        )

    db.session.commit()
    return invoice


def _generate_invoice(
    bank_account_id: int, cashflow_ids: list[int], is_debit_note: bool = False
) -> models.Invoice | None:
    assert feature.FeatureToggle.WIP_ENABLE_NEW_FINANCE_WORKFLOW
    # Acquire lock to avoid 2 simultaneous calls to this function (on
    # the same bank account) generating 2 duplicate invoices.
    # This is also why we call `_filter_invoiceable_cashflows()` again
    # below : the function will process the requested cashflows only
    # in the first call
    lock_bank_account(bank_account_id)
    invoice = models.Invoice(
        bankAccountId=bank_account_id,
    )
    cashflows = _filter_invoiceable_cashflows(
        db.session.query(models.Cashflow)
        .filter(models.Cashflow.id.in_(cashflow_ids))
        .options(
            sa_orm.joinedload(models.Cashflow.pricings)
            .options(sa_orm.joinedload(models.Pricing.lines))
            .options(sa_orm.joinedload(models.Pricing.customRule))
            .options(
                sa_orm.joinedload(models.Pricing.event, innerjoin=True).joinedload(
                    models.FinanceEvent.bookingFinanceIncident
                )
            )
        )
    ).all()
    if not cashflows:
        # We should not end up here unless another instance of the
        # `generate_invoices` command is being executed simultaneously
        # and it has already processed this bank account.
        return None
    pricings_and_rates_by_rule_group = defaultdict(list)
    pricings_by_custom_rule = defaultdict(list)

    for pricing in sum([cf.pricings for cf in cashflows], []):
        rule_reference = pricing.standardRule or pricing.customRuleId
        rule = find_reimbursement_rule(rule_reference)
        if isinstance(rule, models.CustomReimbursementRule):
            pricings_by_custom_rule[rule].append(pricing)
        else:
            pricings_and_rates_by_rule_group[rule.group].append((pricing, rule.rate))  # type: ignore[attr-defined]

    invoice_lines = []
    for rule_group, pricings_and_rates in pricings_and_rates_by_rule_group.items():
        rates = defaultdict(list)
        for pricing, rate in pricings_and_rates:
            rates[rate].append(pricing)
        for rate, pricings in rates.items():
            invoice_lines += _make_invoice_lines(rule_group, pricings, rate)

    for custom_rule, pricings in pricings_by_custom_rule.items():
        # An InvoiceLine rate will be calculated for a CustomRule with a set reimbursed amount
        invoice_lines += _make_invoice_lines(custom_rule.group, pricings, custom_rule.rate)

    invoice.status = models.InvoiceStatus.PENDING
    invoice.amount = sum(line.reimbursedAmount for line in invoice_lines)
    # As of Python 3.9, DEFAULT_ENTROPY is 32 bytes
    invoice.token = secrets.token_urlsafe()
    scheme_name = "invoice.reference" if not is_debit_note else "debit_note.reference"
    scheme = reference_models.ReferenceScheme.get_and_lock(name=scheme_name, year=datetime.date.today().year)
    invoice.reference = scheme.formatted_reference
    scheme.increment_after_use()
    db.session.add(scheme)
    db.session.add(invoice)
    db.session.flush()
    for line in invoice_lines:
        line.invoiceId = invoice.id
    db.session.bulk_save_objects(invoice_lines)
    cf_links = [models.InvoiceCashflow(invoiceId=invoice.id, cashflowId=cashflow.id) for cashflow in cashflows]
    db.session.bulk_save_objects(cf_links)

    # Cashflow.status: UNDER_REVIEW → PENDING_ACCEPTANCE for new workflow
    with log_elapsed(logger, "Updating status of cashflows"):
        db.session.execute(
            sa.text(
                """
                WITH updated AS (
                  UPDATE cashflow
                  SET status = :pending_acceptance
                  WHERE id IN :cashflow_ids
                  RETURNING id AS cashflow_id
                )
                INSERT INTO cashflow_log
                ("cashflowId", "statusBefore", "statusAfter")
                SELECT updated.cashflow_id, :under_review, :pending_acceptance FROM updated
                """
            ),
            params={
                "cashflow_ids": tuple(cashflow_ids),
                "pending_acceptance": models.CashflowStatus.PENDING_ACCEPTANCE.value,
                "under_review": models.CashflowStatus.UNDER_REVIEW.value,
            },
        )

    db.session.commit()
    return invoice


def get_invoice_period(
    batch_cutoff_date: datetime.datetime,
) -> tuple[datetime.date, datetime.date]:
    if batch_cutoff_date.day < 16:
        start_date = batch_cutoff_date.replace(day=1)
    else:
        start_date = batch_cutoff_date.replace(day=16)
    end_date = batch_cutoff_date

    return start_date.date(), end_date.date()


def _prepare_invoice_context(invoice: models.Invoice, batch: models.CashflowBatch) -> dict:
    # Easier to sort here and not in PostgreSQL, and not much slower
    # because there are very few cashflows (and usually only 1).
    cashflows = sorted(filter(lambda c: c.amount != 0, invoice.cashflows), key=lambda c: (c.creationDate, c.id))
    is_caledonian_invoice = invoice.bankAccount.offerer.is_caledonian

    invoice_lines = sorted(invoice.lines, key=lambda k: (k.group["position"], -k.rate))
    total_used_bookings_amount = 0
    total_contribution_amount = 0
    total_reimbursed_amount = 0
    invoice_groups: dict[str, tuple[dict, list[models.InvoiceLine]]] = {}
    for line in invoice_lines:
        group = line.group
        if line.group["label"] in invoice_groups:
            invoice_groups[line.group["label"]][1].append(line)
        else:
            invoice_groups[line.group["label"]] = (group, [line])

    groups = []
    for group, lines in invoice_groups.values():
        contribution_subtotal = sum(line.contributionAmount for line in lines)
        total_contribution_amount += contribution_subtotal
        reimbursed_amount_subtotal = sum(line.reimbursedAmount for line in lines)
        total_reimbursed_amount += reimbursed_amount_subtotal
        used_bookings_subtotal = sum(line.bookings_amount for line in lines if line.bookings_amount)
        total_used_bookings_amount += used_bookings_subtotal

        invoice_group = models.InvoiceLineGroup(
            position=group["position"],
            label=group["label"],
            contribution_subtotal=contribution_subtotal,
            reimbursed_amount_subtotal=reimbursed_amount_subtotal,
            used_bookings_subtotal=used_bookings_subtotal,
            lines=lines,
        )
        groups.append(invoice_group)
    reimbursements_by_venue = get_reimbursements_by_venue(invoice)

    bank_account = invoice.bankAccount
    if not bank_account:
        raise ValueError("Could not generate invoice without bank account")
    bank_account_label = bank_account.label
    bank_account_iban = bank_account.iban

    if feature.FeatureToggle.WIP_ENABLE_NEW_FINANCE_WORKFLOW.is_active():
        invoice_date = invoice.date.strftime("%d/%m/%Y")
    else:
        invoice_date = (invoice.date + datetime.timedelta(days=2)).strftime("%d/%m/%Y")
    period_start, period_end = get_invoice_period(batch.cutoff)

    return dict(
        invoice=invoice,
        is_caledonian_invoice=is_caledonian_invoice,
        cashflows=cashflows,
        groups=groups,
        bank_account=bank_account,
        bank_account_label=bank_account_label,
        bank_account_iban=bank_account_iban,
        total_used_bookings_amount=total_used_bookings_amount,
        total_contribution_amount=total_contribution_amount,
        total_reimbursed_amount=total_reimbursed_amount,
        invoice_date=invoice_date,
        period_start=period_start,
        period_end=period_end,
        reimbursements_by_venue=reimbursements_by_venue,
        including_finance_incident=any(
            cashflow
            for cashflow in cashflows
            if any(pricing.event.bookingFinanceIncidentId for pricing in cashflow.pricings)
        ),
    )


def get_reimbursements_by_venue(
    invoice: models.Invoice,
) -> typing.ValuesView:
    common_columns: tuple = (offerers_models.Venue.id.label("venue_id"), offerers_models.Venue.common_name)

    pricing_query = (
        db.session.query(models.Invoice)
        .join(models.Invoice.cashflows)
        .join(models.Cashflow.pricings)
        .filter(models.Invoice.id == invoice.id)
    )

    query = (
        pricing_query.with_entities(
            *common_columns,
            models.Pricing.amount.label("pricing_amount"),
            bookings_models.Booking.amount.label("booking_unit_amount"),
            bookings_models.Booking.quantity.label("booking_quantity"),
        )
        .join(models.Pricing.booking)
        .join(bookings_models.Booking.venue)
        .order_by(offerers_models.Venue.id, offerers_models.Venue.common_name)
    )
    incident_query = (
        pricing_query.with_entities(
            *common_columns,
            sa_func.sum(models.Pricing.amount).label("pricing_amount"),
            models.BookingFinanceIncident.newTotalAmount.label("incident_new_total_amount"),
            bookings_models.Booking.quantity.label("booking_quantity"),
            bookings_models.Booking.amount.label("booking_unit_amount"),
        )
        .join(models.Pricing.event)
        .join(models.FinanceEvent.bookingFinanceIncident)
        .join(models.BookingFinanceIncident.booking)
        .join(bookings_models.Booking.venue)
        .group_by(
            offerers_models.Venue.id,
            offerers_models.Venue.common_name,
            models.BookingFinanceIncident.id,
            bookings_models.Booking.id,
        )
        .order_by(offerers_models.Venue.id, offerers_models.Venue.common_name)
    )
    collective_query = (
        pricing_query.with_entities(
            *common_columns,
            sa_func.sum(models.Pricing.amount).label("reimbursed_amount"),
            sa_func.sum(educational_models.CollectiveStock.price).label("booking_amount"),
        )
        .join(models.Pricing.collectiveBooking)
        .join(educational_models.CollectiveBooking.venue)
        .join(educational_models.CollectiveBooking.collectiveStock)
        .group_by(offerers_models.Venue.id, offerers_models.Venue.common_name)
        .order_by(offerers_models.Venue.id, offerers_models.Venue.common_name)
    )
    collective_incident_query = (
        pricing_query.with_entities(
            *common_columns,
            sa_func.sum(models.Pricing.amount).label("pricing_amount"),
            models.BookingFinanceIncident.newTotalAmount.label("incident_new_total_amount"),
            educational_models.CollectiveStock.price.label("booking_amount"),
        )
        .join(models.Pricing.event)
        .join(models.FinanceEvent.bookingFinanceIncident)
        .join(models.BookingFinanceIncident.collectiveBooking)
        .join(educational_models.CollectiveBooking.venue)
        .join(educational_models.CollectiveBooking.collectiveStock)
        .group_by(
            offerers_models.Venue.id,
            offerers_models.Venue.common_name,
            models.BookingFinanceIncident.id,
            educational_models.CollectiveStock.id,
        )
        .order_by(offerers_models.Venue.id, offerers_models.Venue.common_name)
    )

    reimbursements_by_venue = {}
    venue_info_base = {
        "venue_name": "",
        "reimbursed_amount": 0,
        "validated_booking_amount": 0,
        "individual_amount": 0,
        "finance_incident_amount": 0,
        "finance_incident_contribution": 0,
        "individual_incident_amount": 0,
    }
    for (venue_id, venue_common_name), bookings in itertools.groupby(query, lambda x: (x.venue_id, x.common_name)):
        validated_booking_amount = decimal.Decimal(0)
        reimbursed_amount = 0
        individual_amount = 0
        for booking in bookings:
            reimbursed_amount += booking.pricing_amount
            validated_booking_amount += decimal.Decimal(booking.booking_unit_amount) * booking.booking_quantity
            individual_amount += booking.pricing_amount
        reimbursements_by_venue[venue_id] = {
            "venue_name": venue_common_name,
            "reimbursed_amount": reimbursed_amount,
            "validated_booking_amount": -utils.to_cents(validated_booking_amount),
            "individual_amount": individual_amount,
            "finance_incident_amount": 0,
            "finance_incident_contribution": 0,
            "individual_incident_amount": 0,
        }

    for venue_pricing_info in collective_query:
        venue_id = venue_pricing_info.venue_id
        venue_common_name = venue_pricing_info.common_name
        reimbursed_amount = venue_pricing_info.reimbursed_amount
        booking_amount = -utils.to_cents(venue_pricing_info.booking_amount)
        if venue_id in reimbursements_by_venue:
            reimbursements_by_venue[venue_id]["reimbursed_amount"] += reimbursed_amount
            reimbursements_by_venue[venue_id]["validated_booking_amount"] += booking_amount
        else:
            reimbursements_by_venue[venue_id] = {
                "venue_name": venue_common_name,
                "reimbursed_amount": reimbursed_amount,
                "validated_booking_amount": booking_amount,
                "individual_amount": 0,
                "finance_incident_amount": 0,
                "finance_incident_contribution": 0,
                "individual_incident_amount": 0,
            }

    for (venue_id, venue_common_name), bookings in itertools.groupby(
        incident_query, lambda x: (x.venue_id, x.common_name)
    ):
        total_pricing_amount = 0
        incident_amount = 0
        for booking in bookings:
            incident_amount += (
                booking.booking_unit_amount * booking.booking_quantity * 100
            ) - booking.incident_new_total_amount
            total_pricing_amount += booking.pricing_amount

        if venue_id not in reimbursements_by_venue:
            reimbursements_by_venue[venue_id] = venue_info_base
            reimbursements_by_venue[venue_id]["venue_name"] = venue_common_name
        reimbursements_by_venue[venue_id]["finance_incident_amount"] += total_pricing_amount
        reimbursements_by_venue[venue_id]["finance_incident_contribution"] += incident_amount - total_pricing_amount
        reimbursements_by_venue[venue_id]["individual_incident_amount"] += total_pricing_amount

    for (venue_id, venue_common_name), bookings in itertools.groupby(
        collective_incident_query, lambda x: (x.venue_id, x.common_name)
    ):
        total_pricing_amount = 0
        incident_amount = 0
        for booking in bookings:
            incident_amount += (booking.booking_amount * 100) - booking.incident_new_total_amount
            total_pricing_amount += booking.pricing_amount

        if venue_id not in reimbursements_by_venue:
            reimbursements_by_venue[venue_id] = venue_info_base
            reimbursements_by_venue[venue_id]["venue_name"] = venue_common_name
        reimbursements_by_venue[venue_id]["finance_incident_amount"] += total_pricing_amount
        reimbursements_by_venue[venue_id]["finance_incident_contribution"] += incident_amount - total_pricing_amount

    return reimbursements_by_venue.values()


def _generate_invoice_html(invoice: models.Invoice, batch: models.CashflowBatch) -> str:
    context = _prepare_invoice_context(invoice, batch)
    return render_template("invoices/invoice.html", **context)


def _generate_debit_note_html(invoice: models.Invoice, batch: models.CashflowBatch) -> str:
    context = _prepare_invoice_context(invoice, batch)
    return render_template("invoices/debit_note.html", **context)


def _store_invoice_pdf(invoice_storage_id: str, invoice_html: str) -> None:
    with log_elapsed(logger, "Generated PDF invoice"):
        invoice_pdf = pdf_utils.generate_pdf_from_html(html_content=invoice_html)
    with log_elapsed(logger, "Stored PDF invoice in object storage"):
        store_public_object(
            folder="invoices", object_id=invoice_storage_id, blob=invoice_pdf, content_type="application/pdf"
        )


def merge_cashflow_batches(
    batches_to_remove: list[models.CashflowBatch],
    target_batch: models.CashflowBatch,
) -> None:
    """Merge multiple cashflow batches into a single (existing) one.

    This function is to be used in a script if multiple batches have
    been wrongly generated (for example because the cutoff of the
    first batch was wrong). The target batch must hence be the one
    with the right cutoff.
    """
    assert len(batches_to_remove) >= 1
    assert target_batch not in batches_to_remove

    batch_ids_to_remove = [batch.id for batch in batches_to_remove]
    bank_account_ids = [
        id_
        for (id_,) in db.session.query(models.Cashflow)
        .filter(models.Cashflow.batchId.in_(batch_ids_to_remove))
        .with_entities(models.Cashflow.bankAccountId)
        .distinct()
    ]

    with transaction():
        initial_sum = (
            db.session.query(models.Cashflow)
            .filter(
                models.Cashflow.batchId.in_([b.id for b in batches_to_remove + [target_batch]]),
            )
            .with_entities(sa_func.sum(models.Cashflow.amount))
            .scalar()
        )
        for bank_account_id in bank_account_ids:
            cashflows = (
                db.session.query(models.Cashflow)
                .filter(
                    models.Cashflow.bankAccountId == bank_account_id,
                    models.Cashflow.batchId.in_(
                        batch_ids_to_remove + [target_batch.id],
                    ),
                )
                .all()
            )
            # One cashflow, wrong batch. Just change the batchId.
            if len(cashflows) == 1:
                db.session.query(models.Cashflow).filter_by(id=cashflows[0].id).update(
                    {
                        "batchId": target_batch.id,
                        "creationDate": target_batch.creationDate,
                    },
                    synchronize_session=False,
                )
                continue

            # Multiple cashflows, possibly including the target batch.
            # Update "right" cashflow amount if there is one (or any
            # cashflow otherwise), delete other cashflows.
            try:
                cashflow_to_keep = [cf for cf in cashflows if cf.batchId == target_batch.id][0]
            except IndexError:
                cashflow_to_keep = cashflows[0]
            cashflow_ids_to_remove = [cf.id for cf in cashflows if cf != cashflow_to_keep]
            sum_to_add = (
                db.session.query(models.Cashflow)
                .filter(models.Cashflow.id.in_(cashflow_ids_to_remove))
                .with_entities(sa_func.sum(models.Cashflow.amount))
                .scalar()
            )
            db.session.query(models.CashflowPricing).filter(
                models.CashflowPricing.cashflowId.in_(cashflow_ids_to_remove)
            ).update(
                {"cashflowId": cashflow_to_keep.id},
                synchronize_session=False,
            )
            db.session.query(models.Cashflow).filter_by(id=cashflow_to_keep.id).update(
                {
                    "batchId": target_batch.id,
                    "amount": cashflow_to_keep.amount + sum_to_add,
                },
                synchronize_session=False,
            )
            db.session.query(models.CashflowLog).filter(
                models.CashflowLog.cashflowId.in_(cashflow_ids_to_remove),
            ).delete(synchronize_session=False)
            db.session.query(models.Cashflow).filter(
                models.Cashflow.id.in_(cashflow_ids_to_remove),
            ).delete(synchronize_session=False)
        db.session.query(models.CashflowBatch).filter(models.CashflowBatch.id.in_(batch_ids_to_remove)).delete(
            synchronize_session=False,
        )
        final_sum = (
            db.session.query(models.Cashflow)
            .filter(
                models.Cashflow.batchId.in_(batch_ids_to_remove + [target_batch.id]),
            )
            .with_entities(sa_func.sum(models.Cashflow.amount))
            .scalar()
        )
        assert final_sum == initial_sum
        db.session.commit()


def create_offerer_reimbursement_rule(
    offerer_id: int,
    subcategories: list[int],
    rate: decimal.Decimal,
    start_date: datetime.datetime,
    end_date: datetime.datetime | None = None,
) -> models.CustomReimbursementRule:
    return _create_reimbursement_rule(
        offerer_id=offerer_id,
        subcategories=subcategories,
        rate=rate,
        start_date=start_date,
        end_date=end_date,
    )


def create_venue_reimbursement_rule(
    venue_id: int,
    subcategories: list[int],
    rate: decimal.Decimal,
    start_date: datetime.datetime,
    end_date: datetime.datetime | None = None,
) -> models.CustomReimbursementRule:
    return _create_reimbursement_rule(
        venue_id=venue_id,
        subcategories=subcategories,
        rate=rate,
        start_date=start_date,
        end_date=end_date,
    )


def create_offer_reimbursement_rule(
    offer_id: int,
    amount: decimal.Decimal,
    start_date: datetime.datetime,
    end_date: datetime.datetime | None = None,
) -> models.CustomReimbursementRule:
    return _create_reimbursement_rule(
        offer_id=offer_id,
        amount=amount,
        start_date=start_date,
        end_date=end_date,
    )


def _create_reimbursement_rule(
    *,
    offerer_id: int | None = None,
    venue_id: int | None = None,
    offer_id: int | None = None,
    subcategories: list[int] | None = None,
    rate: decimal.Decimal | None = None,
    amount: decimal.Decimal | None = None,
    start_date: datetime.datetime | None = None,
    end_date: datetime.datetime | None = None,
) -> models.CustomReimbursementRule:
    subcategories = subcategories or []
    if not (bool(offerer_id) ^ bool(venue_id) ^ bool(offer_id)):
        raise ValueError("Must provide offer, venue, or offerer (only one)")
    if not (bool(rate) ^ bool(amount)):
        raise ValueError("Must provide rate or amount (but not both)")
    if not bool(rate) and (bool(offerer_id) or bool(venue_id)):
        raise ValueError("Rate must be specified only with an offerer or venue (not with an offer)")
    if not (bool(amount) or not bool(offer_id)):
        raise ValueError("Amount must be specified only with an offer (not with an offerer or venue)")
    if not start_date:
        raise ValueError("Start date must be provided")
    rule = models.CustomReimbursementRule(
        offererId=offerer_id,
        venueId=venue_id,
        offerId=offer_id,
        subcategories=subcategories,
        rate=rate,  # only for offerers and venues
        amount=utils.to_cents(amount) if amount is not None else None,  # only for offers
        timespan=(start_date, end_date),
    )
    validation.validate_reimbursement_rule(rule)
    db.session.add(rule)
    db.session.commit()
    return rule


def edit_reimbursement_rule(
    rule: models.CustomReimbursementRule,
    end_date: datetime.datetime,
) -> models.CustomReimbursementRule:
    if end_date.date() <= datetime.datetime.utcnow().date():
        error = "La date de fin doit être postérieure à la date du jour."
        raise exceptions.WrongDateForReimbursementRule(error)
    # To avoid complexity, we do not allow to edit the end date of a
    # rule that already has one.
    if rule.timespan.upper:
        error = "Il n'est pas possible de modifier la date de fin lorsque celle-ci est déjà définie."
        raise exceptions.WrongDateForReimbursementRule(error)
    # `rule.timespan.lower` is a naive datetime but it comes from the
    # database, and is thus UTC. We hence need to localize it so that
    # `make_timerange()` does not convert it again. This is not needed
    # on production (where the server timezone is UTC), but it's
    # necessary for local development and tests that may be run
    # under a different timezone.
    rule.timespan = db_utils.make_timerange(pytz.utc.localize(rule.timespan.lower), end_date)
    try:
        validation.validate_reimbursement_rule(rule, check_start_date=False)
    except exceptions.ReimbursementRuleValidationError:
        # Make sure that the change to `timespan` is not accidentally
        # flushed to the database.
        db.session.expire(rule)
        raise
    db.session.add(rule)
    db.session.flush()
    return rule


def update_bank_account_venues_links(
    user: users_models.User,
    bank_account: models.BankAccount,
    venues_ids: set[int],
) -> None:
    offerer = bank_account.offerer
    venues = offerer.managedVenues

    venues_linked_to_other_bank_account = {
        venue.id
        for venue in venues
        if venue.id in venues_ids
        and venue.current_bank_account_link
        and venue.current_bank_account_link.bankAccountId != bank_account.id
    }
    if venues_linked_to_other_bank_account:
        raise exceptions.VenueAlreadyLinkedToAnotherBankAccount(
            f"At least one venue {(*venues_linked_to_other_bank_account,)} is already linked to another bank account"
        )

    managed_venues_ids = {venue.id for venue in venues if venue.current_pricing_point_link}
    current_links_by_venue_id = {
        venue.id: venue.current_bank_account_link
        for venue in venues
        if venue.current_bank_account_link and venue.current_bank_account_link.bankAccountId == bank_account.id
    }

    venues_already_linked = set(current_links_by_venue_id.keys())
    venues_links_to_create = venues_ids.difference(venues_already_linked)
    venues_links_to_deprecate = venues_already_linked.difference(venues_ids)

    new_links = []

    with transaction():
        link_bulk_update_mapping = []
        action_history_bulk_insert_mapping = []

        for venue_id in venues_links_to_deprecate:
            link = current_links_by_venue_id[venue_id]

            link_bulk_update_mapping.append(
                {
                    "id": link.id,
                    "timespan": db_utils.make_timerange(link.timespan.lower, datetime.datetime.utcnow()),
                }
            )
            action_history_bulk_insert_mapping.append(
                {
                    "actionType": history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
                    "authorUserId": user.real_user.id,
                    "venueId": link.venueId,
                    "bankAccountId": bank_account.id,
                }
            )
        db.session.bulk_update_mappings(
            offerers_models.VenueBankAccountLink,
            link_bulk_update_mapping,
        )

        for venue_id in venues_links_to_create:
            if venue_id not in managed_venues_ids:
                logger.warning(
                    "Attempt of a user to link a venue that does not meet criteria (venue without pricing point or belonging to another offerer)",
                    extra={
                        "venue_id": venue_id,
                        "bank_account_id": bank_account.id,
                        "offerer_id": offerer.id,
                        "user_id": user.id,
                    },
                )
                continue

            new_links.append(
                {
                    "venueId": venue_id,
                    "bankAccountId": bank_account.id,
                    "timespan": db_utils.make_timerange(datetime.datetime.utcnow()),
                }
            )
            action_history_bulk_insert_mapping.append(
                {
                    "actionType": history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
                    "authorUserId": user.real_user.id,
                    "venueId": venue_id,
                    "bankAccountId": bank_account.id,
                }
            )

        db.session.bulk_insert_mappings(offerers_models.VenueBankAccountLink, new_links)

        db.session.bulk_insert_mappings(
            history_models.ActionHistory,
            action_history_bulk_insert_mapping,
        )

        for venue in venues:
            if venue.id in venues_links_to_deprecate and venue.bookingEmail:
                transactional_mails.send_venue_bank_account_link_deprecated(
                    venue.common_name, bank_account.label, venue.bookingEmail
                )


def create_overpayment_finance_incident(
    *,
    bookings: list[bookings_models.Booking],
    author: users_models.User,
    origin: models.FinanceIncidentRequestOrigin,
    zendesk_id: int | None = None,
    comment: str | None = None,
    amount: decimal.Decimal | None = None,
) -> models.FinanceIncident:
    incident = models.FinanceIncident(
        kind=models.IncidentType.OVERPAYMENT,
        status=models.IncidentStatus.CREATED,
        venueId=bookings[0].venueId,
        details={
            "authorId": author.id,
            "createdAt": datetime.datetime.utcnow().isoformat(),
        },
        zendeskId=zendesk_id,
        origin=origin,
        comment=comment,
    )
    db.session.add(incident)
    db.session.flush()

    booking_finance_incidents_to_create = []
    if len(bookings) == 1:
        booking = bookings[0]
        new_total_amount = decimal.Decimal(0) if amount is None else booking.total_amount - decimal.Decimal(amount)
        booking_finance_incidents_to_create.append(
            models.BookingFinanceIncident(
                bookingId=booking.id,
                incidentId=incident.id,
                beneficiaryId=booking.userId,
                newTotalAmount=utils.to_cents(new_total_amount),
            )
        )
    else:
        for booking in bookings:
            booking_finance_incidents_to_create.append(
                models.BookingFinanceIncident(
                    bookingId=booking.id,
                    incidentId=incident.id,
                    beneficiaryId=booking.userId,
                    # Only total overpayment if multiple bookings are selected
                    newTotalAmount=0,
                )
            )
    db.session.add_all(booking_finance_incidents_to_create)

    history_api.add_action(
        history_models.ActionType.FINANCE_INCIDENT_CREATED,
        author=author,
        finance_incident=incident,
        comment=comment,
    )

    db.session.flush()

    return incident


def create_overpayment_finance_incident_collective_booking(
    booking: educational_models.CollectiveBooking,
    author: users_models.User,
    origin: models.FinanceIncidentRequestOrigin,
    zendesk_id: int | None = None,
    comment: str | None = None,
) -> models.FinanceIncident:
    incident = models.FinanceIncident(
        kind=models.IncidentType.OVERPAYMENT,
        status=models.IncidentStatus.CREATED,
        venueId=booking.venueId,
        details={
            "authorId": author.id,
            "createdAt": datetime.datetime.utcnow().isoformat(),
        },
        zendeskId=zendesk_id,
        origin=origin,
        comment=comment,
    )
    db.session.add(incident)
    db.session.flush()

    booking_finance_incident = models.BookingFinanceIncident(
        collectiveBookingId=booking.id,
        incidentId=incident.id,
        newTotalAmount=0,
    )
    db.session.add(booking_finance_incident)

    history_api.add_action(
        history_models.ActionType.FINANCE_INCIDENT_CREATED,
        author=author,
        finance_incident=incident,
        comment=comment,
    )

    db.session.flush()

    return incident


def create_finance_commercial_gesture(
    *,
    bookings: list[bookings_models.Booking],
    amount: decimal.Decimal,
    author: users_models.User,
    origin: models.FinanceIncidentRequestOrigin,
    zendesk_id: int | None = None,
    comment: str | None = None,
) -> models.FinanceIncident:
    incident = models.FinanceIncident(
        kind=models.IncidentType.COMMERCIAL_GESTURE,
        status=models.IncidentStatus.CREATED,
        venueId=bookings[0].venueId,
        details={
            "authorId": author.id,
            "createdAt": datetime.datetime.utcnow().isoformat(),
        },
        zendeskId=zendesk_id,
        origin=origin,
        comment=comment,
    )
    db.session.add(incident)
    db.session.flush()

    booking_finance_incidents_to_create = []
    total_bookings_quantity = sum(booking.quantity for booking in bookings)
    total_amount = sum(utils.to_cents(booking.total_amount) for booking in bookings)
    amount_cents = utils.to_cents(amount)
    # First calculate the partial commercial gesture's amount for each booking in the list except the last one:
    # → (∑<bookings amounts> - <input commercial gesture amount>) * <booking quantity> ÷ ∑<bookings quantity>
    # Then calculate the last booking's commercial gesture amount based on the (n - 1) first amounts to avoid rounding issues:
    # → <total commercial gesture amount> - <sum of partial commercial gesture amounts previously calculated>
    # The sum of created partial commercial gestures should be equal to: ∑<bookings amounts> - <input commercial gesture amount>
    for booking in bookings[:-1]:
        # all bookings in a commercial gesture must be from the same stock → they all have the same amount
        new_total_amount = (total_amount - amount_cents) * booking.quantity // total_bookings_quantity
        booking_finance_incidents_to_create.append(
            models.BookingFinanceIncident(
                bookingId=booking.id,
                incidentId=incident.id,
                beneficiaryId=booking.userId,
                newTotalAmount=new_total_amount,
            )
        )
    # Calculate the commercial gesture's amount for the last remaining booking (cf. the comments above ↑)
    for booking in bookings[-1:]:
        # all bookings in a commercial gesture must be from the same stock → they all have the same amount
        new_total_amount = (total_amount - amount_cents) - sum(
            b.newTotalAmount for b in booking_finance_incidents_to_create
        )
        booking_finance_incidents_to_create.append(
            models.BookingFinanceIncident(
                bookingId=booking.id,
                incidentId=incident.id,
                beneficiaryId=booking.userId,
                newTotalAmount=new_total_amount,
            )
        )

    db.session.add_all(booking_finance_incidents_to_create)
    history_api.add_action(
        history_models.ActionType.FINANCE_INCIDENT_CREATED,
        author=author,
        finance_incident=incident,
        comment=comment,
    )
    db.session.flush()
    return incident


def create_finance_commercial_gesture_collective_booking(
    booking: educational_models.CollectiveBooking,
    author: users_models.User,
    origin: models.FinanceIncidentRequestOrigin,
    zendesk_id: int | None = None,
    comment: str | None = None,
) -> models.FinanceIncident:
    incident = models.FinanceIncident(
        kind=models.IncidentType.COMMERCIAL_GESTURE,
        status=models.IncidentStatus.CREATED,
        venueId=booking.venueId,
        details={
            "authorId": author.id,
            "createdAt": datetime.datetime.utcnow().isoformat(),
        },
        zendeskId=zendesk_id,
        origin=origin,
        comment=comment,
    )
    db.session.add(incident)
    db.session.flush()
    booking_finance_incident = models.BookingFinanceIncident(
        collectiveBookingId=booking.id,
        incidentId=incident.id,
        newTotalAmount=0,
    )
    db.session.add(booking_finance_incident)
    history_api.add_action(
        history_models.ActionType.FINANCE_INCIDENT_CREATED,
        author=author,
        finance_incident=incident,
        comment=comment,
    )
    db.session.flush()
    return incident


def _create_finance_events_from_incident(
    booking_finance_incident: models.BookingFinanceIncident,
    incident_validation_date: datetime.datetime | None = None,
) -> list[models.FinanceEvent]:
    finance_events = []
    assert booking_finance_incident.incident
    # In the case of commercial gesture, only one finance event will be created with the new price (incident amount)
    if booking_finance_incident.incident.kind == models.IncidentType.COMMERCIAL_GESTURE:
        finance_events.append(
            add_event(
                models.FinanceEventMotive.INCIDENT_COMMERCIAL_GESTURE,
                booking_incident=booking_finance_incident,
                incident_validation_date=incident_validation_date,
            )
        )
    elif booking_finance_incident.incident.kind in (
        models.IncidentType.OVERPAYMENT,
        models.IncidentType.OFFER_PRICE_REGULATION,
        models.IncidentType.FRAUD,
    ):
        # Retrieve initial amount of the booking
        finance_events.append(
            add_event(
                models.FinanceEventMotive.INCIDENT_REVERSAL_OF_ORIGINAL_EVENT,
                booking_incident=booking_finance_incident,
                incident_validation_date=incident_validation_date,
            )
        )

        if booking_finance_incident.is_partial:
            # Declare new amount (equivalent to booking incident new total amount)
            finance_events.append(
                add_event(
                    models.FinanceEventMotive.INCIDENT_NEW_PRICE,
                    booking_incident=booking_finance_incident,
                    incident_validation_date=incident_validation_date,
                )
            )
    db.session.add_all(finance_events)
    db.session.flush()

    return finance_events


def validate_finance_overpayment_incident(
    finance_incident: models.FinanceIncident,
    force_debit_note: bool,
    author: users_models.User,
) -> None:
    from pcapi.core.bookings import api as bookings_api

    incident_validation_date = datetime.datetime.utcnow()
    finance_events = []
    for booking_incident in finance_incident.booking_finance_incidents:
        finance_events.extend(
            _create_finance_events_from_incident(booking_incident, incident_validation_date=incident_validation_date)
        )
        if not booking_incident.is_partial:
            if booking := booking_incident.booking:
                bookings_api.cancel_booking_for_finance_incident(booking)
                db.session.add(booking)
            elif collective_booking := booking_incident.collectiveBooking:
                collective_booking.cancel_booking(
                    educational_models.CollectiveBookingCancellationReasons.FINANCE_INCIDENT,
                    cancel_even_if_reimbursed=True,
                )
                db.session.add(collective_booking)
        recredit = deposit_api.recredit_new_deposit_after_validation_of_incident_on_expired_deposit(booking_incident)
    db.session.add_all(finance_events)

    if not finance_incident.relates_to_collective_bookings:
        beneficiaries = set(
            booking_incident.beneficiary for booking_incident in finance_incident.booking_finance_incidents
        )
        for beneficiary in beneficiaries:
            history_api.add_action(
                history_models.ActionType.FINANCE_INCIDENT_USER_RECREDIT,
                author=author,
                user=beneficiary,
                linked_incident_id=finance_incident.id,
                comment=(
                    "Suite à la validation d'un incident finance déclaré sur le crédit '15-17 ans' (expiré du fait de la réforme des crédits), le recrédit se fera automatiquement sur celui '17-18 ans'"
                    if recredit
                    else None
                ),
            )

    finance_incident.status = models.IncidentStatus.VALIDATED
    finance_incident.forceDebitNote = force_debit_note
    db.session.add(finance_incident)

    history_api.add_action(
        history_models.ActionType.FINANCE_INCIDENT_VALIDATED,
        author=author,
        venue=finance_incident.venue,
        finance_incident=finance_incident,
        comment=(
            "Génération d'une note de débit à la prochaine échéance."
            if force_debit_note
            else "Récupération sur les prochaines réservations."
        ),
        linked_incident_id=finance_incident.id,
    )

    db.session.flush()

    # send mail to pro
    send_finance_incident_emails(finance_incident=finance_incident)
    # send mail to beneficiaries or educational redactor
    for booking_incident in finance_incident.booking_finance_incidents:
        if not booking_incident.is_partial:
            if booking_incident.collectiveBooking:
                educational_api_booking.notify_reimburse_collective_booking(
                    collective_booking=booking_incident.collectiveBooking,
                    reason="NO_EVENT",
                )
            else:
                send_booking_cancellation_by_pro_to_beneficiary_email(
                    booking=booking_incident.booking,
                )


def validate_finance_commercial_gesture(
    finance_incident: models.FinanceIncident,
    author: users_models.User,
) -> None:
    incident_validation_date = datetime.datetime.utcnow()
    finance_events = []
    for booking_incident in finance_incident.booking_finance_incidents:
        finance_events += _create_finance_events_from_incident(
            booking_finance_incident=booking_incident,
            incident_validation_date=incident_validation_date,
        )

    db.session.add_all(finance_events)

    if not finance_incident.relates_to_collective_bookings:
        beneficiaries = {
            booking_incident.beneficiary for booking_incident in finance_incident.booking_finance_incidents
        }
        for beneficiary in beneficiaries:
            history_api.add_action(
                history_models.ActionType.FINANCE_INCIDENT_USER_RECREDIT,
                author=author,
                user=beneficiary,
                linked_incident_id=finance_incident.id,
            )

    finance_incident.status = models.IncidentStatus.VALIDATED
    finance_incident.forceDebitNote = False
    db.session.add(finance_incident)

    history_api.add_action(
        history_models.ActionType.FINANCE_INCIDENT_VALIDATED,
        author=author,
        venue=finance_incident.venue,
        finance_incident=finance_incident,
        comment="Récupération sur les prochaines réservations.",
        linked_incident_id=finance_incident.id,
    )

    db.session.flush()

    # send mail to pro
    send_commercial_gesture_email(finance_incident=finance_incident)


def cancel_finance_incident(
    incident: models.FinanceIncident,
    comment: str,
    author: users_models.User,
) -> None:
    if incident.status == models.IncidentStatus.CANCELLED:
        raise exceptions.FinanceIncidentAlreadyCancelled
    if incident.status == models.IncidentStatus.VALIDATED:
        raise exceptions.FinanceIncidentAlreadyValidated

    incident.status = models.IncidentStatus.CANCELLED
    db.session.add(incident)

    history_api.add_action(
        history_models.ActionType.FINANCE_INCIDENT_CANCELLED,
        author=author,
        finance_incident=incident,
        comment=comment,
    )

    db.session.flush()


def are_cashflows_being_generated() -> bool:
    return bool(app.redis_client.exists(conf.REDIS_GENERATE_CASHFLOW_LOCK))


def deprecate_venue_bank_account_links(bank_account: models.BankAccount) -> None:
    """
    Deprecate all up-to-date link between a bankAccount and a Venue.
    Log that action as well by creating an ActionHistory.
    """
    for link in bank_account.venueLinks:
        if link.timespan.upper is None:
            link.timespan = db_utils.make_timerange(link.timespan.lower, datetime.datetime.utcnow())
            action_history = history_models.ActionHistory(
                venueId=link.venueId,
                bankAccountId=bank_account.id,
                actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
            )
            db.session.add_all([link, action_history])

    db.session.flush()


def mark_bank_account_without_continuation(ds_application_id: int) -> None:
    now = datetime.datetime.utcnow()

    bank_account = (
        db.session.query(models.BankAccount)
        .filter_by(dsApplicationId=ds_application_id)
        .outerjoin(
            offerers_models.VenueBankAccountLink,
            sa.and_(
                models.BankAccount.id == offerers_models.VenueBankAccountLink.bankAccountId,
                offerers_models.VenueBankAccountLink.timespan.contains(now),
            ),
        )
        .outerjoin(
            models.BankAccountStatusHistory,
            sa.and_(
                models.BankAccount.id == models.BankAccountStatusHistory.bankAccountId,
                models.BankAccountStatusHistory.timespan.contains(now),
            ),
        )
        .options(sa_orm.contains_eager(models.BankAccount.venueLinks))
        .options(sa_orm.contains_eager(models.BankAccount.statusHistory))
        .one_or_none()
    )
    if not bank_account:
        return

    bank_account.status = models.BankAccountApplicationStatus.WITHOUT_CONTINUATION
    bank_account.dateLastStatusUpdate = now
    if bank_account.statusHistory:
        current_status_history = bank_account.statusHistory[0]
        current_status_history.timespan = db_utils.make_timerange(current_status_history.timespan.lower, now)
        db.session.add(current_status_history)
    new_status_history = models.BankAccountStatusHistory(
        bankAccount=bank_account, status=models.BankAccountApplicationStatus.WITHOUT_CONTINUATION, timespan=(now,)
    )
    db.session.add_all([bank_account, new_status_history])
    db.session.flush()

    # This shouldn't happen but we need to be sure that if any venue is linked to a bank account
    # that is going to be marked as without continuation, it's unlinked.
    # We don't want any cashflows to be generated using non valid bank accounts (non valid as not validated by the compliance).
    # Hence this bank account can no longer be linked to any venue, if any.
    deprecate_venue_bank_account_links(bank_account)
