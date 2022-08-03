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
import hashlib
import itertools
import logging
import math
from operator import attrgetter
from operator import or_
import pathlib
import secrets
import tempfile
import typing
import zipfile

from flask import render_template
from flask_sqlalchemy import BaseQuery
import pytz
import sqlalchemy as sqla
from sqlalchemy import Date
from sqlalchemy import and_
from sqlalchemy import cast
import sqlalchemy.orm as sqla_orm
import sqlalchemy.sql.functions as sqla_func

from pcapi import settings
from pcapi.connectors import googledrive
import pcapi.core.bookings.models as bookings_models
import pcapi.core.educational.models as educational_models
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.logging import log_elapsed
from pcapi.core.mails.transactional.pro.invoice_available_to_pro import send_invoice_available_to_pro_email
from pcapi.core.object_storage import store_public_object
from pcapi.core.offerers import repository as offerers_repository
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.payments.models as payments_models
import pcapi.core.reference.models as reference_models
import pcapi.core.users.models as users_models
from pcapi.domain import reimbursement
from pcapi.models import db
from pcapi.models.feature import FeatureToggle
from pcapi.repository import transaction
from pcapi.utils import date as date_utils
from pcapi.utils import human_ids
from pcapi.utils import pdf as pdf_utils

from . import conf
from . import exceptions
from . import models
from . import utils
from . import validation


logger = logging.getLogger(__name__)

# When used through the cron, only price bookings that were used in 2022.
# Prior bookings will be priced manually.
# FIXME (dbaty, 2021-12-23): remove once prior bookings have been priced.
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

