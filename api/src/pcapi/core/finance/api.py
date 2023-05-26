"""Finance-related functions.

Dependent pricings
==================

The reimbursement rule to be applied for each booking depends on the
yearly revenue to date. For this to be reproducible, we must price
bookings in a specific, stable order: more or less (*), the order in
which bookings are used.

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
  which should be very rare.

(*) Actually, it's a bit more complicated. Bookings are ordered on a
few more criteria, see `price_bookings()` and
`_delete_dependent_pricings()`.
"""

from collections import defaultdict
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

from dateutil.relativedelta import relativedelta
from flask import render_template
from flask_sqlalchemy import BaseQuery
import pytz
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm
import sqlalchemy.sql.functions as sqla_func

from pcapi import settings
from pcapi.connectors import googledrive
import pcapi.core.bookings.models as bookings_models
import pcapi.core.educational.models as educational_models
import pcapi.core.external.attributes.api as external_attributes_api
from pcapi.core.logging import log_elapsed
import pcapi.core.mails.transactional as transactional_mails
from pcapi.core.object_storage import store_public_object
from pcapi.core.offerers import repository as offerers_repository
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.reference.models as reference_models
import pcapi.core.users.constants as users_constants
import pcapi.core.users.models as users_models
from pcapi.domain import reimbursement
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.utils import human_ids
import pcapi.utils.date as date_utils
import pcapi.utils.db as db_utils
import pcapi.utils.pdf as pdf_utils

from . import conf
from . import exceptions
from . import models
from . import repository
from . import utils
from . import validation


logger = logging.getLogger(__name__)

RECREDIT_UNDERAGE_USERS_BATCH_SIZE = 1000

# When used through the cron, only price bookings that were used in 2022.
# Prior bookings have been priced manually.
MIN_DATE_TO_PRICE = datetime.datetime(2021, 12, 31, 23, 0)  # UTC

# The ORDER BY clause to be used to price bookings in a specific,
# stable order. If you change this, you MUST update
# `_booking_comparison_tuple()` below.
_PRICE_BOOKINGS_ORDER_CLAUSE = (
    sqla.func.greatest(
        sqla.func.lower(offerers_models.VenuePricingPointLink.timespan),
        sqla.func.greatest(
            offers_models.Stock.beginningDatetime,
            bookings_models.Booking.dateUsed,
        ),
    ),
    sqla.func.greatest(
        offers_models.Stock.beginningDatetime,
        bookings_models.Booking.dateUsed,
    ),
    # If an event (or multiple events) have the same date _after_ the
    # used date, fallback on the used date.
    bookings_models.Booking.dateUsed,
    # Some bookings are marked as used in a batch, hence with the same
    # datetime value. In that case, we order by their id.
    bookings_models.Booking.id,
)


PRICE_BOOKINGS_BATCH_SIZE = 100
CASHFLOW_BATCH_LABEL_PREFIX = "VIR"


def price_bookings(
    min_date: datetime.datetime = MIN_DATE_TO_PRICE,
    batch_size: int = PRICE_BOOKINGS_BATCH_SIZE,
) -> None:
    """Price bookings that have been recently marked as used.

    This function is normally called by a cron job.
    """
    # The upper bound on `dateUsed` avoids selecting a very recent
    # booking that may have been COMMITed to the database just before
    # another booking with a slightly older `dateUsed` (see note in
    # module docstring).
    threshold = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
    window = (min_date, threshold)

    errored_pricing_point_ids = set()

    # This is a quick hack to avoid fetching all bookings at once,
    # resulting in a very large session that is updated on each
    # commit, which takes a lot of time (up to 1 or 2 seconds per
    # commit).
    booking_query = _get_bookings_to_price(bookings_models.Booking, window)
    collective_booking_query = _get_bookings_to_price(educational_models.CollectiveBooking, window)
    loops = math.ceil(max(booking_query.count(), collective_booking_query.count()) / batch_size)

    def _get_loop_query(
        query: BaseQuery,
        last_booking: bookings_models.Booking | educational_models.CollectiveBooking | None,
    ) -> BaseQuery:
        # We cannot use OFFSET and LIMIT because the loop "consumes"
        # bookings that have been priced (so the query will not return
        # them in the next loop), but keeps bookings that cannot be
        # priced (so the query WILL return them in the next loop).
        if last_booking:
            if isinstance(last_booking, bookings_models.Booking):
                clause = sqla.func.ROW(*_PRICE_BOOKINGS_ORDER_CLAUSE) > sqla.func.ROW(
                    *_booking_comparison_tuple(last_booking)
                )
            else:
                clause = sqla.func.ROW(
                    educational_models.CollectiveBooking.dateUsed, educational_models.CollectiveBooking.id
                ) > sqla.func.ROW(last_booking.dateUsed, last_booking.id)
            query = query.filter(clause)
        return query.limit(batch_size)

    last_booking = None
    last_collective_booking = None
    while loops > 0:
        with log_elapsed(logger, "Fetched batch of bookings to price"):
            bookings = list(
                itertools.chain.from_iterable(
                    (
                        _get_loop_query(booking_query, last_booking),
                        _get_loop_query(collective_booking_query, last_collective_booking),
                    )
                )
            )
        for booking in bookings:
            if isinstance(booking, bookings_models.Booking):
                last_booking = booking
            else:
                last_collective_booking = booking
            try:
                pricing_point_id = _get_pricing_point_link(booking).pricingPointId
                if pricing_point_id in errored_pricing_point_ids:
                    continue
                extra = {
                    "booking": booking.id,
                    "pricing_point": pricing_point_id,
                }
                with log_elapsed(logger, "Priced booking", extra):
                    price_booking(booking)
            except Exception as exc:  # pylint: disable=broad-except
                errored_pricing_point_ids.add(pricing_point_id)
                logger.info(
                    "Ignoring further bookings from pricing point",
                    extra={"pricing_point": pricing_point_id},
                )
                logger.exception(
                    "Could not price booking",
                    extra={
                        "booking": booking.id,
                        "pricing_point": pricing_point_id,
                        "exc": str(exc),
                    },
                )
        loops -= 1
        # Keep last booking in the session, we'll need it when calling
        # `_get_loop_query()` for the next loop.
        with log_elapsed(logger, "Expunged priced bookings from session"):
            for booking in bookings:
                if booking not in (last_booking, last_collective_booking):
                    db.session.expunge(booking)


def _get_pricing_point_link(
    booking: bookings_models.Booking | educational_models.CollectiveBooking,
) -> offerers_models.VenuePricingPointLink:
    """Return the venue-pricing point link to use at the requested
    datetime.
    """
    timestamp = booking.dateUsed
    links = booking.venue.pricing_point_links
    # Look for a link that was active at the requested date.
    for link in links:
        if timestamp < link.timespan.lower:
            continue
        if not link.timespan.upper or timestamp < link.timespan.upper:
            return link
    # If a (single) link was added after and it's still active, we can
    # use it.
    if len(links) == 1 and links[0].timespan.upper is None:
        return links[0]
    # Otherwise, we just cannot know what to do. Raise an error so
    # that we can investigate such cases.
    raise ValueError(f"Could not find pricing point for booking {booking.id}")


