import datetime
import logging

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import pcapi.core.bookings.models as bookings_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.payments.models as payments_models
from pcapi.domain import reimbursement
from pcapi.models import db
from pcapi.repository import transaction

from . import exceptions
from . import models
from . import utils


logger = logging.getLogger(__name__)

DEFAULT_MAX_AGE_TO_PRICE = datetime.timedelta(minutes=60)


def price_bookings(max_age: datetime.timedelta = DEFAULT_MAX_AGE_TO_PRICE):
    """Price bookings that have been recently marked as used.

    This function is normally called by a cron job.
    """
    # The lower bound avoids querying the whole table. If all goes
    # well, bookings with an older `dateUsed` will have already been
    # priced.
    # The upper bound avoids selecting a very recent booking that may
    # have been COMMITed to the database just before another booking
    # with a slightly older `dateUsed`.
    now = datetime.datetime.utcnow()
    time_range = (now - max_age, now - datetime.timedelta(minutes=1))
    bookings = (
        bookings_models.Booking.query.filter(bookings_models.Booking.dateUsed.between(*time_range))
        .outerjoin(
            models.Pricing,
            models.Pricing.bookingId == bookings_models.Booking.id,
        )
        .filter(models.Pricing.id.is_(None))
        .join(bookings_models.Booking.venue)
        .filter(offerers_models.Venue.businessUnitId.isnot(None))
        .order_by(bookings_models.Booking.dateUsed, bookings_models.Booking.id)
        .options(
            sqla_orm.load_only(bookings_models.Booking.id),
            # Our code does not access `Venue.id` but SQLAlchemy needs
            # it to build a `Venue` object (which we access through
            # `booking.venue`).
            sqla_orm.contains_eager(bookings_models.Booking.venue).load_only(
                offerers_models.Venue.id,
                offerers_models.Venue.businessUnitId,
            ),
        )
    )
    errorred_business_unit_ids = set()
    for booking in bookings:
        try:
            if booking.venue.businessUnitId in errorred_business_unit_ids:
                continue
            price_booking(booking)
        except Exception as exc:  # pylint: disable=broad-except
            errorred_business_unit_ids.add(booking.venue.businessUnitId)
            logger.exception(
                "Could not price booking",
                extra={
                    "booking": booking.id,
                    "business_unit": booking.venue.businessUnitId,
                    "exc": str(exc),
                },
            )


def lock_business_unit(business_unit_id: int):
    """Lock a business unit while we are doing some work that cannot be
    done while there are other running operations on the same business
    unit.

    IMPORTANT: This must only be used within a transaction.

    The lock is automatically released at the end of the transaction.
    """
    models.BusinessUnit.query.with_for_update(nowait=False).get(business_unit_id)


def price_booking(booking: bookings_models.Booking) -> models.Pricing:
    business_unit_id = booking.venue.businessUnitId
    if not business_unit_id:
        return None

    with transaction():
        lock_business_unit(business_unit_id)

        # Now that we have acquired a lock, fetch the booking from the
        # database again so that we can make some final checks before
        # actually pricing the booking.
        booking = (
            bookings_models.Booking.query.filter_by(id=booking.id)
            .options(
                sqla_orm.joinedload(bookings_models.Booking.venue, innerjoin=True),
                sqla_orm.joinedload(bookings_models.Booking.stock, innerjoin=True).joinedload(
                    offers_models.Stock.offer, innerjoin=True
                ),
            )
            .one()
        )

        # Perhaps the booking has been marked as unused since we
        # fetched it before we acquired the lock.
        if not booking.isUsed:
            return None

        # Pricing the same booking twice is not allowed (and would be
        # rejected by a database constraint, anyway).
        pricing = models.Pricing.query.filter(
            models.Pricing.booking == booking,
            models.Pricing.status != models.PricingStatus.CANCELLED,
        ).one_or_none()
        if pricing:
            return pricing

        _delete_dependent_pricings(booking, "Deleted pricings priced too early")

        pricing = _price_booking(booking)
        db.session.add(pricing)

        db.session.commit()
    return pricing