# The ORDER BY clause to be used to price bookings in a specific,
# stable order. If you change this, you MUST update
# `_legacy_booking_comparison_tuple()` below. This is legacy and
# can be removed when business units are deleted.
_LEGACY_PRICE_BOOKINGS_ORDER_CLAUSE = (
    sqla.func.greatest(
        sqla.func.lower(models.BusinessUnitVenueLink.timespan),
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

    use_pricing_point = FeatureToggle.USE_PRICING_POINT_FOR_PRICING.is_active()
    errored_business_unit_ids = set()
    errored_pricing_point_ids = set()

    # This is a quick hack to avoid fetching all bookings at once,
    # resulting in a very large session that is updated on each
    # commit, which takes a lot of time (up to 1 or 2 seconds per
    # commit).
    booking_query = _get_bookings_to_price(bookings_models.Booking, window, use_pricing_point)
    collective_booking_query = _get_bookings_to_price(educational_models.CollectiveBooking, window, use_pricing_point)
    loops = math.ceil(max(booking_query.count(), collective_booking_query.count()) / batch_size)

    def _get_loop_query(
        query: BaseQuery,
        last_booking: bookings_models.Booking | educational_models.CollectiveBooking | None,
        use_pricing_point: bool,
    ) -> BaseQuery:
        # We cannot use OFFSET and LIMIT because the loop "consumes"
        # bookings that have been priced (so the query will not return
        # them in the next loop), but keeps bookings that cannot be
        # priced (so the query WILL return them in the next loop).
        if last_booking:
            if isinstance(last_booking, bookings_models.Booking):
                if use_pricing_point:
                    clause = sqla.func.ROW(*_PRICE_BOOKINGS_ORDER_CLAUSE) > sqla.func.ROW(
                        *_booking_comparison_tuple(last_booking)
                    )
                else:
                    clause = sqla.func.ROW(*_LEGACY_PRICE_BOOKINGS_ORDER_CLAUSE) > sqla.func.ROW(
                        *_legacy_booking_comparison_tuple(last_booking)
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
        bookings = itertools.chain.from_iterable(
            (
                _get_loop_query(booking_query, last_booking, use_pricing_point),
                _get_loop_query(collective_booking_query, last_collective_booking, use_pricing_point),
            )
        )
        for booking in bookings:
            if isinstance(booking, bookings_models.Booking):
                last_booking = booking
            else:
                last_collective_booking = booking
            try:
                business_unit_id = pricing_point_id = None
                if use_pricing_point:
                    pricing_point_id = _get_pricing_point_link(booking).pricingPointId
                    if pricing_point_id in errored_pricing_point_ids:
                        continue
                else:
                    business_unit_id = booking.venue.businessUnitId
                    if business_unit_id in errored_business_unit_ids:
                        continue
                extra = {
                    "booking": booking.id,
                    "business_unit": business_unit_id,
                    "pricing_point": pricing_point_id,
                }
                with log_elapsed(logger, "Priced booking", extra):
                    price_booking(booking, use_pricing_point)
            except Exception as exc:  # pylint: disable=broad-except
                if use_pricing_point:
                    errored_pricing_point_ids.add(pricing_point_id)
                    logger.info(
                        "Ignoring further bookings from pricing point",
                        extra={"pricing_point": pricing_point_id},
                    )
                else:
                    errored_business_unit_ids.add(business_unit_id)
                    logger.info(
                        "Ignoring further bookings from business unit",
                        extra={"business_unit": business_unit_id},
                    )
                logger.exception(
                    "Could not price booking",
                    extra={
                        "booking": booking.id,
                        "business_unit": business_unit_id,
                        "pricing_point": pricing_point_id,
                        "exc": str(exc),
                    },
                )
        loops -= 1
        # Keep last booking in the session, we'll need it when calling
        # `_get_loop_query()` for the next loop.
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
    use_pricing_point: bool,
) -> BaseQuery:
    query = model.query
    if model == bookings_models.Booking:
        query = (
            query.filter(
                bookings_models.Booking.status == bookings_models.BookingStatus.USED,
                bookings_models.Booking.educationalBookingId.is_(None),
            )
            .join(bookings_models.Booking.stock)
            .outerjoin(
                models.Pricing,
                models.Pricing.bookingId == bookings_models.Booking.id,
            )
            .order_by(*(_PRICE_BOOKINGS_ORDER_CLAUSE if use_pricing_point else _LEGACY_PRICE_BOOKINGS_ORDER_CLAUSE))
        )
    else:
        query = query.outerjoin(
            models.Pricing,
            models.Pricing.collectiveBookingId == educational_models.CollectiveBooking.id,
        ).order_by(
            educational_models.CollectiveBooking.dateUsed,
            educational_models.CollectiveBooking.id,
        )

    query = query.filter(
        model.dateUsed.between(*window),  # type: ignore [union-attr]
        models.Pricing.id.is_(None),
    )

    query = query.join(model.venue)

    if use_pricing_point:
        query = query.join(offerers_models.Venue.pricing_point_links)
    else:
        query = (
            query.join(offerers_models.Venue.businessUnit)
            .filter(models.BusinessUnit.siret.isnot(None))
            .filter(models.BusinessUnit.status == models.BusinessUnitStatus.ACTIVE)
            .join(
                models.BusinessUnitVenueLink,
                sqla.and_(
                    models.BusinessUnitVenueLink.venueId == model.venueId,
                    models.BusinessUnitVenueLink.businessUnitId == models.BusinessUnit.id,
                ),
            )
        )

    query = query.options(
        sqla_orm.load_only(model.id),
        sqla_orm.load_only(model.dateUsed),
        # Our code does not access `Venue.id` but SQLAlchemy needs
        # it to build a `Venue` object (which we access through
        # `booking.venue`).
        sqla_orm.contains_eager(model.venue).load_only(
            offerers_models.Venue.id,
            offerers_models.Venue.businessUnitId,
        ),
    )

    if use_pricing_point:
        query = query.options(
            sqla_orm.joinedload(model.venue, innerjoin=True).joinedload(
                offerers_models.Venue.pricing_point_links, innerjoin=True
            )
        )

    return query


def _booking_comparison_tuple(booking: bookings_models.Booking) -> tuple:
    """Return a tuple of values, for a particular booking, that can be
    compared to `_PRICE_BOOKINGS_ORDER_CLAUSE`.
    """
    assert booking.dateUsed is not None  # helps mypy for `max()` below
    tupl = (
        max(
            _get_pricing_point_link(booking).timespan.lower,
            max((booking.stock.beginningDatetime or booking.dateUsed, booking.dateUsed)),
        ),
        max((booking.stock.beginningDatetime or booking.dateUsed, booking.dateUsed)),
        booking.dateUsed,
        booking.id,
    )
    if len(tupl) != len(_PRICE_BOOKINGS_ORDER_CLAUSE):
        raise RuntimeError("_booking_comparison_tuple has a wrong length.")
    return tupl


def _legacy_booking_comparison_tuple(booking: bookings_models.Booking) -> tuple:
    """Return a tuple of values, for a particular booking, that can be
    compared to `_LEGACY_PRICE_BOOKINGS_ORDER_CLAUSE`.
    """
    assert booking.dateUsed is not None  # helps mypy for `max()` below
    business_unit_venue_links = [
        link for link in booking.venue.businessUnit.venue_links if link.venueId == booking.venueId
    ]
    tupl = (
        max(
            business_unit_venue_links[-1].timespan.lower,
            max((booking.stock.beginningDatetime or booking.dateUsed, booking.dateUsed)),
        ),
        max((booking.stock.beginningDatetime or booking.dateUsed, booking.dateUsed)),
        booking.dateUsed,
        booking.id,
    )
    if len(tupl) != len(_LEGACY_PRICE_BOOKINGS_ORDER_CLAUSE):
        raise RuntimeError("_legacy_booking_comparison_tuple has a wrong length.")
    return tupl


def lock_pricing_point(pricing_point_id: int) -> None:
    """Lock a pricing point (a venue) while we are doing some work that
    cannot be done while there are other running operations on the
    same pricing point.

    IMPORTANT: This must only be used within a transaction.

    The lock is automatically released at the end of the transaction.
    """
    # We want a numeric lock identifier. Using `pricing_point_id`
    # would not be unique enough, so we add a prefix, hash the
    # resulting string, keep only the first 14 characters to avoid
    # collisions (and still stay within the range of PostgreSQL big
    # int type), and turn it back into an integer.
    lock_bytestring = f"pricing-point-{pricing_point_id}".encode()
    lock_id = int(hashlib.sha256(lock_bytestring).hexdigest()[:14], 16)
    db.session.execute(sqla.select([sqla.func.pg_advisory_xact_lock(lock_id)]))


def lock_business_unit(business_unit_id: int) -> None:
    """Lock a business unit while we are doing some work that cannot be
    done while there are other running operations on the same business
    unit.

    IMPORTANT: This must only be used within a transaction.

    The lock is automatically released at the end of the transaction.
    """
    log_extra = {"business_unit": business_unit_id}
    with log_elapsed(logger, "Acquired lock on business unit", log_extra):
        models.BusinessUnit.query.with_for_update(nowait=False).get(business_unit_id)


def get_non_cancelled_pricing_from_booking(
    booking: bookings_models.Booking | educational_models.CollectiveBooking,
) -> models.Pricing | None:
    if isinstance(booking, bookings_models.Booking):
        pricing_query = models.Pricing.query.filter_by(booking=booking)
    else:
        pricing_query = models.Pricing.query.filter(
            or_(
                models.Pricing.collectiveBookingId == booking.id,
                and_(models.Pricing.bookingId.isnot(None), models.Pricing.bookingId == booking.bookingId),
            )
        )

    return pricing_query.filter(models.Pricing.status != models.PricingStatus.CANCELLED).one_or_none()


def price_booking(
    booking: bookings_models.Booking | CollectiveBooking,
    use_pricing_point: bool,
) -> models.Pricing | None:
    if use_pricing_point:
        if not booking.venue.pricing_point_links:
            return None
        pricing_point_id = _get_pricing_point_link(booking).pricingPointId
    else:
        business_unit_id = booking.venue.businessUnitId
        if not business_unit_id:
            return None

    is_booking_collective = isinstance(booking, educational_models.CollectiveBooking)

    with transaction():
        if use_pricing_point:
            lock_pricing_point(pricing_point_id)
        else:
            lock_business_unit(business_unit_id)

        # Now that we have acquired a lock, fetch the booking from the
        # database again so that we can make some final checks before
        # actually pricing the booking.
        booking = (
            reload_collective_booking_for_pricing(booking.id, use_pricing_point)
            if is_booking_collective
            else reload_booking_for_pricing(booking.id, use_pricing_point)
        )

        # Perhaps the booking has been marked as unused since we
        # fetched it before we acquired the lock.
        # If the status is REIMBURSED, it means the booking is
        # already priced.
        if (is_booking_collective and booking.status is not CollectiveBookingStatus.USED) or (
            not is_booking_collective and booking.status is not bookings_models.BookingStatus.USED
        ):
            return None

        if use_pricing_point:
            if not booking.venue.pricing_point_links:
                return None
            pricing_point = _get_pricing_point_link(booking).pricingPoint
            if pricing_point.id != pricing_point_id:
                # The pricing point has changed since the beginning of the
                # function. We should stop now, and let the booking be
                # priced later (when we can lock the right pricing point).
                return None
        else:
            business_unit = booking.venue.businessUnit
            if not business_unit:
                return None
            if business_unit.id != business_unit_id:
                # The business unit has changed since the beginning of the
                # function. We should stop now, and let the booking be
                # priced later (when we can lock the new business unit).
                return None
            if not business_unit.siret:
                return None
            if business_unit.status != models.BusinessUnitStatus.ACTIVE:
                return None

        # Pricing the same booking twice is not allowed (and would be
        # rejected by a database constraint, anyway).
        pricing = get_non_cancelled_pricing_from_booking(booking)
        if pricing:
            return pricing

        _delete_dependent_pricings(booking, "Deleted pricings priced too early", use_pricing_point)

        pricing = _price_booking(booking, use_pricing_point)
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


def _get_siret_and_current_revenue(booking: bookings_models.Booking) -> typing.Tuple[str, int]:
    """Return the SIRET to use for the requested booking, and the current
    year revenue for this SIRET, NOT including the requested booking.
    """
    assert booking.dateUsed is not None  # helps mypy for `_get_revenue_period()`
    siret = booking.venue.siret or booking.venue.businessUnit.siret
    revenue_period = _get_revenue_period(booking.dateUsed)
    # I tried to be clever and store the accruing revenue on `Pricing`
    # for quick access. But my first attempt had a bug. I *think* that
    # the right way is to do this (but it has NOT been field-tested):
    #
    #     latest_pricing = (
    #         models.Pricing.query.filter_by(siret=siret)
    #         .filter(models.Pricing.valueDate.between(*revenue_period))
    #         # See `order_by` used in `price_bookings()`
    #         .order_by(models.Pricing.valueDate.desc(), models.Pricing.bookingId.desc())
    #         .first()
    #     )
    #
    # ... but a less error-prone and actually fast enough way is to
    # just calculate the sum on-the-fly.
    current_revenue = (
        bookings_models.Booking.query.join(models.Pricing)
        # Collective bookings must not be included in revenue.
        .filter(bookings_models.Booking.individualBookingId.isnot(None))
        .filter(
            models.Pricing.siret == siret,
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
    return siret, utils.to_eurocents(current_revenue or 0)


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
    current_revenue = (
        bookings_models.Booking.query.join(models.Pricing)
        # Collective bookings must not be included in revenue.
        .filter(bookings_models.Booking.individualBookingId.isnot(None))
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
    booking: bookings_models.Booking | CollectiveBooking,
    use_pricing_point: bool,
) -> models.Pricing:
    if use_pricing_point:
        pricing_point_id, current_revenue = _get_pricing_point_id_and_current_revenue(booking)
        siret = None
        business_unit_id = None
    else:
        siret, current_revenue = _get_siret_and_current_revenue(booking)
        business_unit_id = booking.venue.businessUnitId
        pricing_point_id = None
    new_revenue = current_revenue
    is_booking_collective = isinstance(booking, CollectiveBooking)
    # Collective bookings must not be included in revenue.
    if not is_booking_collective and booking.individualBookingId:
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
            amount=amount - lines[0].amount,  # type: ignore [operator]
            category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
        )
    )

    pricing_data = {
        "status": _get_initial_pricing_status(booking),
        "businessUnitId": business_unit_id,
        "siret": siret,
        "pricingPointId": pricing_point_id,
        "valueDate": booking.dateUsed,
        "amount": amount,
        "standardRule": rule.description if not isinstance(rule, payments_models.CustomReimbursementRule) else "",
        "customRuleId": rule.id if isinstance(rule, payments_models.CustomReimbursementRule) else None,
        "revenue": new_revenue,
        "lines": lines,
        "bookingId": booking.id if not is_booking_collective else None,
        "collectiveBookingId": booking.id if is_booking_collective else None,
    }

    return models.Pricing(**pricing_data)  # type: ignore [arg-type]


def _get_initial_pricing_status(booking: bookings_models.Booking | CollectiveBooking) -> models.PricingStatus:
    # In the future, we may set the pricing as "pending" (as in
    # "pending validation") for example if the business unit is new,
    # or if the offer or offerer has particular characteristics. For
    # now, we'll automatically mark it as validated, i.e. payable.
    return models.PricingStatus.VALIDATED


def _delete_dependent_pricings(
    booking: bookings_models.Booking | CollectiveBooking,
    log_message: str,
    use_pricing_point: bool,
) -> None:
    """Delete pricings for bookings that should be priced after the
    requested ``booking``.

    See note in the module docstring for further details.
    """
    # Collective bookings are always reimbursed 100%, so there is no need to price them in
    # a specific order. In other words, there are no dependent pricings, and hence none to
    # delete.
    if isinstance(booking, CollectiveBooking):
        return

    assert booking.dateUsed is not None  # helps mypy for `_get_revenue_period()`
    revenue_period_start, revenue_period_end = _get_revenue_period(booking.dateUsed)
    pricings = models.Pricing.query.filter(bookings_models.Booking.educationalBookingId.is_(None))
    if use_pricing_point:
        pricing_point_id = _get_pricing_point_link(booking).pricingPointId
        pricings = pricings.filter_by(pricingPointId=pricing_point_id)
    else:
        siret = booking.venue.siret or booking.venue.businessUnit.siret
        pricings = pricings.filter(models.Pricing.siret == siret)

    pricings = (
        pricings.join(models.Pricing.booking).join(bookings_models.Booking.stock).join(bookings_models.Booking.venue)
    )

    if use_pricing_point:
        pricings = pricings.join(offerers_models.Venue.pricing_point_links)
    else:
        pricings = pricings.join(
            models.BusinessUnitVenueLink,
            sqla.and_(
                models.BusinessUnitVenueLink.venueId == bookings_models.Booking.venueId,
                models.BusinessUnitVenueLink.businessUnitId == models.Pricing.businessUnitId,
            ),
        )

    pricings = pricings.filter(models.Pricing.valueDate.between(revenue_period_start, revenue_period_end))

    if use_pricing_point:
        clause = sqla.func.ROW(*_PRICE_BOOKINGS_ORDER_CLAUSE) > sqla.func.ROW(*_booking_comparison_tuple(booking))
    else:
        clause = sqla.func.ROW(*_LEGACY_PRICE_BOOKINGS_ORDER_CLAUSE) > sqla.func.ROW(
            *_legacy_booking_comparison_tuple(booking)
        )
    pricings = pricings.filter(clause)

    if not use_pricing_point:
        # De-duplicate if there was multiple venue-business unit links.
        pricings = pricings.distinct(models.Pricing.id)

    pricings = pricings.with_entities(
        models.Pricing.id,
        models.Pricing.bookingId,
        models.Pricing.status,
        # FIXME (dbaty, 2022-07-06): remove siret column when
        # FINANCE_OVERRIDE_PRICING_ORDERING_ON_SIRET_LIST is removed.
        models.Pricing.siret,
        bookings_models.Booking.stockId,
    ).all()
    if not pricings:
        return
    pricing_ids = {p.id for p in pricings}
    bookings_already_priced = {p.bookingId for p in pricings}
    for pricing in pricings:
        if pricing.status not in models.DELETABLE_PRICING_STATUSES:
            # FIXME (dbaty, 2022-04-06): there was a bug that caused
            # cashflows to be generated for events that had not yet
            # happened (see fix in 4d68e12dae26c54d8e03fcacdfdf3002b).
            # For impacted events, we will end up here but we cannot
            # do anything. Once all impacted events have happened
            # (i.e. after 2022-11-05), we can remove the `if` part of
            # the block (and always log an error and raise an
            # exception as we currently do in the `else` part).
            #
            # Stock identifiers have been exported with this query:
            #   SELECT id, "beginningDatetime" FROM stock
            #   WHERE id in (
            #     SELECT distinct(stock.id) FROM stock
            #     JOIN booking ON booking."stockId" = stock.id
            #     JOIN pricing ON pricing."bookingId" = booking.id
            #     WHERE stock."beginningDatetime" > now() AND pricing.status = 'invoiced'
            #   )
            #   ORDER BY "beginningDatetime";
            # fmt: off
            stock_ids = {
                # happen before end of April
                50064552, 50416251, 46417998, 23264071, 48486869, 49304599, 49474883, 43553116,
                45321327, 30776142, 51231535, 46406103, 50416326, 49096489, 49096374, 50222944,
                49096506, 49096405, 45964076, 49096446, 50222788, 49096475, 48487047, 23264187,
                44848126,
                # happen before end of May
                49726292, 30070444,
                # happen before end of June
                47917093, 47917071, 47916748, 50629375, 50276834, 47916807, 30833457,
                # happen before end of July
                49729242, 49729181, 49729227, 49729197, 49729210, 49923686, 50221016, 42193135,
                49343153, 49343119, 49343139, 49343148, 49343160, 50259980, 49425966, 48774702,
                50259991, 49425801,
                # happens before end of September
                30776103,
                # happens on 2022-11-05
                51132276,
            }
            # fmt: on
            if pricing.stockId in stock_ids:
                pricing_ids.remove(pricing.id)
                bookings_already_priced.remove(pricing.bookingId)
                logger.info(
                    "Found non-deletable pricing for a SIRET that has an older booking to price or cancel (special case for prematurely reimbursed event bookings)",
                    extra={
                        "booking_being_priced_or_cancelled": booking.id,
                        "older_pricing": pricing.id,
                        "older_pricing_status": pricing.status,
                    },
                )
            # FIXME (dbaty, 2022-07-06): temporarily disable pricing
            # ordering to get back on our feet. See PC-16084.
            elif pricing.siret in settings.FINANCE_OVERRIDE_PRICING_ORDERING_ON_SIRET_LIST:
                pricing_ids.remove(pricing.id)
                bookings_already_priced.remove(pricing.bookingId)
                logger.info(
                    "Found non-deletable pricing for a SIRET that has an older booking to price or cancel (special case for problematic venues)",
                    extra={
                        "booking_being_priced_or_cancelled": booking.id,
                        "older_pricing": pricing.id,
                        "older_pricing_status": pricing.status,
                        "siret": pricing.siret,
                    },
                )
            else:
                logger.error(
                    "Found non-deletable pricing for a SIRET that has an older booking to price or cancel",
                    extra={
                        "booking_being_priced_or_cancelled": booking.id,
                        "older_pricing": pricing.id,
                        "older_pricing_status": pricing.status,
                    },
                )
                raise exceptions.NonCancellablePricingError()

    # Do not reuse the `pricings` query. It should not have changed
    # since the beginning of the function (since we should have an
    # exclusive lock on the business unit to avoid that)... but I'd
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
        },
    )