def _get_bookings_to_price(
    model: typing.Type[bookings_models.Booking] | typing.Type[educational_models.CollectiveBooking],
    window: tuple[datetime.datetime, datetime.datetime],
) -> BaseQuery:
    bookings_with_right_pricing_point = model.query
    if model == bookings_models.Booking:
        bookings_with_right_pricing_point = bookings_with_right_pricing_point.filter(
            model.status == bookings_models.BookingStatus.USED,
        ).outerjoin(models.Pricing, models.Pricing.bookingId == model.id)
    else:
        bookings_with_right_pricing_point = bookings_with_right_pricing_point.filter(
            model.status == educational_models.CollectiveBookingStatus.USED
        ).outerjoin(models.Pricing, models.Pricing.collectiveBookingId == model.id)

    # Select the "right" pricing point link to use for each booking.
    # This is done in a CTE because we must first find those links,
    # and only then apply a filter to look for bookings.
    bookings_with_right_pricing_point = (
        bookings_with_right_pricing_point.filter(
            model.dateUsed.between(*window),  # type: ignore [union-attr]
            models.Pricing.id.is_(None) | (models.Pricing.status == models.PricingStatus.CANCELLED),
        )
        .distinct(model.id, offerers_models.VenuePricingPointLink.venueId)
        .join(model.venue)
        .join(offerers_models.Venue.pricing_point_links)
        .filter(
            offerers_models.VenuePricingPointLink.timespan.contains(model.dateUsed)
            # See comment in `_delete_dependent_pricings()` about the corner cases
            # that we ignore here.
            | (model.dateUsed < sqla.func.lower(offerers_models.VenuePricingPointLink.timespan))
        )
        .order_by(
            model.id,
            offerers_models.VenuePricingPointLink.venueId,
            sqla.func.lower(offerers_models.VenuePricingPointLink.timespan),
        )
        .with_entities(
            model.id.label("booking_id"),  # type: ignore [attr-defined]
            offerers_models.VenuePricingPointLink.id.label("pricing_point_link_id"),
        )
        .cte("bookings_with_right_pricing_point")
    )

    query = (
        db.session.query(model)
        .join(bookings_with_right_pricing_point, bookings_with_right_pricing_point.c.booking_id == model.id)
        .join(
            offerers_models.VenuePricingPointLink,
            offerers_models.VenuePricingPointLink.id == bookings_with_right_pricing_point.c.pricing_point_link_id,
        )
    )

    if model == bookings_models.Booking:
        query = query.join(bookings_models.Booking.stock).order_by(*_PRICE_BOOKINGS_ORDER_CLAUSE)
    else:
        query = query.order_by(
            educational_models.CollectiveBooking.dateUsed,
            educational_models.CollectiveBooking.id,
        )

    query = query.options(
        sqla_orm.load_only(model.id),
        sqla_orm.load_only(model.dateUsed),
        # Our code does not access `Venue.id` but SQLAlchemy needs
        # it to build a `Venue` object (which we access through
        # `booking.venue`).
        sqla_orm.contains_eager(model.venue).load_only(
            offerers_models.Venue.id,
        ),
        sqla_orm.joinedload(model.venue, innerjoin=True).joinedload(
            offerers_models.Venue.pricing_point_links, innerjoin=True
        ),
    )

    return query


def _booking_comparison_tuple(booking: bookings_models.Booking) -> tuple:
    """Return a tuple of values, for a particular booking, that can be
    compared to `_PRICE_BOOKINGS_ORDER_CLAUSE`.
    """
    assert booking.dateUsed is not None  # helps mypy for `max()` below
    event_date_or_used_date = max(booking.stock.beginningDatetime or booking.dateUsed, booking.dateUsed)
    tupl = (
        max(_get_pricing_point_link(booking).timespan.lower, event_date_or_used_date),
        event_date_or_used_date,
        booking.dateUsed,
        booking.id,
    )
    if len(tupl) != len(_PRICE_BOOKINGS_ORDER_CLAUSE):
        raise RuntimeError("_booking_comparison_tuple has a wrong length.")
    return tupl


def lock_pricing_point(pricing_point_id: int) -> None:
    """Lock a pricing point (a venue) while we are doing some work that
    cannot be done while there are other running operations on the
    same pricing point.

    IMPORTANT: This must only be used within a transaction.

    The lock is automatically released at the end of the transaction.
    """
    return db_utils.acquire_lock(f"pricing-point-{pricing_point_id}")


def lock_reimbursement_point(reimbursement_point_id: int) -> None:
    """Lock a reimbursement point (a venue) while we are doing some
    work that cannot be done while there are other running operations
    on the same reimbursement point.

    IMPORTANT: This must only be used within a transaction.

    The lock is automatically released at the end of the transaction.
    """
    return db_utils.acquire_lock(f"reimbursement-point-{reimbursement_point_id}")


def get_non_cancelled_pricing_from_booking(
    booking: bookings_models.Booking | educational_models.CollectiveBooking,
) -> models.Pricing | None:
    if isinstance(booking, bookings_models.Booking):
        pricing_query = models.Pricing.query.filter_by(booking=booking)
    else:
        pricing_query = models.Pricing.query.filter_by(collectiveBooking=booking)

    return pricing_query.filter(models.Pricing.status != models.PricingStatus.CANCELLED).one_or_none()


def price_booking(
    booking: bookings_models.Booking | educational_models.CollectiveBooking,
) -> models.Pricing | None:
    # Handle bookings that were used when we fetched them in `price_bookings()`
    # but have been marked as unused since then.
    if not booking.dateUsed:
        return None
    pricing_point_id = _get_pricing_point_link(booking).pricingPointId

    is_booking_collective = isinstance(booking, educational_models.CollectiveBooking)

    with transaction():
        lock_pricing_point(pricing_point_id)

        # Now that we have acquired a lock, fetch the booking from the
        # database again so that we can make some final checks before
        # actually pricing the booking.
        booking = (
            reload_collective_booking_for_pricing(booking.id)
            if is_booking_collective
            else reload_booking_for_pricing(booking.id)
        )

        # Perhaps the booking has been marked as unused since we
        # fetched it before we acquired the lock.
        # If the status is REIMBURSED, it means the booking is
        # already priced.
        if (is_booking_collective and booking.status is not educational_models.CollectiveBookingStatus.USED) or (
            not is_booking_collective and booking.status is not bookings_models.BookingStatus.USED
        ):
            return None

        pricing_point = _get_pricing_point_link(booking).pricingPoint
        if pricing_point.id != pricing_point_id:
            # The pricing point has changed since the beginning of the
            # function. We should stop now, and let the booking be
            # priced later (when we can lock the right pricing point).
            return None

        # Pricing the same booking twice is not allowed (and would be
        # rejected by a database constraint, anyway), unless the
        # existing pricing has been cancelled.
        pricing = get_non_cancelled_pricing_from_booking(booking)
        if pricing:
            return pricing

        _delete_dependent_pricings(booking, "Deleted pricings priced too early")

        pricing = _price_booking(booking)
        db.session.add(pricing)

        db.session.commit()
    return pricing


def _get_revenue_period(value_date: datetime.datetime) -> typing.Tuple[datetime.datetime, datetime.datetime]:
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


def _get_pricing_point_id_and_current_revenue(
    booking: bookings_models.Booking,
) -> typing.Tuple[int, int]:
    """Return the id of the pricing point to use for the requested
    booking, and the current year revenue for this pricing point, NOT
    including the requested booking.
    """
    assert booking.dateUsed is not None  # helps mypy for `_get_revenue_period()`
    pricing_point_id = _get_pricing_point_link(booking).pricingPointId
    revenue_period = _get_revenue_period(booking.dateUsed)
    # Collective bookings must not be included in revenue.
    current_revenue = (
        bookings_models.Booking.query.join(models.Pricing)
        .filter(
            models.Pricing.pricingPointId == pricing_point_id,
            # The following filter is not strictly necessary, because
            # this function is called when the booking is being priced
            # (so there is no Pricing yet).
            models.Pricing.bookingId != booking.id,
            models.Pricing.valueDate.between(*revenue_period),
            models.Pricing.status.notin_(
                (
                    models.PricingStatus.CANCELLED,
                    models.PricingStatus.REJECTED,
                )
            ),
        )
        .with_entities(sqla.func.sum(bookings_models.Booking.amount * bookings_models.Booking.quantity))
        .scalar()
    )
    return pricing_point_id, utils.to_eurocents(current_revenue or 0)