def _price_booking(booking: bookings_models.Booking) -> models.Pricing:
    latest_pricing = (
        models.Pricing.query.filter_by(businessUnitId=booking.venue.businessUnitId)
        .order_by(models.Pricing.valueDate.desc())
        .first()
    )
    revenue = latest_pricing.revenue if latest_pricing else 0
    revenue += utils.to_eurocents(booking.total_amount)
    rule_finder = reimbursement.CustomRuleFinder()
    # FIXME (dbaty, 2021-11-10): `revenue` here is in eurocents but
    # `get_reimbursement_rule` expects euros. Clean that once the
    # old payment code has been removed and the function accepts
    # eurocents instead.
    rule = reimbursement.get_reimbursement_rule(booking, rule_finder, revenue / 100)

    amount = -utils.to_eurocents(rule.apply(booking))  # outgoing, thus negative
    # `Pricing.amount` equals the sum of the amount of all lines.
    lines = [
        models.PricingLine(
            amount=-utils.to_eurocents(booking.total_amount),
            category=models.PricingLineCategory.OFFERER_REVENUE,
        )
    ]
    lines.append(
        models.PricingLine(
            amount=amount - lines[0].amount,
            category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
        )
    )
    pricing = models.Pricing(
        status=_get_initial_pricing_status(booking),
        bookingId=booking.id,
        businessUnitId=booking.venue.businessUnitId,
        valueDate=booking.dateUsed,
        amount=amount,
        standardRule=rule.description if not isinstance(rule, payments_models.CustomReimbursementRule) else "",
        customRuleId=rule.id if isinstance(rule, payments_models.CustomReimbursementRule) else None,
        revenue=revenue,
        lines=lines,
    )
    return pricing


def _get_initial_pricing_status(booking: bookings_models.Booking) -> models.PricingStatus:
    # In the future, we may set the pricing as "pending" (as in
    # "pending validation") for example if the business unit is new,
    # or if the offer or offerer has particular characteristics. For
    # now, we'll automatically mark it as validated, i.e. payable.
    return models.PricingStatus.VALIDATED


def _delete_dependent_pricings(booking: bookings_models.Booking, log_message: str):
    """Delete pricings for bookings that have been used after the given
    ``booking``.

    FIXME (dbaty, 2021-11-03): review explanation, I am not sure it's
    clear...

    Bookings must be priced in the order in which they are marked as
    used, because:
    - Reimbursement threshold rules depend on the revenue as of the
      pricing, so the order in which bookings are priced is relevant;
    - We want the pricing to be replicable.

    As such:
    - When a booking is priced, we should delete any pricing that
      relates to a booking that has been marked as used later. It
      could happen if two HTTP requests ask to mark two bookings as
      used, and the COMMIT that updates the "first" one is delayed and
      we try to price the second one first.
    - When a pricing is cancelled, we should delete all subsequent
      pricings, so that related booking can be priced again. That
      happens only if we unmark a booking (i.e. mark as unused), which
      should be very rare.
    """
    business_unit_id = booking.venue.businessUnitId
    query = models.Pricing.query.filter(
        models.Pricing.businessUnitId == business_unit_id,
        sqla.or_(
            models.Pricing.valueDate > booking.dateUsed,
            sqla.and_(
                models.Pricing.valueDate == booking.dateUsed,
                models.Pricing.bookingId > booking.id,
            ),
        ),
    )
    pricings = query.all()
    if not pricings:
        return
    for pricing in pricings:
        if pricing.status not in models.DELETABLE_PRICING_STATUSES:
            logger.error(
                "Found non-deletable pricing for a business unit that has an older booking to price or cancel",
                extra={
                    "business_unit": pricing.businessUnitId,
                    "booking_being_priced_or_cancelled": booking.id,
                    "older_pricing": pricing.id,
                    "older_pricing_status": pricing.status,
                },
            )
            raise exceptions.NonCancellablePricingError()

    # Do not reuse `query` from above. It should not have changed
    # since the beginning of the function (since we should have an
    # exclusive lock on the business unit to avoid that)... but I'd
    # rather be safe than sorry.
    pricing_ids = [p.id for p in pricings]
    query = models.Pricing.query.filter(models.Pricing.id.in_(pricing_ids))
    query.delete(synchronize_session=False)
    logger.info(
        log_message,
        extra={
            "booking_being_priced": booking.id,
            "booking_already_priced": [p.bookingId for p in pricings],
            "business_unit": business_unit_id,
        },
    )


def cancel_pricing(booking: bookings_models.Booking, reason: models.PricingLogReason) -> models.Pricing:
    business_unit_id = booking.venue.businessUnitId
    if not business_unit_id:
        return None

    with transaction():
        lock_business_unit(business_unit_id)

        pricing = models.Pricing.query.filter(
            models.Pricing.booking == booking,
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
    return pricing