def cancel_pricing(
    booking: bookings_models.Booking | CollectiveBooking, reason: models.PricingLogReason
) -> models.Pricing | None:
    use_pricing_point = FeatureToggle.USE_PRICING_POINT_FOR_PRICING.is_active()

    if use_pricing_point:
        if not booking.venue.pricing_point_links:
            return None
        if not booking.dateUsed:
            return None
        pricing_point_id = _get_pricing_point_link(booking).pricingPointId
    else:
        business_unit_id = booking.venue.businessUnitId
        if not business_unit_id:
            return None

    with transaction():
        if use_pricing_point:
            lock_pricing_point(pricing_point_id)
        else:
            lock_business_unit(business_unit_id)

        if isinstance(booking, CollectiveBooking):
            booking_attribute = models.Pricing.collectiveBooking
        else:
            booking_attribute = models.Pricing.booking
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
        _delete_dependent_pricings(booking, "Deleted pricings that depended on cancelled pricing", use_pricing_point)

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
    return batch_id  # type: ignore [return-value]


def _generate_cashflows(batch: models.CashflowBatch) -> None:
    """Given an existing CashflowBatch and corresponding cutoff, generate
    a new cashflow for each reimbursement point for which there is
    money to transfer.

    This is a private function that you should never called directly,
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

    use_reimbursement_point = FeatureToggle.USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS.is_active()
    if use_reimbursement_point:
        reimbursement_point_infos = (
            models.Pricing.query.filter(*filters)
            .outerjoin(models.Pricing.booking)
            .outerjoin(models.Pricing.collectiveBooking)
            .outerjoin(bookings_models.Booking.stock)
            .outerjoin(educational_models.CollectiveBooking.collectiveStock)
            .join(
                offerers_models.VenueReimbursementPointLink,
                offerers_models.VenueReimbursementPointLink.venueId
                == sqla_func.coalesce(
                    bookings_models.Booking.venueId,
                    educational_models.CollectiveBooking.venueId,
                ),
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
                sqla.func.array_remove(
                    sqla.func.array_cat(
                        sqla_func.array_agg(bookings_models.Booking.venueId),
                        sqla_func.array_agg(educational_models.CollectiveBooking.venueId),
                    ),
                    None,
                ),
            )
            .group_by(
                offerers_models.VenueReimbursementPointLink.reimbursementPointId,
                models.BankInformation.id,
            )
        )
        business_unit_infos = ()
    else:
        reimbursement_point_infos = ()
        business_unit_infos = (
            models.Pricing.query.filter(
                models.BusinessUnit.bankAccountId.isnot(None),
                *filters,
            )
            .outerjoin(models.Pricing.booking)
            .outerjoin(models.Pricing.collectiveBooking)
            .outerjoin(bookings_models.Booking.stock)
            .outerjoin(educational_models.CollectiveBooking.collectiveStock)
            .join(models.Pricing.businessUnit)
            .join(models.BusinessUnit.bankAccount)
            .outerjoin(models.CashflowPricing)
            .with_entities(models.Pricing.businessUnitId, models.BusinessUnit.bankAccountId)
            .distinct()
        )

    for info in reimbursement_point_infos or business_unit_infos:
        if use_reimbursement_point:
            reimbursement_point_id, bank_account_id, venue_ids = info
            business_unit_id = None
        else:
            business_unit_id, bank_account_id = info
            reimbursement_point_id = None
        log_extra = {
            "batch": batch_id,
            "reimbursement_point": reimbursement_point_id,
            "business_unit": business_unit_id,
        }
        logger.info("Generating cashflow", extra=log_extra)
        try:
            with transaction():
                if use_reimbursement_point:
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
                            sqla_func.coalesce(
                                bookings_models.Booking.venueId,
                                educational_models.CollectiveBooking.venueId,
                            ).in_(venue_ids),
                            *filters,
                        )
                    )
                else:
                    pricings = (
                        models.Pricing.query.outerjoin(models.Pricing.booking)
                        .outerjoin(bookings_models.Booking.stock)
                        .outerjoin(models.Pricing.collectiveBooking)
                        .outerjoin(educational_models.CollectiveBooking.collectiveStock)
                        .join(models.BusinessUnit)
                        .join(models.BusinessUnit.bankAccount)
                        .outerjoin(models.CashflowPricing)
                        .filter(
                            models.Pricing.businessUnitId == business_unit_id,
                            *filters,
                        )
                    )
                total = pricings.with_entities(sqla.func.sum(models.Pricing.amount)).scalar()
                if not total:
                    # Mark as `PROCESSED` even if there is no cashflow, so
                    # that we will not process these pricings again.
                    _mark_as_processed(pricings)
                    continue
                cashflow = models.Cashflow(
                    batchId=batch_id,
                    businessUnitId=business_unit_id,
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
                logger.info("Generated cashflow", extra=log_extra)
        except Exception:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not generate cashflows for a business unit",
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
    if FeatureToggle.USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS.is_active():
        logger.info("Generating reimbursement points file")
        file_paths["reimbursement_points"] = _generate_reimbursement_points_file()
    else:
        logger.info("Generating business units file")
        file_paths["business_units"] = _generate_business_units_file()
    logger.info("Generating payments file")
    file_paths["payments"] = _generate_payments_file(batch_id)
    logger.info("Generating wallets file")
    file_paths["wallets"] = _generate_wallets_file()
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
    filename: str,
    header: typing.Iterable,
    rows: typing.Iterable,
    row_formatter: typing.Callable[[typing.Iterable], typing.Iterable] = lambda row: row,
    compress: bool = False,
) -> pathlib.Path:

    # Store file in a dedicated directory within "/tmp". It's easier
    # to clean files in tests that way.
    path = pathlib.Path(tempfile.mkdtemp()) / f"{filename}.csv"
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


def _generate_business_units_file() -> pathlib.Path:
    header = (
        "Identifiant de la BU",
        "SIRET",
        "Raison sociale de la BU",
        "Libellé de la BU",  # actually, the commercial name of the related venue
        "IBAN",
        "BIC",
    )
    query = (
        models.BusinessUnit.query.join(models.BusinessUnit.bankAccount)
        # See `_generate_payments_file()` as for why we do an _outer_
        # join and not an _inner_ join here.
        .outerjoin(
            offerers_models.Venue,
            offerers_models.Venue.siret == models.BusinessUnit.siret,
        )
        .order_by(models.BusinessUnit.id)
        .with_entities(
            offerers_models.Venue.id.label("venue_id"),
            models.BusinessUnit.siret.label("business_unit_siret"),
            models.BusinessUnit.name.label("business_unit_name"),
            sqla_func.coalesce(
                offerers_models.Venue.publicName,
                offerers_models.Venue.name,
            ).label("venue_name"),
            models.BankInformation.iban.label("iban"),
            models.BankInformation.bic.label("bic"),
        )
    )
    row_formatter = lambda row: (
        human_ids.humanize(row.venue_id),
        _clean_for_accounting(row.business_unit_siret),
        _clean_for_accounting(row.business_unit_name),
        _clean_for_accounting(row.venue_name),
        _clean_for_accounting(row.iban),
        _clean_for_accounting(row.bic),
    )
    return _write_csv("business_units", header, rows=query, row_formatter=row_formatter)


def _clean_for_accounting(value: str) -> str:
    if not isinstance(value, str):
        return value
    # Accounting software dislikes quotes and newline characters.
    return value.strip().replace('"', "").replace("\n", "")


def _generate_payments_file(batch_id: int) -> pathlib.Path:
    use_reimbursement_point = FeatureToggle.USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS.is_active()
    if use_reimbursement_point:
        header = [
            "Identifiant du point de remboursement",
            "SIRET du point de remboursement",
            "Libellé du point de remboursement",  # commercial name
            "Type de réservation",
            "Ministère",
            "Prix de la réservation",
            "Montant remboursé à l'offreur",
        ]
    else:
        header = [
            "Identifiant de la BU",
            "SIRET de la BU",
            "Libellé de la BU",  # actually, the commercial name of the related venue
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
    )
    if use_reimbursement_point:
        bookings_query = bookings_query.join(
            offerers_models.Venue,
            offerers_models.Venue.id == models.Cashflow.reimbursementPointId,
        )
    else:
        bookings_query = (
            bookings_query.join(models.Pricing.businessUnit)
            # There should be a Venue with the same SIRET as the business
            # unit... but edition has been sloppy and there are
            # inconsistencies. To avoid excluding business unit, we do an
            # _outer_ join and not an _inner_ join here. Obviously, the
            # corresponding columns will be empty in the CSV file.
            # See also `_generate_business_units_file()` and `generate_invoice_file()`.
            .outerjoin(
                offerers_models.Venue,
                models.BusinessUnit.siret == offerers_models.Venue.siret,
            )
        )
    bookings_query = (
        bookings_query.join(bookings_models.Booking.individualBooking)
        .join(bookings_models.IndividualBooking.deposit)
        .filter(models.Cashflow.batchId == batch_id)
        .group_by(
            offerers_models.Venue.id,
            offerers_models.Venue.siret if use_reimbursement_point else models.BusinessUnit.siret,
            payments_models.Deposit.type,
        )
    )
    if use_reimbursement_point:
        bookings_query = bookings_query.with_entities(
            offerers_models.Venue.id.label("reimbursement_point_id"),
            offerers_models.Venue.siret.label("reimbursement_point_siret"),
            sqla_func.coalesce(
                offerers_models.Venue.publicName,
                offerers_models.Venue.name,
            ).label("reimbursement_point_name"),
            sqla_func.sum(bookings_models.Booking.amount * bookings_models.Booking.quantity).label("booking_amount"),
            payments_models.Deposit.type.label("deposit_type"),
            sqla_func.sum(models.Pricing.amount).label("pricing_amount"),
        )
    else:
        bookings_query = bookings_query.with_entities(
            offerers_models.Venue.id.label("business_unit_venue_id"),
            models.BusinessUnit.siret.label("business_unit_siret"),
            sqla_func.coalesce(
                offerers_models.Venue.publicName,
                offerers_models.Venue.name,
            ).label("business_unit_venue_name"),
            sqla_func.sum(bookings_models.Booking.amount * bookings_models.Booking.quantity).label("booking_amount"),
            payments_models.Deposit.type.label("deposit_type"),
            sqla_func.sum(models.Pricing.amount).label("pricing_amount"),
        )
    # FIXME (dbaty, 2021-11-30): other functions use `yield_per()`
    # but I am not sure it helps here. We have used
    # `pcapi.utils.db.get_batches` in the old-style payment code
    # and that may be what's best here.
    bookings_query = bookings_query.yield_per(1000)

    collective_bookings_query = (
        models.Pricing.query.filter_by(status=models.PricingStatus.PROCESSED)
        .join(models.Pricing.cashflows)
        .join(models.Pricing.collectiveBooking)
        .join(CollectiveBooking.collectiveStock)
    )
    if use_reimbursement_point:
        collective_bookings_query = collective_bookings_query.join(
            offerers_models.Venue,
            offerers_models.Venue.id == models.Cashflow.reimbursementPointId,
        )
    else:
        collective_bookings_query = (
            collective_bookings_query.join(models.Pricing.businessUnit)
            # There should be a Venue with the same SIRET as the business
            # unit... but edition has been sloppy and there are
            # inconsistencies. To avoid excluding business unit, we do an
            # _outer_ join and not an _inner_ join here. Obviously, the
            # corresponding columns will be empty in the CSV file.
            # See also `_generate_business_units_file()` and `generate_invoice_file()`.
            .outerjoin(
                offerers_models.Venue,
                models.BusinessUnit.siret == offerers_models.Venue.siret,
            )
        )
    collective_bookings_query = (
        collective_bookings_query.join(CollectiveBooking.educationalInstitution)
        .join(
            educational_models.EducationalDeposit,
            and_(
                educational_models.EducationalDeposit.educationalYearId == CollectiveBooking.educationalYearId,
                educational_models.EducationalDeposit.educationalInstitutionId
                == educational_models.EducationalInstitution.id,
            ),
        )
        .filter(models.Cashflow.batchId == batch_id)
        .group_by(
            offerers_models.Venue.id,
            offerers_models.Venue.siret if use_reimbursement_point else models.BusinessUnit.siret,
            educational_models.EducationalDeposit.ministry,
        )
    )
    if use_reimbursement_point:
        collective_bookings_query = collective_bookings_query.with_entities(
            offerers_models.Venue.id.label("reimbursement_point_id"),
            offerers_models.Venue.siret.label("reimbursement_point_siret"),
            sqla_func.coalesce(
                offerers_models.Venue.publicName,
                offerers_models.Venue.name,
            ).label("reimbursement_point_name"),
            sqla_func.sum(CollectiveStock.price).label("booking_amount"),
            educational_models.EducationalDeposit.ministry.label("ministry"),
            sqla_func.sum(models.Pricing.amount).label("pricing_amount"),
        )
    else:
        collective_bookings_query = collective_bookings_query.with_entities(
            offerers_models.Venue.id.label("business_unit_venue_id"),
            models.BusinessUnit.siret.label("business_unit_siret"),
            sqla_func.coalesce(
                offerers_models.Venue.publicName,
                offerers_models.Venue.name,
            ).label("business_unit_venue_name"),
            sqla_func.sum(CollectiveStock.price).label("booking_amount"),
            educational_models.EducationalDeposit.ministry.label("ministry"),
            sqla_func.sum(models.Pricing.amount).label("pricing_amount"),
        )
    # FIXME (dbaty, 2021-11-30): other functions use `yield_per()`
    # but I am not sure it helps here. We have used
    # `pcapi.utils.db.get_batches` in the old-style payment code
    # and that may be what's best here.
    collective_bookings_query = collective_bookings_query.yield_per(1000)

    return _write_csv(
        "payment_details",
        header,
        rows=itertools.chain(bookings_query, collective_bookings_query),
        row_formatter=_payment_details_row_formatter,
        compress=True,  # it's a large CSV file (> 100 Mb), we should compress it
    )


def _payment_details_row_formatter(sql_row) -> tuple:  # type: ignore [no-untyped-def]
    if hasattr(sql_row, "ministry"):
        booking_type = "EACC"
    elif sql_row.deposit_type == payments_models.DepositType.GRANT_15_17:
        booking_type = "EACI"
    elif sql_row.deposit_type == payments_models.DepositType.GRANT_18:
        booking_type = "PC"
    else:
        raise ValueError("Unknown booking type (not educational nor individual)")

    booking_total_amount = sql_row.booking_amount
    reimbursed_amount = utils.to_euros(-sql_row.pricing_amount)
    ministry = sql_row.ministry.name if hasattr(sql_row, "ministry") else ""

    # "legacy" means: use business unit. Otherwise, use reimbursement point.
    legacy = hasattr(sql_row, "business_unit_venue_id")
    return (
        human_ids.humanize(sql_row.business_unit_venue_id if legacy else sql_row.reimbursement_point_id),
        _clean_for_accounting(sql_row.business_unit_siret if legacy else sql_row.reimbursement_point_siret),
        _clean_for_accounting(sql_row.business_unit_venue_name if legacy else sql_row.reimbursement_point_name),
        booking_type,
        ministry,
        booking_total_amount,
        reimbursed_amount,
    )


def _generate_wallets_file() -> pathlib.Path:
    header = ["ID de l'utilisateur", "Solde théorique", "Solde réel"]
    # Warning: this query ignores the expiration date of deposits.
    query = (
        db.session.query(
            users_models.User.id.label("user_id"),
            sqla.func.get_wallet_balance(users_models.User.id, False).label("current_balance"),
            sqla.func.get_wallet_balance(users_models.User.id, True).label("real_balance"),
        )
        .filter(users_models.User.deposits != None)
        .order_by(users_models.User.id)
    )
    row_formatter = lambda row: (row.user_id, row.current_balance, row.real_balance)
    return _write_csv(
        "soldes_des_utilisateurs",
        header,
        rows=query,
        row_formatter=row_formatter,
        compress=True,
    )


def edit_business_unit(business_unit: models.BusinessUnit, siret: str) -> None:
    if business_unit.siret:
        raise ValueError("Cannot edit a business unit that already has a SIRET.")

    validation.check_business_unit_siret(business_unit, siret)
    venue = offerers_models.Venue.query.filter(offerers_models.Venue.siret == siret).one()
    business_unit.name = venue.publicName or venue.name
    business_unit.siret = siret
    db.session.add(business_unit)
    db.session.commit()


def find_reimbursement_rule(rule_reference: str | int) -> payments_models.ReimbursementRule:
    # regular rule description
    if isinstance(rule_reference, str):
        for regular_rule in reimbursement.REGULAR_RULES:
            if rule_reference == regular_rule.description:
                return regular_rule
    # CustomReimbursementRule.id
    return payments_models.CustomReimbursementRule.query.get(rule_reference)


def _make_invoice_line(
    group: conf.RuleGroups,
    pricings: list,
    line_rate: decimal.Decimal = None,
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


def generate_invoices() -> None:
    """Generate (and store) all invoices."""
    use_reimbursement_point = FeatureToggle.USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS.is_active()
    rows = (
        db.session.query(
            sqla.literal(None).label("business_unit_id")
            if use_reimbursement_point
            else models.Cashflow.businessUnitId.label("business_unit_id"),
            models.Cashflow.reimbursementPointId.label("reimbursement_point_id")
            if use_reimbursement_point
            else sqla.literal(None).label("reimbursement_point_id"),
            sqla_func.array_agg(models.Cashflow.id).label("cashflow_ids"),
        )
        .filter(models.Cashflow.status == models.CashflowStatus.UNDER_REVIEW)
        .outerjoin(
            models.InvoiceCashflow,
            models.InvoiceCashflow.cashflowId == models.Cashflow.id,
        )
        # There should not be any invoice linked to a cashflow that is
        # UNDER_REVIEW, but having a safety belt here is almost free.
        .filter(models.InvoiceCashflow.invoiceId.is_(None))
    )
    if use_reimbursement_point:
        rows = rows.group_by(models.Cashflow.reimbursementPointId)
    else:
        rows = rows.group_by(models.Cashflow.businessUnitId)

    for row in rows:
        try:
            with transaction():
                extra = {
                    "business_unit_id": row.business_unit_id,
                    "reimbursement_point_id": row.reimbursement_point_id,
                }
                with log_elapsed(logger, "Generated and sent invoice", extra):
                    generate_and_store_invoice(
                        business_unit_id=row.business_unit_id,
                        reimbursement_point_id=row.reimbursement_point_id,
                        cashflow_ids=row.cashflow_ids,
                        use_reimbursement_point=use_reimbursement_point,
                    )
        except Exception as exc:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not generate invoice",
                extra={
                    "business_unit": row.business_unit_id,
                    "reimbursement_point_id": row.reimbursement_point_id,
                    "cashflow_ids": row.cashflow_ids,
                    "exc": str(exc),
                },
            )
    with log_elapsed(logger, "Generated CSV invoices file"):
        path = generate_invoice_file(datetime.date.today(), use_reimbursement_point)
    batch_id = models.CashflowBatch.query.order_by(models.CashflowBatch.cutoff.desc()).first().id
    drive_folder_name = _get_drive_folder_name(batch_id)
    with log_elapsed(logger, "Uploaded CSV invoices file to Google Drive"):
        _upload_files_to_google_drive(drive_folder_name, [path])


def generate_invoice_file(invoice_date: datetime.date, use_reimbursement_point: bool) -> pathlib.Path:
    header = [
        "Identifiant du point de remboursement" if use_reimbursement_point else "Identifiant de la BU",
        "Date du justificatif",
        "Référence du justificatif",
        "Identifiant valorisation",
        "Identifiant ticket de facturation",
        "type de ticket de facturation",
        "montant du ticket de facturation",
    ]
    BusinessUnitVenue = sqla_orm.aliased(offerers_models.Venue)
    query = (
        db.session.query(
            models.Invoice,
            sqla.literal(None).label("business_unit_venue_id")
            if use_reimbursement_point
            else BusinessUnitVenue.id.label("business_unit_venue_id"),
            models.Invoice.reimbursementPointId.label("reimbursement_point_id")
            if use_reimbursement_point
            else sqla.literal(None).label("reimbursement_point_id"),
            models.Pricing.id.label("pricing_id"),
            models.PricingLine.id.label("pricing_line_id"),
            models.PricingLine.category.label("pricing_line_category"),
            models.PricingLine.amount.label("pricing_line_amount"),
        )
        .join(models.Invoice.cashflows)
        .join(models.Cashflow.pricings)
        .join(models.Pricing.lines)
    )
    if not use_reimbursement_point:
        query = (
            query.join(models.Invoice.businessUnit)
            # See `_generate_payments_file()` as for why we do an _outer_
            # join and not an _inner_ join here.
            .outerjoin(
                BusinessUnitVenue,
                models.BusinessUnit.siret == BusinessUnitVenue.siret,
            )
        )
    query = query.filter(cast(models.Invoice.date, Date) == invoice_date).order_by(
        models.Invoice.id, models.Pricing.id, models.PricingLine.id
    )

    row_formatter = lambda row: (
        human_ids.humanize(row.reimbursement_point_id if use_reimbursement_point else row.business_unit_venue_id),
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
    business_unit_id: int | None,
    reimbursement_point_id: int | None,
    cashflow_ids: list[int],
    use_reimbursement_point: bool,
) -> None:
    log_extra = {"business_unit": business_unit_id, "reimbursement_point": reimbursement_point_id}
    with log_elapsed(logger, "Generated invoice model instance", log_extra):
        invoice = _generate_invoice(
            business_unit_id=business_unit_id,
            reimbursement_point_id=reimbursement_point_id,
            cashflow_ids=cashflow_ids,
        )
    with log_elapsed(logger, "Generated invoice HTML", log_extra):
        invoice_html = _generate_invoice_html(invoice, use_reimbursement_point)
    with log_elapsed(logger, "Generated and stored PDF invoice", log_extra):
        _store_invoice_pdf(invoice_storage_id=invoice.storage_object_id, invoice_html=invoice_html)
    with log_elapsed(logger, "Sent invoice", log_extra):
        send_invoice_available_to_pro_email(invoice, use_reimbursement_point)


def _generate_invoice(
    business_unit_id: int | None,
    reimbursement_point_id: int | None,
    cashflow_ids: list[int],
) -> models.Invoice:
    invoice = models.Invoice(
        businessUnitId=business_unit_id,
        reimbursementPointId=reimbursement_point_id,
    )
    total_reimbursed_amount = 0
    cashflows = models.Cashflow.query.filter(models.Cashflow.id.in_(cashflow_ids)).options(
        sqla_orm.joinedload(models.Cashflow.pricings)
        .options(sqla_orm.joinedload(models.Pricing.lines))
        .options(sqla_orm.joinedload(models.Pricing.customRule))
    )
    pricings_and_rates_by_rule_group = defaultdict(list)
    pricings_by_custom_rule = defaultdict(list)

    cashflows_pricings = [cf.pricings for cf in cashflows]
    flat_pricings = list(itertools.chain.from_iterable(cashflows_pricings))
    for pricing in flat_pricings:
        rule_reference = pricing.standardRule or pricing.customRuleId
        rule = find_reimbursement_rule(rule_reference)
        if isinstance(rule, payments_models.CustomReimbursementRule):
            pricings_by_custom_rule[rule].append(pricing)
        else:
            pricings_and_rates_by_rule_group[rule.group].append((pricing, rule.rate))  # type: ignore [attr-defined]

    invoice_lines = []
    for rule_group, pricings_and_rates in pricings_and_rates_by_rule_group.items():
        rates = defaultdict(list)
        for pricing, rate in pricings_and_rates:
            rates[rate].append(pricing)
        for rate, pricings in rates.items():
            invoice_line, reimbursed_amount = _make_invoice_line(rule_group, pricings, rate)  # type: ignore [arg-type]
            invoice_lines.append(invoice_line)
            total_reimbursed_amount += reimbursed_amount

    for custom_rule, pricings in pricings_by_custom_rule.items():
        # An InvoiceLine rate will be calculated for a CustomRule with a set reimbursed amount
        invoice_line, reimbursed_amount = _make_invoice_line(custom_rule.group, pricings, custom_rule.rate)  # type: ignore [arg-type]
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
          "reimbursementDate" = :reimbursement_date
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
        "reimbursementDate" = :reimbursement_date
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


def _prepare_invoice_context(invoice: models.Invoice, use_reimbursement_point: bool) -> dict:
    invoice_lines = sorted(invoice.lines, key=lambda k: (k.group["position"], -k.rate))
    total_used_bookings_amount = 0
    total_contribution_amount = 0
    total_reimbursed_amount = 0
    invoice_groups: dict[str, tuple[str, list[models.InvoiceLine]]] = {}
    for group, lines in itertools.groupby(invoice_lines, attrgetter("group")):
        invoice_groups[group["label"]] = (group, list(lines))

    groups = []
    for group, lines in invoice_groups.values():  # type: ignore [assignment]
        contribution_subtotal = sum(line.contributionAmount for line in lines)
        total_contribution_amount += contribution_subtotal
        reimbursed_amount_subtotal = sum(line.reimbursedAmount for line in lines)
        total_reimbursed_amount += reimbursed_amount_subtotal
        used_bookings_subtotal = sum(line.bookings_amount for line in lines)
        total_used_bookings_amount += used_bookings_subtotal

        invoice_group = models.InvoiceLineGroup(
            position=group["position"],
            label=group["label"],
            contribution_subtotal=contribution_subtotal,
            reimbursed_amount_subtotal=reimbursed_amount_subtotal,
            used_bookings_subtotal=used_bookings_subtotal,
            lines=lines,  # type: ignore [arg-type]
        )
        groups.append(invoice_group)
    reimbursements_by_venue = get_reimbursements_by_venue(invoice)

    # FIXME (dbaty, 2022-07-18): once business units are not used
    # anymore, stop using `venue` in the template.
    if use_reimbursement_point:
        reimbursement_point = invoice.reimbursementPoint
        venue = None
    else:
        venue = offerers_repository.find_venue_by_siret(invoice.businessUnit.siret)  # type: ignore [arg-type]
        reimbursement_point = None
    period_start, period_end = get_invoice_period(invoice.date)  # type: ignore [arg-type]
    return dict(
        invoice=invoice,
        groups=groups,
        venue=venue,
        reimbursement_point=reimbursement_point,
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
    common_columns = (  # type: ignore [var-annotated]
        offerers_models.Venue.id.label("venue_id"),
        sqla_func.coalesce(offerers_models.Venue.publicName, offerers_models.Venue.name).label("venue_name"),
    )

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
            bookings_models.Booking.individualBookingId,
        )
        .join(models.Pricing.booking)
        .join(bookings_models.Booking.venue)
        .order_by(
            offerers_models.Venue.id,
            sqla_func.coalesce(offerers_models.Venue.publicName, offerers_models.Venue.name),
        )
    )
    collective_query = (
        pricing_query.with_entities(
            *common_columns,
            sqla_func.sum(models.Pricing.amount).label("reimbursed_amount"),
            sqla_func.sum(CollectiveStock.price).label("booking_amount"),
        )
        .join(models.Pricing.collectiveBooking)
        .join(CollectiveBooking.venue)
        .join(CollectiveBooking.collectiveStock)
        .group_by(
            offerers_models.Venue.id,
            sqla_func.coalesce(offerers_models.Venue.publicName, offerers_models.Venue.name),
        )
        .order_by(
            offerers_models.Venue.id,
            sqla_func.coalesce(offerers_models.Venue.publicName, offerers_models.Venue.name),
        )
    )

    reimbursements_by_venue = {}
    for (venue_id, venue_name), bookings in itertools.groupby(query, lambda x: (x.venue_id, x.venue_name)):
        validated_booking_amount = decimal.Decimal(0)
        reimbursed_amount = 0
        individual_amount = 0
        for booking in bookings:
            reimbursed_amount += booking.pricing_amount
            validated_booking_amount += decimal.Decimal(booking.booking_unit_amount) * booking.booking_quantity
            if booking.individualBookingId:
                individual_amount += booking.pricing_amount
        reimbursements_by_venue[venue_id] = {
            "venue_name": venue_name,
            "reimbursed_amount": reimbursed_amount,
            "validated_booking_amount": -utils.to_eurocents(validated_booking_amount),
            "individual_amount": individual_amount,
        }

    for venue_pricing_info in collective_query:
        venue_id = venue_pricing_info.venue_id
        venue_name = venue_pricing_info.venue_name
        reimbursed_amount = venue_pricing_info.reimbursed_amount
        booking_amount = -utils.to_eurocents(venue_pricing_info.booking_amount)
        if venue_pricing_info.venue_id in reimbursements_by_venue:
            reimbursements_by_venue[venue_pricing_info.venue_id]["reimbursed_amount"] += reimbursed_amount
            reimbursements_by_venue[venue_pricing_info.venue_id]["validated_booking_amount"] += booking_amount
        else:
            reimbursements_by_venue[venue_pricing_info.venue_id] = {
                "venue_name": venue_name,
                "reimbursed_amount": reimbursed_amount,
                "validated_booking_amount": booking_amount,
                "individual_amount": 0,
            }

    return reimbursements_by_venue.values()


def _generate_invoice_html(invoice: models.Invoice, use_reimbursement_point: bool) -> str:
    context = _prepare_invoice_context(invoice, use_reimbursement_point)
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
    business_unit_ids = [
        id_
        for id_, in (
            models.Cashflow.query.filter(models.Cashflow.batchId.in_(batch_ids_to_remove))
            .with_entities(models.Cashflow.businessUnitId)
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
        for business_unit_id in business_unit_ids:
            cashflows = models.Cashflow.query.filter(
                models.Cashflow.businessUnitId == business_unit_id,
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


def reload_booking_for_pricing(booking_id: int, use_pricing_point: bool) -> bookings_models.Booking:
    query = bookings_models.Booking.query.filter_by(id=booking_id).options(
        sqla_orm.joinedload(bookings_models.Booking.stock, innerjoin=True).joinedload(
            offers_models.Stock.offer, innerjoin=True
        ),
    )
    if use_pricing_point:
        query = query.options(
            sqla_orm.joinedload(bookings_models.Booking.venue, innerjoin=True)
            .joinedload(offerers_models.Venue.pricing_point_links, innerjoin=True)
            .joinedload(offerers_models.VenuePricingPointLink.venue, innerjoin=True)
        )
    else:
        query = query.options(
            sqla_orm.joinedload(bookings_models.Booking.venue, innerjoin=True)
            .joinedload(offerers_models.Venue.businessUnit, innerjoin=True)
            .joinedload(models.BusinessUnit.venue_links, innerjoin=True),
        )
    return query.one()


def reload_collective_booking_for_pricing(booking_id: int, use_pricing_point: bool) -> CollectiveBooking:
    query = CollectiveBooking.query.filter_by(id=booking_id).options(
        sqla_orm.joinedload(CollectiveBooking.collectiveStock, innerjoin=True).joinedload(
            CollectiveStock.collectiveOffer, innerjoin=True
        ),
    )
    if use_pricing_point:
        query = query.options(
            sqla_orm.joinedload(CollectiveBooking.venue, innerjoin=True)
            .joinedload(offerers_models.Venue.pricing_point_links, innerjoin=True)
            .joinedload(offerers_models.VenuePricingPointLink.venue, innerjoin=True)
        )
    else:
        query = query.options(
            sqla_orm.joinedload(CollectiveBooking.venue, innerjoin=True)
            .joinedload(offerers_models.Venue.businessUnit, innerjoin=True)
            .joinedload(models.BusinessUnit.venue_links, innerjoin=True),
        )
    return query.one()