def _price_booking(
    booking: bookings_models.Booking | educational_models.CollectiveBooking,
) -> models.Pricing:
    pricing_point_id, current_revenue = _get_pricing_point_id_and_current_revenue(booking)
    new_revenue = current_revenue
    is_booking_collective = isinstance(booking, educational_models.CollectiveBooking)
    # Collective bookings must not be included in revenue.
    if not is_booking_collective:
        new_revenue += utils.to_eurocents(booking.total_amount)
    rule_finder = reimbursement.CustomRuleFinder()
    # FIXME (dbaty, 2021-11-10): `revenue` here is in eurocents but
    # `get_reimbursement_rule` expects euros. Clean that once the
    # old payment code has been removed and the function accepts
    # eurocents instead.
    rule = reimbursement.get_reimbursement_rule(booking, rule_finder, utils.to_euros(new_revenue))
    amount = -utils.to_eurocents(rule.apply(booking))  # outgoing, thus negative
    # `Pricing.amount` equals the sum of the amount of all lines.
    lines = [
        models.PricingLine(
            amount=-utils.to_eurocents(
                booking.collectiveStock.price if is_booking_collective else booking.total_amount
            ),
            category=models.PricingLineCategory.OFFERER_REVENUE,
        )
    ]
    lines.append(
        models.PricingLine(
            amount=amount - lines[0].amount,
            category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
        )
    )

    assert booking.dateUsed  # helps mypy when setting Pricing.valueDate below
    return models.Pricing(
        status=_get_initial_pricing_status(booking),
        pricingPointId=pricing_point_id,
        valueDate=booking.dateUsed,
        amount=amount,
        standardRule=rule.description if not isinstance(rule, models.CustomReimbursementRule) else "",
        customRuleId=rule.id if isinstance(rule, models.CustomReimbursementRule) else None,
        revenue=new_revenue,
        lines=lines,
        bookingId=booking.id if not is_booking_collective else None,
        collectiveBookingId=booking.id if is_booking_collective else None,
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


def _delete_dependent_pricings(
    booking: bookings_models.Booking | educational_models.CollectiveBooking,
    log_message: str,
) -> None:
    """Delete pricings for bookings that should be priced after the
    requested ``booking``.

    See note in the module docstring for further details.
    """
    # Collective bookings are always reimbursed 100%, so there is no need to price them in
    # a specific order. In other words, there are no dependent pricings, and hence none to
    # delete.
    if isinstance(booking, educational_models.CollectiveBooking):
        return

    assert booking.dateUsed is not None  # helps mypy for `_get_revenue_period()`
    revenue_period_start, revenue_period_end = _get_revenue_period(booking.dateUsed)
    pricing_point_id = _get_pricing_point_link(booking).pricingPointId

    # Select the "right" pricing point link to use for each booking.
    # This is done in a CTE because we must first find those links,
    # and only then apply a filter to look for pricings to delete.
    pricings_with_right_pricing_point = (
        models.Pricing.query.filter_by(pricingPointId=pricing_point_id)
        .distinct(models.Pricing.id, offerers_models.VenuePricingPointLink.venueId)
        .join(
            offerers_models.VenuePricingPointLink,
            offerers_models.VenuePricingPointLink.venueId == models.Pricing.venueId,
        )
        .filter(
            offerers_models.VenuePricingPointLink.timespan.contains(booking.dateUsed)
            # If a pricing point was selected after the booking
            # validation, choose it. Corner cases: the link may have
            # ended, and it may even be followed by another pricing
            # point link. Using the first or the latest link in this
            # case both seems to make sense. We use the first link for
            # simplicity's sake and because these corner cases should
            # be rare.
            | (booking.dateUsed < sqla.func.lower(offerers_models.VenuePricingPointLink.timespan))
        )
        .order_by(
            models.Pricing.id,
            offerers_models.VenuePricingPointLink.venueId,
            sqla.func.lower(offerers_models.VenuePricingPointLink.timespan),
        )
        .with_entities(
            models.Pricing.id,
            models.Pricing.status,
            models.Pricing.bookingId,
            models.Pricing.valueDate,
            offerers_models.VenuePricingPointLink.id.label("pricing_point_link_id"),
        )
        .cte("pricings_with_right_pricing_point")
    )

    pricings = (
        db.session.query(
            pricings_with_right_pricing_point.c.id,
            pricings_with_right_pricing_point.c.bookingId,
            pricings_with_right_pricing_point.c.status,
            bookings_models.Booking.stockId,
        )
        # FIXME (dbaty, 2023-02-01): Here we JOIN on the `booking`
        # table again, even though we already did above in the
        # CTE. This is because _PRICE_BOOKINGS_ORDER_CLAUSE references
        # `Booking.dateUsed`, not our CTE. Perhaps we could trick it
        # to use a (new) CTE column if we alias it? Ditto for the JOIN
        # on `venue_pricing_point_link` table.
        .join(bookings_models.Booking, bookings_models.Booking.id == pricings_with_right_pricing_point.c.bookingId)
        .join(offers_models.Stock, offers_models.Stock.id == bookings_models.Booking.stockId)
        .join(
            offerers_models.VenuePricingPointLink,
            offerers_models.VenuePricingPointLink.id == pricings_with_right_pricing_point.c.pricing_point_link_id,
        )
        .filter(
            pricings_with_right_pricing_point.c.valueDate.between(revenue_period_start, revenue_period_end),
            sqla.func.ROW(*_PRICE_BOOKINGS_ORDER_CLAUSE) > sqla.func.ROW(*_booking_comparison_tuple(booking)),
        )
    )

    pricings = pricings.all()
    if not pricings:
        return
    pricing_ids = {p.id for p in pricings}
    bookings_already_priced = {p.bookingId for p in pricings}
    for pricing in pricings:
        if pricing.status not in models.DELETABLE_PRICING_STATUSES:
            if pricing_point_id in settings.FINANCE_OVERRIDE_PRICING_ORDERING_ON_PRICING_POINTS:
                pricing_ids.remove(pricing.id)
                bookings_already_priced.remove(pricing.bookingId)
                logger.info(
                    "Found non-deletable pricing for a pricing point that has an older booking to price or cancel (special case for problematic pricing points)",
                    extra={
                        "booking_being_priced_or_cancelled": booking.id,
                        "older_pricing": pricing.id,
                        "older_pricing_status": pricing.status,
                        "pricing_point": pricing_point_id,
                    },
                )
            else:
                logger.error(
                    "Found non-deletable pricing for a SIRET that has an older booking to price or cancel",
                    extra={
                        "booking_being_priced_or_cancelled": booking.id,
                        "older_pricing": pricing.id,
                        "older_pricing_status": pricing.status,
                        "pricing_point": pricing_point_id,
                    },
                )
                raise exceptions.NonCancellablePricingError()

    if not pricing_ids:
        return

    # Do not reuse the `pricings` query. It should not have changed
    # since the beginning of the function (since we should have an
    # exclusive lock on the pricing point to avoid that)... but I'd
    # rather be safe than sorry.
    lines = models.PricingLine.query.filter(models.PricingLine.pricingId.in_(pricing_ids))
    lines.delete(synchronize_session=False)
    logs = models.PricingLog.query.filter(models.PricingLog.pricingId.in_(pricing_ids))
    logs.delete(synchronize_session=False)
    pricings = models.Pricing.query.filter(models.Pricing.id.in_(pricing_ids))
    pricings.delete(synchronize_session=False)
    logger.info(
        log_message,
        extra={
            "booking_being_priced_or_cancelled": booking.id,
            "bookings_already_priced": bookings_already_priced,
            "pricing_point": pricing_point_id,
        },
    )


def cancel_pricing(
    booking: bookings_models.Booking | educational_models.CollectiveBooking, reason: models.PricingLogReason
) -> models.Pricing | None:
    if isinstance(booking, educational_models.CollectiveBooking):
        booking_attribute = models.Pricing.collectiveBooking
    else:
        booking_attribute = models.Pricing.booking
    pricing = models.Pricing.query.filter(
        booking_attribute == booking,
        models.Pricing.status != models.PricingStatus.CANCELLED,
    ).one_or_none()

    if not pricing:
        return None

    with transaction():
        lock_pricing_point(pricing.pricingPointId)

        pricing = models.Pricing.query.filter(
            booking_attribute == booking,
            models.Pricing.status != models.PricingStatus.CANCELLED,
        ).one_or_none()

        if not pricing:
            return None

        if pricing.status not in models.CANCELLABLE_PRICING_STATUSES:
            # That could happen if the offerer tries to mark as unused a
            # booking for which we have already created a cashflow.
            raise exceptions.NonCancellablePricingError()

        # We need to *cancel* the pricing of the requested booking AND
        # *delete* all pricings that depended on it (i.e. all pricings
        # for bookings used after that booking), so that we can price
        # them again.
        _delete_dependent_pricings(booking, "Deleted pricings that depended on cancelled pricing")

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
        db.session.commit()
        logger.info("Cancelled pricing", extra={"pricing": pricing.id})
    return pricing


def generate_cashflows_and_payment_files(cutoff: datetime.datetime) -> None:
    batch_id = generate_cashflows(cutoff)
    generate_payment_files(batch_id)


def _get_next_cashflow_batch_label() -> str:
    """Return the label of the next CashflowBatch."""
    latest_batch = models.CashflowBatch.query.order_by(models.CashflowBatch.cutoff.desc()).limit(1).one_or_none()
    if latest_batch is None:
        latest_number = 0
    else:
        latest_number = int(latest_batch.label[len(CASHFLOW_BATCH_LABEL_PREFIX) :])

    next_number = latest_number + 1
    return CASHFLOW_BATCH_LABEL_PREFIX + str(next_number)


def generate_cashflows(cutoff: datetime.datetime) -> int:
    """Generate a new CashflowBatch and a new cashflow for each
    reimbursement point for which there is money to transfer.
    """
    batch = models.CashflowBatch(cutoff=cutoff, label=_get_next_cashflow_batch_label())
    db.session.add(batch)
    db.session.commit()
    # Store now otherwise SQLAlchemy will make a SELECT to fetch the
    # id again after COMMITs in `_generate_cashflows()`.
    batch_id = batch.id
    _generate_cashflows(batch)
    return batch_id


def _generate_cashflows(batch: models.CashflowBatch) -> None:
    """Given an existing CashflowBatch and corresponding cutoff, generate
    a new cashflow for each reimbursement point for which there is
    money to transfer.

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
        # Bookings can now be priced even if BankInformation is not ACCEPTED,
        # but to generate cashflows we definitely need it.
        models.BankInformation.status == models.BankInformationStatus.ACCEPTED,
        # Even if a booking is marked as used prematurely, we should
        # wait for the event to happen.
        sqla.or_(
            sqla.and_(
                models.Pricing.bookingId.isnot(None),
                sqla.or_(
                    offers_models.Stock.beginningDatetime.is_(None),
                    offers_models.Stock.beginningDatetime < batch.cutoff,
                ),
            ),
            sqla.and_(
                models.Pricing.collectiveBookingId.isnot(None),
                educational_models.CollectiveStock.beginningDatetime < batch.cutoff,
            ),
        ),
    )

    def _mark_as_processed(pricings: sqla_orm.Query) -> None:
        pricings_to_update = models.Pricing.query.filter(
            models.Pricing.id.in_(pricings.with_entities(models.Pricing.id))
        )
        pricings_to_update.update(
            {"status": models.PricingStatus.PROCESSED},
            synchronize_session=False,
        )

    reimbursement_point_infos = (
        models.Pricing.query.filter(*filters)
        .outerjoin(models.Pricing.booking)
        .outerjoin(models.Pricing.collectiveBooking)
        .outerjoin(bookings_models.Booking.stock)
        .outerjoin(educational_models.CollectiveBooking.collectiveStock)
        .join(
            offerers_models.VenueReimbursementPointLink,
            offerers_models.VenueReimbursementPointLink.venueId == models.Pricing.venueId,
        )
        .filter(offerers_models.VenueReimbursementPointLink.timespan.contains(batch.cutoff))
        .join(
            models.BankInformation,
            models.BankInformation.venueId == offerers_models.VenueReimbursementPointLink.reimbursementPointId,
        )
        .outerjoin(models.CashflowPricing)
        .with_entities(
            offerers_models.VenueReimbursementPointLink.reimbursementPointId,
            models.BankInformation.id,
            sqla_func.array_agg(models.Pricing.venueId.distinct()),
        )
        .group_by(
            offerers_models.VenueReimbursementPointLink.reimbursementPointId,
            models.BankInformation.id,
        )
    )

    for reimbursement_point_id, bank_account_id, venue_ids in reimbursement_point_infos:
        log_extra = {
            "batch": batch_id,
            "reimbursement_point": reimbursement_point_id,
        }
        start = time.perf_counter()
        logger.info("Generating cashflow", extra=log_extra)
        try:
            with transaction():
                pricings = (
                    models.Pricing.query.outerjoin(models.Pricing.booking)
                    .outerjoin(bookings_models.Booking.stock)
                    .outerjoin(models.Pricing.collectiveBooking)
                    .outerjoin(educational_models.CollectiveBooking.collectiveStock)
                    .join(
                        models.BankInformation,
                        models.BankInformation.venueId == reimbursement_point_id,
                    )
                    .outerjoin(models.CashflowPricing)
                    .filter(
                        models.Pricing.venueId.in_(venue_ids),
                        *filters,
                    )
                )

                # Check integrity by looking for bookings whose amount
                # has been changed after they have been priced.
                diff = (
                    pricings.join(models.Pricing.lines)
                    .filter(
                        models.PricingLine.category == models.PricingLineCategory.OFFERER_REVENUE,
                        models.PricingLine.amount
                        != -100
                        * sqla.case(
                            (
                                bookings_models.Booking.id.isnot(None),
                                bookings_models.Booking.amount * bookings_models.Booking.quantity,
                            ),
                            else_=educational_models.CollectiveStock.price,
                        ),
                    )
                    .with_entities(models.Pricing.id)
                )
                diff = {_pricing_id for _pricing_id, in diff.all()}
                if diff:
                    logger.error(
                        "Found integrity error on booking prices vs. pricing lines",
                        extra={
                            "pricing_lines": diff,
                            "reimbursement_point": reimbursement_point_id,
                        },
                    )
                    continue

                total = pricings.with_entities(sqla.func.sum(models.Pricing.amount)).scalar()
                if not total:
                    # Mark as `PROCESSED` even if there is no cashflow, so
                    # that we will not process these pricings again.
                    _mark_as_processed(pricings)
                    continue
                cashflow = models.Cashflow(
                    batchId=batch_id,
                    reimbursementPointId=reimbursement_point_id,
                    bankAccountId=bank_account_id,
                    status=models.CashflowStatus.PENDING,
                    amount=total,
                )
                db.session.add(cashflow)
                links = [
                    models.CashflowPricing(
                        cashflowId=cashflow.id,
                        pricingId=pricing.id,
                    )
                    for pricing in pricings
                ]
                # Mark as `PROCESSED` now (and not before), otherwise the
                # `pricings` query above will be empty since it
                # filters on `VALIDATED` pricings.
                _mark_as_processed(pricings)
                db.session.bulk_save_objects(links)
                db.session.commit()
                elapsed = time.perf_counter() - start
                logger.info("Generated cashflow", extra=log_extra | {"elapsed": elapsed})
        except Exception:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not generate cashflow for reimbursement point %d",
                reimbursement_point_id,
                extra=log_extra,
            )


def generate_payment_files(batch_id: int) -> None:
    """Generate all payment files that are related to the requested
    CashflowBatch and mark all related Cashflow as ``UNDER_REVIEW``.
    """
    logger.info("Generating payment files")
    not_pending_cashflows = models.Cashflow.query.filter(
        models.Cashflow.batchId == batch_id,
        models.Cashflow.status != models.CashflowStatus.PENDING,
    ).count()
    if not_pending_cashflows:
        raise ValueError(
            f"Refusing to generate payment files for {batch_id}, "
            f"because {not_pending_cashflows} cashflows are not pending",
        )

    file_paths = {}
    logger.info("Generating reimbursement points file")
    file_paths["reimbursement_points"] = _generate_reimbursement_points_file()
    logger.info("Generating payments file")
    file_paths["payments"] = _generate_payments_file(batch_id)
    logger.info(
        "Finance files have been generated",
        extra={"paths": [str(path) for path in file_paths.values()]},
    )
    drive_folder_name = _get_drive_folder_name(batch_id)
    _upload_files_to_google_drive(drive_folder_name, file_paths.values())

    logger.info("Updating cashflow status")
    db.session.execute(
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
    """,
        params={
            "batch_id": batch_id,
            "pending": models.CashflowStatus.PENDING.value,
            "under_review": models.CashflowStatus.UNDER_REVIEW.value,
        },
    )
    db.session.commit()
    logger.info("Updated cashflow status")


def _get_drive_folder_name(batch_id: int) -> str:
    """Return the name of the directory (on Google Drive) that holds
    finance files for the requested cashflow batch.

    Looks like "2022-03 - jusqu'au 15 mars".
    """
    batch = models.CashflowBatch.query.get(batch_id)
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
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception(
            "Could not create folder and upload finance files to Google Drive",
            extra={"exc": exc},
        )
        return
    for path in paths:
        try:
            gdrive_api.create_file(parent_folder_id, path.name, path)
        except Exception as exc:  # pylint: disable=broad-except
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
    filename = filename_base + local_now.strftime("_%Y%m%d_%H%M%S") + ".csv"
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


def _generate_reimbursement_points_file() -> pathlib.Path:
    header = (
        "Identifiant du point de remboursement",
        "SIRET",
        "Raison sociale du point de remboursement",
        "IBAN",
        "BIC",
    )
    query = (
        offerers_models.Venue.query.join(offerers_models.Venue.bankInformation)
        .filter(
            offerers_models.Venue.id.in_(
                offerers_models.VenueReimbursementPointLink.query.with_entities(
                    offerers_models.VenueReimbursementPointLink.reimbursementPointId
                )
            )
        )
        .order_by(offerers_models.Venue.id)
        .with_entities(
            offerers_models.Venue.id,
            offerers_models.Venue.siret,
            offerers_models.Venue.name,
            models.BankInformation.iban.label("iban"),
            models.BankInformation.bic.label("bic"),
        )
    )
    row_formatter = lambda row: (
        human_ids.humanize(row.id),
        _clean_for_accounting(row.siret),
        _clean_for_accounting(row.name),
        _clean_for_accounting(row.iban),
        _clean_for_accounting(row.bic),
    )
    return _write_csv("reimbursement_points", header, rows=query, row_formatter=row_formatter)


def _clean_for_accounting(value: str) -> str:
    if not isinstance(value, str):
        return value
    # Accounting software dislikes quotes and newline characters.
    return value.strip().replace('"', "").replace("\n", "")


def _generate_payments_file(batch_id: int) -> pathlib.Path:
    header = [
        "Identifiant du point de remboursement",
        "SIRET du point de remboursement",
        "Libellé du point de remboursement",  # commercial name
        "Type de réservation",
        "Ministère",
        "Prix de la réservation",
        "Montant remboursé à l'offreur",
    ]
    bookings_query = (
        models.Pricing.query.filter_by(status=models.PricingStatus.PROCESSED)
        .join(models.Pricing.cashflows)
        .join(models.Pricing.booking)
        .filter(bookings_models.Booking.amount != 0)
        .join(
            offerers_models.Venue,
            offerers_models.Venue.id == models.Cashflow.reimbursementPointId,
        )
        .join(bookings_models.Booking.deposit)
        .filter(models.Cashflow.batchId == batch_id)
        .group_by(
            offerers_models.Venue.id,
            offerers_models.Venue.siret,
            models.Deposit.type,
        )
        .with_entities(
            offerers_models.Venue.id.label("reimbursement_point_id"),
            offerers_models.Venue.siret.label("reimbursement_point_siret"),
            offerers_models.Venue.common_name.label("reimbursement_point_name"),  # type: ignore[attr-defined]
            sqla_func.sum(bookings_models.Booking.amount * bookings_models.Booking.quantity).label("booking_amount"),
            models.Deposit.type.label("deposit_type"),
            sqla_func.sum(models.Pricing.amount).label("pricing_amount"),
        )
    )

    collective_bookings_query = (
        models.Pricing.query.filter_by(status=models.PricingStatus.PROCESSED)
        .join(models.Pricing.cashflows)
        .join(models.Pricing.collectiveBooking)
        .join(educational_models.CollectiveBooking.collectiveStock)
        .join(
            offerers_models.Venue,
            offerers_models.Venue.id == models.Cashflow.reimbursementPointId,
        )
        .join(educational_models.CollectiveBooking.educationalInstitution)
        .join(
            educational_models.EducationalDeposit,
            sqla.and_(
                educational_models.EducationalDeposit.educationalYearId
                == educational_models.CollectiveBooking.educationalYearId,
                educational_models.EducationalDeposit.educationalInstitutionId
                == educational_models.EducationalInstitution.id,
            ),
        )
        .filter(models.Cashflow.batchId == batch_id)
        .group_by(
            offerers_models.Venue.id,
            offerers_models.Venue.siret,
            educational_models.EducationalDeposit.ministry,
        )
        .with_entities(
            offerers_models.Venue.id.label("reimbursement_point_id"),
            offerers_models.Venue.siret.label("reimbursement_point_siret"),
            offerers_models.Venue.common_name.label("reimbursement_point_name"),  # type: ignore[attr-defined]
            sqla_func.sum(educational_models.CollectiveStock.price).label("booking_amount"),
            educational_models.EducationalDeposit.ministry.label("ministry"),
            sqla_func.sum(models.Pricing.amount).label("pricing_amount"),
        )
    )

    return _write_csv(
        "payment_details",
        header,
        rows=itertools.chain(bookings_query, collective_bookings_query),
        row_formatter=_payment_details_row_formatter,
    )


def _payment_details_row_formatter(sql_row: typing.Any) -> tuple:
    if hasattr(sql_row, "ministry"):
        booking_type = "EACC"
    elif sql_row.deposit_type == models.DepositType.GRANT_15_17:
        booking_type = "EACI"
    elif sql_row.deposit_type == models.DepositType.GRANT_18:
        booking_type = "PC"
    else:
        raise ValueError("Unknown booking type (not educational nor individual)")

    booking_total_amount = sql_row.booking_amount
    reimbursed_amount = utils.to_euros(-sql_row.pricing_amount)
    ministry = sql_row.ministry.name if hasattr(sql_row, "ministry") else ""

    return (
        human_ids.humanize(sql_row.reimbursement_point_id),
        _clean_for_accounting(sql_row.reimbursement_point_siret),
        _clean_for_accounting(sql_row.reimbursement_point_name),
        booking_type,
        ministry,
        booking_total_amount,
        reimbursed_amount,
    )


def find_reimbursement_rule(rule_reference: str | int) -> models.ReimbursementRule:
    # regular rule description
    if isinstance(rule_reference, str):
        for regular_rule in reimbursement.REGULAR_RULES:
            if rule_reference == regular_rule.description:
                return regular_rule
    # CustomReimbursementRule.id
    return models.CustomReimbursementRule.query.get(rule_reference)


def _make_invoice_line(
    group: models.RuleGroup,
    pricings: list,
    line_rate: decimal.Decimal | None = None,
) -> tuple[models.InvoiceLine, int]:
    reimbursed_amount = 0
    flat_lines = list(itertools.chain.from_iterable(pricing.lines for pricing in pricings))
    # positive
    contribution_amount = sum(
        line.amount for line in flat_lines if line.category == models.PricingLineCategory.OFFERER_CONTRIBUTION
    )
    # negative
    offerer_revenue = sum(
        line.amount for line in flat_lines if line.category == models.PricingLineCategory.OFFERER_REVENUE
    )
    passculture_commission = sum(
        line.amount for line in flat_lines if line.category == models.PricingLineCategory.PASS_CULTURE_COMMISSION
    )

    reimbursed_amount += offerer_revenue + contribution_amount + passculture_commission
    if offerer_revenue:
        # A rate is calculated for this line if we are using a
        # CustomRule with an amount instead of a rate.
        rate = line_rate or (decimal.Decimal(reimbursed_amount) / decimal.Decimal(offerer_revenue)).quantize(
            decimal.Decimal("0.0001")
        )
    else:
        rate = decimal.Decimal(0)
    invoice_line = models.InvoiceLine(
        label="Montant remboursé",
        group=group.value,
        contributionAmount=contribution_amount,
        reimbursedAmount=reimbursed_amount,
        rate=rate,
    )
    return invoice_line, reimbursed_amount


def _filter_invoiceable_cashflows(query: BaseQuery) -> BaseQuery:
    return (
        query.filter(models.Cashflow.status == models.CashflowStatus.UNDER_REVIEW).outerjoin(
            models.InvoiceCashflow,
            models.InvoiceCashflow.cashflowId == models.Cashflow.id,
        )
        # There should not be any invoice linked to a cashflow that is
        # UNDER_REVIEW, but having a safety belt here is almost free.
        .filter(models.InvoiceCashflow.invoiceId.is_(None))
    )


def generate_invoices() -> None:
    """Generate (and store) all invoices."""
    rows = _filter_invoiceable_cashflows(
        db.session.query(
            models.Cashflow.reimbursementPointId.label("reimbursement_point_id"),
            sqla_func.array_agg(models.Cashflow.id).label("cashflow_ids"),
        )
    ).group_by(models.Cashflow.reimbursementPointId)

    for row in rows:
        try:
            with transaction():
                extra = {"reimbursement_point_id": row.reimbursement_point_id}
                with log_elapsed(logger, "Generated and sent invoice", extra):
                    generate_and_store_invoice(
                        reimbursement_point_id=row.reimbursement_point_id,
                        cashflow_ids=row.cashflow_ids,
                    )
        except Exception as exc:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not generate invoice",
                extra={
                    "reimbursement_point_id": row.reimbursement_point_id,
                    "cashflow_ids": row.cashflow_ids,
                    "exc": str(exc),
                },
            )
    with log_elapsed(logger, "Generated CSV invoices file"):
        path = generate_invoice_file(datetime.date.today())
    batch_id = models.CashflowBatch.query.order_by(models.CashflowBatch.cutoff.desc()).first().id
    drive_folder_name = _get_drive_folder_name(batch_id)
    with log_elapsed(logger, "Uploaded CSV invoices file to Google Drive"):
        _upload_files_to_google_drive(drive_folder_name, [path])


def generate_invoice_file(invoice_date: datetime.date) -> pathlib.Path:
    header = [
        "Identifiant du point de remboursement",
        "Date du justificatif",
        "Référence du justificatif",
        "Identifiant valorisation",
        "Identifiant ticket de facturation",
        "type de ticket de facturation",
        "montant du ticket de facturation",
    ]
    query = (
        db.session.query(
            models.Invoice,
            models.Invoice.reimbursementPointId.label("reimbursement_point_id"),
            models.Pricing.id.label("pricing_id"),
            models.PricingLine.id.label("pricing_line_id"),
            models.PricingLine.category.label("pricing_line_category"),
            models.PricingLine.amount.label("pricing_line_amount"),
        )
        .join(models.Invoice.cashflows)
        .join(models.Cashflow.pricings)
        .join(models.Pricing.lines)
        .filter(sqla.cast(models.Invoice.date, sqla.Date) == invoice_date)
        .order_by(models.Invoice.id, models.Pricing.id, models.PricingLine.id)
    )
    row_formatter = lambda row: (
        human_ids.humanize(row.reimbursement_point_id),
        row.Invoice.date.date().isoformat(),
        row.Invoice.reference,
        row.pricing_id,
        row.pricing_line_id,
        row.pricing_line_category.value,
        abs(row.pricing_line_amount),
    )
    return _write_csv(
        "invoices",
        header,
        rows=query,
        row_formatter=row_formatter,
        compress=True,
    )


def generate_and_store_invoice(
    reimbursement_point_id: int,
    cashflow_ids: list[int],
) -> None:
    log_extra = {"reimbursement_point": reimbursement_point_id}
    with log_elapsed(logger, "Generated invoice model instance", log_extra):
        invoice = _generate_invoice(
            reimbursement_point_id=reimbursement_point_id,
            cashflow_ids=cashflow_ids,
        )
        if not invoice:
            return
    with log_elapsed(logger, "Generated invoice HTML", log_extra):
        invoice_html = _generate_invoice_html(invoice)
    with log_elapsed(logger, "Generated and stored PDF invoice", log_extra):
        _store_invoice_pdf(invoice_storage_id=invoice.storage_object_id, invoice_html=invoice_html)
    with log_elapsed(logger, "Sent invoice", log_extra):
        transactional_mails.send_invoice_available_to_pro_email(invoice)


def _generate_invoice(
    reimbursement_point_id: int,
    cashflow_ids: list[int],
) -> models.Invoice | None:
    # Acquire lock to avoid 2 simultaneous calls to this function (on
    # the same reimbursement point) generating 2 duplicate invoices.
    # This is also why we call `_filter_invoiceable_cashflows()` again
    # below.
    lock_reimbursement_point(reimbursement_point_id)
    invoice = models.Invoice(
        reimbursementPointId=reimbursement_point_id,
    )
    total_reimbursed_amount = 0
    cashflows = _filter_invoiceable_cashflows(
        models.Cashflow.query.filter(models.Cashflow.id.in_(cashflow_ids)).options(
            sqla_orm.joinedload(models.Cashflow.pricings)
            .options(sqla_orm.joinedload(models.Pricing.lines))
            .options(sqla_orm.joinedload(models.Pricing.customRule))
        )
    ).all()
    if not cashflows:
        # We should not end up here unless another instance of the
        # `generate_invoices` command is being executed simultaneously
        # and it has already processed this reimbursement point.
        return None
    pricings_and_rates_by_rule_group = defaultdict(list)
    pricings_by_custom_rule = defaultdict(list)

    cashflows_pricings = [cf.pricings for cf in cashflows]
    flat_pricings = list(itertools.chain.from_iterable(cashflows_pricings))
    for pricing in flat_pricings:
        rule_reference = pricing.standardRule or pricing.customRuleId
        rule = find_reimbursement_rule(rule_reference)
        if isinstance(rule, models.CustomReimbursementRule):
            pricings_by_custom_rule[rule].append(pricing)
        else:
            pricings_and_rates_by_rule_group[rule.group].append((pricing, rule.rate))  # type: ignore [attr-defined]

    invoice_lines = []
    for rule_group, pricings_and_rates in pricings_and_rates_by_rule_group.items():
        rates = defaultdict(list)
        for pricing, rate in pricings_and_rates:
            rates[rate].append(pricing)
        for rate, pricings in rates.items():
            invoice_line, reimbursed_amount = _make_invoice_line(rule_group, pricings, rate)
            invoice_lines.append(invoice_line)
            total_reimbursed_amount += reimbursed_amount

    for custom_rule, pricings in pricings_by_custom_rule.items():
        # An InvoiceLine rate will be calculated for a CustomRule with a set reimbursed amount
        invoice_line, reimbursed_amount = _make_invoice_line(custom_rule.group, pricings, custom_rule.rate)
        invoice_lines.append(invoice_line)
        total_reimbursed_amount += reimbursed_amount

    invoice.amount = total_reimbursed_amount
    # As of Python 3.9, DEFAULT_ENTROPY is 32 bytes
    invoice.token = secrets.token_urlsafe()
    scheme = reference_models.ReferenceScheme.get_and_lock(name="invoice.reference", year=datetime.date.today().year)
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
    models.Cashflow.query.filter(models.Cashflow.id.in_(cashflow_ids)).update(
        {"status": models.CashflowStatus.ACCEPTED},
        synchronize_session=False,
    )
    # Pricing.status: PROCESSED -> INVOICED
    # SQLAlchemy ORM cannot call `update()` if a query has been JOINed.
    db.session.execute(
        """
        UPDATE pricing
        SET status = :status
        FROM cashflow_pricing
        WHERE
          cashflow_pricing."pricingId" = pricing.id
          AND cashflow_pricing."cashflowId" IN :cashflow_ids
        """,
        {"status": models.PricingStatus.INVOICED.value, "cashflow_ids": tuple(cashflow_ids)},
    )
    # Booking.status: USED -> REIMBURSED (but keep CANCELLED as is)
    db.session.execute(
        """
        UPDATE booking
        SET
          status =
            CASE WHEN booking.status = CAST(:cancelled AS booking_status)
            THEN CAST(:cancelled AS booking_status)
            ELSE CAST(:reimbursed AS booking_status)
            END,
          "reimbursementDate" = now()
        FROM pricing, cashflow_pricing
        WHERE
          booking.id = pricing."bookingId"
          AND pricing.id = cashflow_pricing."pricingId"
          AND cashflow_pricing."cashflowId" IN :cashflow_ids
        """,
        {
            "cancelled": bookings_models.BookingStatus.CANCELLED.value,
            "reimbursed": bookings_models.BookingStatus.REIMBURSED.value,
            "cashflow_ids": tuple(cashflow_ids),
            "reimbursement_date": datetime.datetime.utcnow(),
        },
    )

    db.session.execute(
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
        (
            collective_booking.id = pricing."collectiveBookingId" OR
            (pricing."bookingId" is not null AND collective_booking."bookingId" = pricing."bookingId")
        )
        AND pricing.id = cashflow_pricing."pricingId"
        AND cashflow_pricing."cashflowId" IN :cashflow_ids
        """,
        {
            "cancelled": bookings_models.BookingStatus.CANCELLED.value,
            "reimbursed": bookings_models.BookingStatus.REIMBURSED.value,
            "cashflow_ids": tuple(cashflow_ids),
            "reimbursement_date": datetime.datetime.utcnow(),
        },
    )
    db.session.commit()
    return invoice


def get_invoice_period(invoice_date: datetime.datetime) -> typing.Tuple[datetime.datetime, datetime.datetime]:
    if invoice_date.day > 15:
        start_date = invoice_date.replace(day=1)
        end_date = start_date.replace(day=15)
    else:
        end_date = invoice_date.replace(day=1) - datetime.timedelta(days=1)
        start_date = end_date.replace(day=16)
    return start_date, end_date


def _prepare_invoice_context(invoice: models.Invoice) -> dict:
    # Easier to sort here and not in PostgreSQL, and not much slower
    # because there are very few cashflows (and usually only 1).
    cashflows = sorted(invoice.cashflows, key=lambda c: (c.creationDate, c.id))

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

    reimbursement_point = invoice.reimbursementPoint
    if reimbursement_point is None:
        raise ValueError("Could not generate invoice without reimbursement point")
    reimbursement_point_name = reimbursement_point.publicName or reimbursement_point.name
    bank_information = offerers_repository.BankInformation.query.filter(
        offerers_repository.BankInformation.venueId == reimbursement_point.id
    ).one()
    reimbursement_point_iban = bank_information.iban if bank_information else None
    period_start, period_end = get_invoice_period(invoice.date)

    return dict(
        invoice=invoice,
        cashflows=cashflows,
        groups=groups,
        reimbursement_point=reimbursement_point,
        reimbursement_point_name=reimbursement_point_name,
        reimbursement_point_iban=reimbursement_point_iban,
        total_used_bookings_amount=total_used_bookings_amount,
        total_contribution_amount=total_contribution_amount,
        total_reimbursed_amount=total_reimbursed_amount,
        period_start=period_start,
        period_end=period_end,
        reimbursements_by_venue=reimbursements_by_venue,
    )


def get_reimbursements_by_venue(
    invoice: models.Invoice,
) -> typing.ValuesView:
    common_columns: tuple = (offerers_models.Venue.id.label("venue_id"), offerers_models.Venue.common_name)

    pricing_query = (
        models.Invoice.query.join(models.Invoice.cashflows)
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
    collective_query = (
        pricing_query.with_entities(
            *common_columns,
            sqla_func.sum(models.Pricing.amount).label("reimbursed_amount"),
            sqla_func.sum(educational_models.CollectiveStock.price).label("booking_amount"),
        )
        .join(models.Pricing.collectiveBooking)
        .join(educational_models.CollectiveBooking.venue)
        .join(educational_models.CollectiveBooking.collectiveStock)
        .group_by(offerers_models.Venue.id, offerers_models.Venue.common_name)
        .order_by(offerers_models.Venue.id, offerers_models.Venue.common_name)
    )

    reimbursements_by_venue = {}
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
            "validated_booking_amount": -utils.to_eurocents(validated_booking_amount),
            "individual_amount": individual_amount,
        }

    for venue_pricing_info in collective_query:
        venue_id = venue_pricing_info.venue_id
        venue_common_name = venue_pricing_info.common_name
        reimbursed_amount = venue_pricing_info.reimbursed_amount
        booking_amount = -utils.to_eurocents(venue_pricing_info.booking_amount)
        if venue_pricing_info.venue_id in reimbursements_by_venue:
            reimbursements_by_venue[venue_pricing_info.venue_id]["reimbursed_amount"] += reimbursed_amount
            reimbursements_by_venue[venue_pricing_info.venue_id]["validated_booking_amount"] += booking_amount
        else:
            reimbursements_by_venue[venue_pricing_info.venue_id] = {
                "venue_name": venue_common_name,
                "reimbursed_amount": reimbursed_amount,
                "validated_booking_amount": booking_amount,
                "individual_amount": 0,
            }

    return reimbursements_by_venue.values()


def _generate_invoice_html(invoice: models.Invoice) -> str:
    context = _prepare_invoice_context(invoice)
    return render_template("invoices/invoice.html", **context)


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

    This function is to be used if multiple batches have been wrongly
    generated (for example because the cutoff of the first batch was
    wrong). The target batch must hence be the one with the right
    cutoff.
    """
    assert len(batches_to_remove) >= 1
    assert target_batch not in batches_to_remove

    batch_ids_to_remove = [batch.id for batch in batches_to_remove]
    reimbursement_point_ids = [
        id_
        for id_, in (
            models.Cashflow.query.filter(models.Cashflow.batchId.in_(batch_ids_to_remove))
            .with_entities(models.Cashflow.reimbursementPointId)
            .distinct()
        )
    ]
    with transaction():
        initial_sum = (
            models.Cashflow.query.filter(
                models.Cashflow.batchId.in_([b.id for b in batches_to_remove + [target_batch]]),
            )
            .with_entities(sqla_func.sum(models.Cashflow.amount))
            .scalar()
        )
        for reimbursement_point_id in reimbursement_point_ids:
            cashflows = models.Cashflow.query.filter(
                models.Cashflow.reimbursementPointId == reimbursement_point_id,
                models.Cashflow.batchId.in_(
                    batch_ids_to_remove + [target_batch.id],
                ),
            ).all()
            # One cashflow, wrong batch. Just change the batchId.
            if len(cashflows) == 1:
                models.Cashflow.query.filter_by(id=cashflows[0].id).update(
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
                models.Cashflow.query.filter(models.Cashflow.id.in_(cashflow_ids_to_remove))
                .with_entities(sqla_func.sum(models.Cashflow.amount))
                .scalar()
            )
            models.CashflowPricing.query.filter(models.CashflowPricing.cashflowId.in_(cashflow_ids_to_remove)).update(
                {"cashflowId": cashflow_to_keep.id},
                synchronize_session=False,
            )
            models.Cashflow.query.filter_by(id=cashflow_to_keep.id).update(
                {
                    "batchId": target_batch.id,
                    "amount": cashflow_to_keep.amount + sum_to_add,
                },
                synchronize_session=False,
            )
            models.CashflowLog.query.filter(
                models.CashflowLog.cashflowId.in_(cashflow_ids_to_remove),
            ).delete(synchronize_session=False)
            models.Cashflow.query.filter(
                models.Cashflow.id.in_(cashflow_ids_to_remove),
            ).delete(synchronize_session=False)
        models.CashflowBatch.query.filter(models.CashflowBatch.id.in_(batch_ids_to_remove)).delete(
            synchronize_session=False,
        )
        final_sum = (
            models.Cashflow.query.filter(
                models.Cashflow.batchId.in_(batch_ids_to_remove + [target_batch.id]),
            )
            .with_entities(sqla_func.sum(models.Cashflow.amount))
            .scalar()
        )
        assert final_sum == initial_sum
        db.session.commit()


def reload_booking_for_pricing(booking_id: int) -> bookings_models.Booking:
    query = bookings_models.Booking.query.filter_by(id=booking_id).options(
        sqla_orm.joinedload(bookings_models.Booking.stock, innerjoin=True).joinedload(
            offers_models.Stock.offer, innerjoin=True
        ),
        sqla_orm.joinedload(bookings_models.Booking.venue, innerjoin=True)
        .joinedload(offerers_models.Venue.pricing_point_links, innerjoin=True)
        .joinedload(offerers_models.VenuePricingPointLink.venue, innerjoin=True),
    )
    return query.one()


def reload_collective_booking_for_pricing(booking_id: int) -> educational_models.CollectiveBooking:
    query = educational_models.CollectiveBooking.query.filter_by(id=booking_id).options(
        sqla_orm.joinedload(educational_models.CollectiveBooking.collectiveStock, innerjoin=True).joinedload(
            educational_models.CollectiveStock.collectiveOffer, innerjoin=True
        ),
        sqla_orm.joinedload(educational_models.CollectiveBooking.venue, innerjoin=True)
        .joinedload(offerers_models.Venue.pricing_point_links, innerjoin=True)
        .joinedload(offerers_models.VenuePricingPointLink.venue, innerjoin=True),
    )
    return query.one()


def create_offerer_reimbursement_rule(
    offerer_id: int,
    subcategories: list[int],
    rate: decimal.Decimal,
    start_date: datetime.datetime,
    end_date: datetime.datetime = None,
) -> models.CustomReimbursementRule:
    return _create_reimbursement_rule(
        offerer_id=offerer_id,
        subcategories=subcategories,
        rate=rate,
        start_date=start_date,
        end_date=end_date,
    )


def create_offer_reimbursement_rule(
    offer_id: int,
    amount: decimal.Decimal,
    start_date: datetime.datetime,
    end_date: datetime.datetime = None,
) -> models.CustomReimbursementRule:
    return _create_reimbursement_rule(
        offer_id=offer_id,
        amount=amount,
        start_date=start_date,
        end_date=end_date,
    )


def _create_reimbursement_rule(
    offerer_id: int | None = None,
    offer_id: int | None = None,
    subcategories: list[int] | None = None,
    rate: decimal.Decimal | None = None,
    amount: decimal.Decimal | None = None,
    start_date: datetime.datetime = None,
    end_date: datetime.datetime | None = None,
) -> models.CustomReimbursementRule:
    subcategories = subcategories or []
    if not (bool(offerer_id) ^ bool(offer_id)):
        raise ValueError("Must provider offer or offerer (but not both)")
    if not (bool(rate) ^ bool(amount)):
        raise ValueError("Must provider rate or amount (but not both)")
    if not (bool(rate) or not bool(offerer_id)):
        raise ValueError("Rate must be specified only with an offerere (not with an offer)")
    if not (bool(amount) or not bool(offer_id)):
        raise ValueError("Amount must be specified only with an offer (not with an offerer)")
    if not start_date:
        raise ValueError("Start date must be provided")
    rule = models.CustomReimbursementRule(
        offererId=offerer_id,
        offerId=offer_id,
        subcategories=subcategories,
        rate=rate,  # only for offerers
        amount=amount,  # only for offers
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
    db.session.commit()
    return rule


def compute_underage_deposit_expiration_datetime(birth_date: datetime.date | None) -> datetime.datetime:
    if not birth_date:
        raise exceptions.UserNotGrantable("User has no validated birth date")
    return datetime.datetime.combine(birth_date, datetime.time(0, 0)) + relativedelta(years=18)


def get_granted_deposit(
    beneficiary: users_models.User,
    eligibility: users_models.EligibilityType,
    age_at_registration: int | None = None,
) -> models.GrantedDeposit | None:
    if eligibility == users_models.EligibilityType.UNDERAGE:
        if age_at_registration not in users_constants.ELIGIBILITY_UNDERAGE_RANGE:
            raise exceptions.UserNotGrantable("User is not eligible for underage deposit")

        return models.GrantedDeposit(
            amount=conf.GRANTED_DEPOSIT_AMOUNTS_FOR_UNDERAGE_BY_AGE[age_at_registration],
            expiration_date=compute_underage_deposit_expiration_datetime(beneficiary.validatedBirthDate),
            type=models.DepositType.GRANT_15_17,
            version=1,
        )

    if eligibility == users_models.EligibilityType.AGE18:
        expiration_date = datetime.datetime.utcnow().date() + relativedelta(years=conf.GRANT_18_VALIDITY_IN_YEARS)
        expiration_datetime = datetime.datetime.combine(expiration_date, datetime.time.max)
        return models.GrantedDeposit(
            amount=conf.GRANTED_DEPOSIT_AMOUNTS_FOR_18_BY_VERSION[2],
            expiration_date=expiration_datetime,
            type=models.DepositType.GRANT_18,
            version=2,
        )

    return None


def _recredit_user(user: users_models.User, deposit: models.Deposit) -> models.Recredit | None:
    if not user.age:
        return None

    recredit = models.Recredit(
        deposit=deposit,
        amount=conf.RECREDIT_TYPE_AMOUNT_MAPPING[conf.RECREDIT_TYPE_AGE_MAPPING[user.age]],
        recreditType=conf.RECREDIT_TYPE_AGE_MAPPING[user.age],
    )
    deposit.amount += recredit.amount
    return recredit


def create_deposit(
    beneficiary: users_models.User,
    deposit_source: str,
    eligibility: users_models.EligibilityType,
    age_at_registration: int | None = None,
) -> models.Deposit:
    """Create a new deposit for the user if there is no deposit yet."""
    granted_deposit = get_granted_deposit(
        beneficiary,
        eligibility,
        age_at_registration=age_at_registration,
    )

    if not granted_deposit:
        raise exceptions.UserNotGrantable()

    if repository.deposit_exists_for_beneficiary_and_type(beneficiary, granted_deposit.type):
        raise exceptions.DepositTypeAlreadyGrantedException(granted_deposit.type)

    if beneficiary.has_active_deposit:
        raise exceptions.UserHasAlreadyActiveDeposit()

    deposit = models.Deposit(
        version=granted_deposit.version,
        type=granted_deposit.type,
        amount=granted_deposit.amount,
        source=deposit_source,
        user=beneficiary,
        expirationDate=granted_deposit.expiration_date,
    )

    # Edge-cases: Validation of the registration occured over a birthday
    # Then we need to add recredit to compensate
    if (
        eligibility == users_models.EligibilityType.UNDERAGE
        and _can_be_recredited(beneficiary)
        and beneficiary.age
        and age_at_registration
    ):
        recredit = _recredit_user(beneficiary, deposit)
        if recredit:
            # Rare edge-case: Validation is longer than a year and started when user was 15
            if beneficiary.age == age_at_registration + 2:
                # User will get grant from registration age and recredit from current age
                # Therefore missing recredit is 16's one.
                additional_amount = conf.GRANTED_DEPOSIT_AMOUNTS_FOR_UNDERAGE_BY_AGE[16]
                deposit.amount += additional_amount

            db.session.add(recredit)

    return deposit


def _can_be_recredited(user: users_models.User) -> bool:
    return _has_celebrated_birthday_since_registration(user) and not _has_been_recredited(user)


def _has_celebrated_birthday_since_registration(user: users_models.User) -> bool:
    import pcapi.core.subscription.api as subscription_api

    first_registration_datetime = subscription_api.get_first_registration_date(
        user, user.validatedBirthDate, users_models.EligibilityType.UNDERAGE
    )
    if first_registration_datetime is None:
        logger.error("No registration date for user to be recredited", extra={"user_id": user.id})
        return False

    return first_registration_datetime.date() < typing.cast(datetime.date, user.latest_birthday)


def _has_been_recredited(user: users_models.User) -> bool:
    if user.deposit is None:
        return False
    if len(user.deposit.recredits) == 0:
        return False

    sorted_recredits = sorted(user.deposit.recredits, key=lambda recredit: recredit.dateCreated)
    return sorted_recredits[-1].recreditType == conf.RECREDIT_TYPE_AGE_MAPPING[user.age]  # type: ignore [index]


def recredit_underage_users() -> None:
    import pcapi.core.users.api as users_api

    sixteen_years_ago = datetime.datetime.utcnow() - relativedelta(years=16)
    eighteen_years_ago = datetime.datetime.utcnow() - relativedelta(years=18)

    user_ids = [
        result
        for result, in (
            users_models.User.query.filter(users_models.User.has_underage_beneficiary_role)
            .filter(users_models.User.validatedBirthDate > eighteen_years_ago)
            .filter(users_models.User.validatedBirthDate <= sixteen_years_ago)
            .with_entities(users_models.User.id)
            .all()
        )
    ]

    start_index = 0
    total_users_recredited = 0
    failed_users = []

    while start_index < len(user_ids):
        users = (
            users_models.User.query.filter(
                users_models.User.id.in_(user_ids[start_index : start_index + RECREDIT_UNDERAGE_USERS_BATCH_SIZE])
            )
            .options(sqla_orm.joinedload(users_models.User.deposits).joinedload(models.Deposit.recredits))
            .all()
        )

        users_to_recredit = [user for user in users if user.deposit and _can_be_recredited(user)]
        users_and_recredit_amounts = []
        with transaction():
            for user in users_to_recredit:
                try:
                    recredit = _recredit_user(user, user.deposit)
                    if recredit:  # recredit will be None is user's age is also None
                        users_and_recredit_amounts.append((user, recredit.amount))
                        user.recreditAmountToShow = recredit.amount if recredit.amount > 0 else None

                        db.session.add(user)
                        db.session.add(recredit)
                        total_users_recredited += 1
                except Exception as e:  # pylint: disable=broad-except
                    failed_users.append(user.id)
                    logger.exception("Could not recredit user %s: %s", user.id, e)
                    continue

        logger.info("Recredited %s underage users deposits", len(users_to_recredit))

        for user, recredit_amount in users_and_recredit_amounts:
            external_attributes_api.update_external_user(user)
            domains_credit = users_api.get_domains_credit(user)
            if not transactional_mails.send_recredit_email_to_underage_beneficiary(
                user, recredit_amount, domains_credit
            ):
                logger.error("Failed to send recredit email to: %s", user.email)

        start_index += RECREDIT_UNDERAGE_USERS_BATCH_SIZE
    logger.info("Recredited %s users successfully", total_users_recredited)
    if failed_users:
        logger.error("Failed to recredit %s users: %s", len(failed_users), failed_users)
