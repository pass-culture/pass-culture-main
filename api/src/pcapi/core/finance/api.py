"""Finance-related functions.

Dependent pricings
==================

The reimbursement rule to be applied for each booking depends on the
yearly revenue to date. That means that we must price bookings in the
order in which they are marked as used. As such:

- When a booking B is priced, we should delete all pricings of
  bookings that have been marked as used later than booking B. It
  could happen if two HTTP requests ask to mark two bookings as used,
  and the COMMIT that updates the "first" one is delayed and we try to
  price the second one first. This is why we have a grace period in
  `price_bookings` that avoids pricing bookings that have been very
  recently marked as used.

 - When a pricing is cancelled, we should delete all dependent
   pricings (since the revenue will be different), so that related
   booking can be priced again. That happens only if we mark a booking
   as unused, which should be very rare.
"""

from collections import defaultdict
import csv
import datetime
import decimal
import itertools
import logging
from operator import attrgetter
import pathlib
import secrets
import tempfile
import time
import typing
import zipfile

from flask import render_template
import pytz
import sqlalchemy as sqla
from sqlalchemy import Date
from sqlalchemy import cast
import sqlalchemy.orm as sqla_orm
import sqlalchemy.sql.functions as sqla_func

from pcapi import settings
import pcapi.core.bookings.models as bookings_models
from pcapi.core.finance import models
from pcapi.core.mails.transactional.pro.invoice_available_to_pro import send_invoice_available_to_pro_email
from pcapi.core.object_storage import store_public_object
from pcapi.core.offerers import repository as offerers_repository
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.payments.models as payments_models
import pcapi.core.payments.utils as payments_utils
import pcapi.core.reference.models as reference_models
from pcapi.domain import reimbursement
from pcapi.models import db
from pcapi.models.bank_information import BankInformation
from pcapi.models.bank_information import BankInformationStatus
from pcapi.repository import transaction
from pcapi.repository import user_queries
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


def price_bookings(min_date: datetime.datetime = MIN_DATE_TO_PRICE):
    """Price bookings that have been recently marked as used.

    This function is normally called by a cron job.
    """
    # The upper bound on `dateUsed` avoids selecting a very recent
    # booking that may have been COMMITed to the database just before
    # another booking with a slightly older `dateUsed` (see note in
    # module docstring).
    threshold = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
    window = (min_date, threshold)
    bookings = (
        bookings_models.Booking.query.filter(bookings_models.Booking.dateUsed.between(*window))
        .outerjoin(
            models.Pricing,
            models.Pricing.bookingId == bookings_models.Booking.id,
        )
        .filter(models.Pricing.id.is_(None))
        .join(bookings_models.Booking.venue)
        .join(offerers_models.Venue.businessUnit)
        # FIXME (dbaty, 2021-12-08): we can get rid of this filter
        # once BusinessUnit.siret is set as NOT NULLable.
        .filter(models.BusinessUnit.siret.isnot(None))
        .filter(models.BusinessUnit.status == models.BusinessUnitStatus.ACTIVE)
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
            start = time.perf_counter()
            price_booking(booking)
            elapsed = time.perf_counter() - start
            logger.info(
                "Priced booking",
                extra={
                    "booking": booking.id,
                    "business_unit_id": booking.venue.businessUnitId,
                    "elapsed": elapsed,
                },
            )
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
    logger.info("Acquiring lock on business unit", extra={"business_unit": business_unit_id})
    models.BusinessUnit.query.with_for_update(nowait=False).get(business_unit_id)
    logger.info("Acquired lock on business unit", extra={"business_unit": business_unit_id})


def price_booking(booking: bookings_models.Booking) -> models.Pricing:
    # pylint: disable=too-many-return-statements
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
                sqla_orm.joinedload(bookings_models.Booking.venue, innerjoin=True).joinedload(
                    offerers_models.Venue.businessUnit, innerjoin=True
                ),
                sqla_orm.joinedload(bookings_models.Booking.stock, innerjoin=True).joinedload(
                    offers_models.Stock.offer, innerjoin=True
                ),
            )
            .one()
        )

        # Perhaps the booking has been marked as unused since we
        # fetched it before we acquired the lock.
        # If the status is REIMBURSED, it means the booking is
        # already priced.
        if booking.status is not bookings_models.BookingStatus.USED:
            return None

        business_unit = booking.venue.businessUnit
        # FIXME (dbaty, 2021-12-08): we can get rid of this condition
        # once BusinessUnit.siret is set as NOT NULLable.
        if not business_unit.siret:
            return None
        if business_unit.status != models.BusinessUnitStatus.ACTIVE:
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


def _get_revenue_period(value_date: datetime.datetime) -> [datetime.datetime, datetime.datetime]:
    """Return a datetime (year) period for the given value date, i.e. the
    first and last seconds of the year of the ``value_date``.
    """
    year = value_date.replace(tzinfo=pytz.utc).astimezone(payments_utils.ACCOUNTING_TIMEZONE).year
    first_second = payments_utils.ACCOUNTING_TIMEZONE.localize(
        datetime.datetime.combine(
            datetime.date(year, 1, 1),
            datetime.time.min,
        )
    ).astimezone(pytz.utc)
    last_second = payments_utils.ACCOUNTING_TIMEZONE.localize(
        datetime.datetime.combine(
            datetime.date(year, 12, 31),
            datetime.time.max,
        )
    ).astimezone(pytz.utc)
    return first_second, last_second


def _get_siret_and_current_revenue(booking: bookings_models.Booking) -> typing.Union[str, int]:
    """Return the SIRET to use for the requested booking, and the current
    year revenue for this SIRET, NOT including the requested booking.
    """
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
        .filter(
            models.Pricing.siret == siret,
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


def _price_booking(booking: bookings_models.Booking) -> models.Pricing:
    siret, current_revenue = _get_siret_and_current_revenue(booking)
    new_revenue = current_revenue + utils.to_eurocents(booking.total_amount)
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
        siret=siret,
        valueDate=booking.dateUsed,
        amount=amount,
        standardRule=rule.description if not isinstance(rule, payments_models.CustomReimbursementRule) else "",
        customRuleId=rule.id if isinstance(rule, payments_models.CustomReimbursementRule) else None,
        revenue=new_revenue,
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

    See note in the module docstring for further details.
    """
    siret = booking.venue.siret or booking.venue.businessUnit.siret
    _period_start, period_end = _get_revenue_period(booking.dateUsed)
    query = models.Pricing.query.filter(
        models.Pricing.siret == siret,
        sqla.or_(
            sqla.and_(
                models.Pricing.valueDate > booking.dateUsed,
                models.Pricing.valueDate <= period_end,
            ),
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
                "Found non-deletable pricing for a SIRET that has an older booking to price or cancel",
                extra={
                    "siret": pricing.siret,
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
    lines = models.PricingLine.query.filter(models.PricingLine.pricingId.in_(pricing_ids))
    lines.delete(synchronize_session=False)
    logs = models.PricingLog.query.filter(models.PricingLog.pricingId.in_(pricing_ids))
    logs.delete(synchronize_session=False)
    bookings_already_priced = [p.bookingId for p in pricings]
    pricings = models.Pricing.query.filter(models.Pricing.id.in_(pricing_ids))
    pricings.delete(synchronize_session=False)
    logger.info(
        log_message,
        extra={
            "booking_being_priced_or_cancelled": booking.id,
            "bookings_already_priced": bookings_already_priced,
            "siret": siret,
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


def generate_cashflows_and_payment_files(cutoff: datetime.datetime):
    batch_id = generate_cashflows(cutoff)
    generate_payment_files(batch_id)


def generate_cashflows(cutoff: datetime.datetime) -> int:
    """Generate a new CashflowBatch and a new cashflow for each business
    unit for which there is money to transfer.
    """
    logger.info("Started to generate cashflows")
    batch = models.CashflowBatch(cutoff=cutoff)
    db.session.add(batch)
    db.session.flush()
    batch_id = batch.id  # access _before_ COMMIT to avoid extra SELECT
    db.session.commit()

    filters = (
        models.Pricing.status == models.PricingStatus.VALIDATED,
        models.Pricing.valueDate < cutoff,
        # Even if a booking is marked as used prematurely, we should
        # wait for the event to happen.
        sqla.or_(
            offers_models.Stock.beginningDatetime.is_(None),
            offers_models.Stock.beginningDatetime < cutoff,
        ),
        # We should not have any validated pricing with a cashflow,
        # this is a safety belt.
        models.CashflowPricing.pricingId.is_(None),
        # Bookings can now be priced even if BankInformation is not ACCEPTED,
        # but to generate cashflows we definitely need it.
        BankInformation.status == BankInformationStatus.ACCEPTED,
    )

    def _mark_as_processed(pricings):
        pricings_to_update = models.Pricing.query.filter(
            models.Pricing.id.in_(pricings.with_entities(models.Pricing.id))
        )
        pricings_to_update.update(
            {"status": models.PricingStatus.PROCESSED},
            synchronize_session=False,
        )

    business_unit_ids_and_bank_account_ids = (
        models.Pricing.query.filter(
            models.BusinessUnit.bankAccountId.isnot(None),
            *filters,
        )
        .join(models.Pricing.booking)
        .join(bookings_models.Booking.stock)
        .join(models.Pricing.businessUnit)
        .join(models.BusinessUnit.bankAccount)
        .outerjoin(models.CashflowPricing)
        .with_entities(models.Pricing.businessUnitId, models.BusinessUnit.bankAccountId)
        .distinct()
    )
    for business_unit_id, bank_account_id in business_unit_ids_and_bank_account_ids:
        logger.info("Generating cashflow", extra={"business_unit": business_unit_id})
        try:
            with transaction():
                pricings = (
                    models.Pricing.query.join(models.BusinessUnit)
                    .join(models.BusinessUnit.bankAccount)
                    .join(models.Pricing.booking)
                    .join(bookings_models.Booking.stock)
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
                    bankAccountId=bank_account_id,
                    status=models.CashflowStatus.PENDING,
                    amount=total,
                )
                db.session.add(cashflow)
                links = [models.CashflowPricing(cashflowId=cashflow.id, pricingId=pricing.id) for pricing in pricings]
                # Mark as `PROCESSED` now (and not before), otherwise the
                # `pricings` query above will be empty since it
                # filters on `VALIDATED` pricings.
                _mark_as_processed(pricings)
                db.session.bulk_save_objects(links)
                db.session.commit()
                logger.info("Generated cashflow", extra={"business_unit": business_unit_id})
        except Exception:  # pylint: disable=broad-except
            if settings.IS_RUNNING_TESTS:
                raise
            logger.exception(
                "Could not generate cashflows for a business unit",
                extra={"business_unit": business_unit_id, "batch": batch_id},
            )

    return batch_id


def generate_payment_files(batch_id: int):
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


def _write_csv(
    filename: str,
    header: typing.Iterable,
    rows: typing.Iterable = None,
    batched_rows: typing.Iterable = None,
    row_formatter: typing.Callable[typing.Any, typing.Iterable] = lambda row: row,
    compress: bool = False,
) -> pathlib.Path:
    assert (rows is not None) ^ (batched_rows is not None)

    # Store file in a dedicated directory within "/tmp". It's easier
    # to clean files in tests that way.
    path = pathlib.Path(tempfile.mkdtemp()) / f"{filename}.csv"
    with open(path, "w+") as fp:
        writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(header)
        if rows is not None:
            writer.writerows(row_formatter(row) for row in rows)
        if batched_rows is not None:
            for rows_ in batched_rows:
                writer.writerows(row_formatter(row) for row in rows_)
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
        .join(
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
            BankInformation.iban.label("iban"),
            BankInformation.bic.label("bic"),
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
    # 2022-01-13 remove potential trailing space, new line and doublequote for BU, venue and offer name
    if not isinstance(value, str):
        return value
    return value.strip().replace('"', "")


def _generate_payments_file(batch_id: int) -> pathlib.Path:
    header = [
        "Identifiant de la BU",
        "SIRET de la BU",
        "Libellé de la BU",  # actually, the commercial name of the related venue
        "Identifiant du lieu",
        "Libellé du lieu",
        "Identifiant de l'offre",
        "Nom de l'offre",
        "Sous-catégorie de l'offre",
        "Prix de la réservation",
        "Type de réservation",
        "Date de validation",
        "Identifiant de la valorisation",
        "Taux de remboursement",
        "Montant remboursé à l'offreur",
    ]
    # We join `Venue` twice: once to get the venue that is related to
    # the business unit ; and once to get the venue of the offer. To
    # distinguish them in `with_entities()`, we need aliases.
    BusinessUnitVenue = sqla_orm.aliased(offerers_models.Venue)
    OfferVenue = sqla_orm.aliased(offerers_models.Venue)
    query = (
        models.Pricing.query.filter_by(status=models.PricingStatus.PROCESSED)
        .join(models.Pricing.cashflows)
        .join(models.Pricing.booking)
        .filter(bookings_models.Booking.amount != 0)
        .join(models.Pricing.businessUnit)
        .join(
            BusinessUnitVenue,
            models.BusinessUnit.siret == BusinessUnitVenue.siret,
        )
        .join(bookings_models.Booking.stock)
        .join(offers_models.Stock.offer)
        .join(offers_models.Offer.venue.of_type(OfferVenue))
        .join(bookings_models.Booking.offerer)
        .outerjoin(bookings_models.Booking.individualBooking)
        .outerjoin(bookings_models.IndividualBooking.deposit)
        .filter(models.Cashflow.batchId == batch_id)
        .distinct(models.Pricing.id)
        .order_by(models.Pricing.id)
        .with_entities(
            BusinessUnitVenue.id.label("business_unit_venue_id"),
            models.BusinessUnit.siret.label("business_unit_siret"),
            sqla_func.coalesce(
                BusinessUnitVenue.publicName,
                BusinessUnitVenue.name,
            ).label("business_unit_venue_name"),
            OfferVenue.id.label("offer_venue_id"),
            OfferVenue.name.label("offer_venue_name"),
            offers_models.Offer.id.label("offer_id"),
            offers_models.Offer.name.label("offer_name"),
            offers_models.Offer.subcategoryId.label("offer_subcategory_id"),
            bookings_models.Booking.amount.label("booking_amount"),
            bookings_models.Booking.quantity.label("booking_quantity"),
            bookings_models.Booking.educationalBookingId.label("educational_booking_id"),
            bookings_models.Booking.individualBookingId.label("individual_booking_id"),
            bookings_models.Booking.dateUsed.label("booking_used_date"),
            payments_models.Deposit.type.label("deposit_type"),
            models.Pricing.id.label("pricing_id"),
            models.Pricing.amount.label("pricing_amount"),
        )
        # FIXME (dbaty, 2021-11-30): other functions use `yield_per()`
        # but I am not sure it helps here. We have used
        # `pcapi.utils.db.get_batches` in the old-style payment code
        # and that may be what's best here.
        .yield_per(1000)
    )
    return _write_csv(
        "payment_details",
        header,
        rows=query,
        row_formatter=_payment_details_row_formatter,
        compress=True,  # it's a large CSV file (> 100 Mb), we should compress it
    )


def _payment_details_row_formatter(sql_row):
    if sql_row.educational_booking_id is not None:
        booking_type = "EACC"
    elif sql_row.deposit_type == payments_models.DepositType.GRANT_15_17:
        booking_type = "EACI"
    elif sql_row.deposit_type == payments_models.DepositType.GRANT_18:
        booking_type = "PC"
    else:
        raise ValueError("Unknown booking type (not educational nor individual)")

    booking_total_amount = sql_row.booking_amount * sql_row.booking_quantity
    reimbursed_amount = utils.to_euros(-sql_row.pricing_amount)
    reimbursement_rate = (reimbursed_amount / booking_total_amount).quantize(decimal.Decimal("0.01"))
    return (
        human_ids.humanize(sql_row.business_unit_venue_id),
        _clean_for_accounting(sql_row.business_unit_siret),
        _clean_for_accounting(sql_row.business_unit_venue_name),
        human_ids.humanize(sql_row.offer_venue_id),
        _clean_for_accounting(sql_row.offer_venue_name),
        sql_row.offer_id,
        _clean_for_accounting(sql_row.offer_name),
        sql_row.offer_subcategory_id,
        booking_total_amount,
        booking_type,
        sql_row.booking_used_date,
        sql_row.pricing_id,
        reimbursement_rate,
        reimbursed_amount,
    )


def _generate_wallets_file() -> pathlib.Path:
    # FIXME (dbaty, 2021-12-01): once the old system is removed, inline
    # `get_all_users_wallet_balances()` into this function.
    header = ["ID de l'utilisateur", "Solde théorique", "Solde réel"]
    query = user_queries.get_all_users_wallet_balances()
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

    business_unit.siret = siret
    db.session.add(business_unit)
    db.session.commit()


def find_reimbursement_rule(rule_reference: [str, int]) -> payments_models.ReimbursementRule:
    # regular rule description
    if isinstance(rule_reference, str):
        for regular_rule in reimbursement.REGULAR_RULES:
            if rule_reference == regular_rule.description:
                return regular_rule
    # CustomReimbursementRule.id
    return payments_models.CustomReimbursementRule.query.get(rule_reference)


def _make_invoice_line(group: conf.RuleGroups, pricings: list, line_rate: decimal.Decimal = None):
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
    # A rate is calculated for this line if we are using a CustomRule with an amount instead of a rate
    rate = line_rate or (decimal.Decimal(reimbursed_amount) / decimal.Decimal(offerer_revenue)).quantize(
        decimal.Decimal("0.0001")
    )
    invoice_line = models.InvoiceLine(
        label="Montant remboursé",
        group=group.value,
        contributionAmount=contribution_amount,
        reimbursedAmount=reimbursed_amount,
        rate=rate,
    )
    return invoice_line, reimbursed_amount


def generate_invoices():
    """Generate (and store) all invoices."""
    rows = (
        db.session.query(
            models.Cashflow.businessUnitId.label("business_unit_id"),
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
        .group_by(models.Cashflow.businessUnitId)
    )

    for row in rows:
        try:
            with transaction():
                generate_and_store_invoice(row.business_unit_id, row.cashflow_ids)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                "Could not generate invoice",
                extra={
                    "business_unit": row.business_unit_id,
                    "cashflow_ids": row.cashflow_ids,
                    "exc": str(exc),
                },
            )
    generate_invoice_file()


def generate_invoice_file(invoice_date: datetime.date = datetime.date.today()) -> pathlib.Path:
    header = [
        "Identifiant de la BU",
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
            BusinessUnitVenue.id.label("business_unit_venue_id"),
            models.Pricing.id.label("pricing_id"),
            models.PricingLine.id.label("pricing_line_id"),
            models.PricingLine.category.label("pricing_line_category"),
            models.PricingLine.amount.label("pricing_line_amount"),
        )
        .join(models.Invoice.cashflows)
        .join(models.Cashflow.pricings)
        .join(models.Pricing.lines)
        .join(models.Invoice.businessUnit)
        .join(
            BusinessUnitVenue,
            models.BusinessUnit.siret == BusinessUnitVenue.siret,
        )
        .filter(cast(models.Invoice.date, Date) == invoice_date)
        .order_by(models.Invoice.id, models.Pricing.id, models.PricingLine.id)
    )

    row_formatter = lambda row: (
        human_ids.humanize(row.business_unit_venue_id),
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


def generate_and_store_invoice(business_unit_id: int, cashflow_ids: list[int]):
    invoice = _generate_invoice(business_unit_id=business_unit_id, cashflow_ids=cashflow_ids)
    invoice_html = _generate_invoice_html(invoice=invoice)
    _store_invoice_pdf(invoice_storage_id=invoice.storage_object_id, invoice_html=invoice_html)
    send_invoice_available_to_pro_email(invoice)


def _generate_invoice(business_unit_id: int, cashflow_ids: list[int]):
    invoice = models.Invoice(businessUnitId=business_unit_id)
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
            pricings_and_rates_by_rule_group[rule.group].append((pricing, rule.rate))

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
    # Booking.status: USED -> REIMBURSED
    db.session.execute(
        """
        UPDATE booking
        SET
          status = :status,
          "reimbursementDate" = :reimbursement_date
        FROM pricing, cashflow_pricing
        WHERE
          booking.id = pricing."bookingId"
          AND pricing.id = cashflow_pricing."pricingId"
          AND cashflow_pricing."cashflowId" IN :cashflow_ids
        """,
        {
            "status": bookings_models.BookingStatus.REIMBURSED.value,
            "cashflow_ids": tuple(cashflow_ids),
            "reimbursement_date": datetime.datetime.utcnow(),
        },
    )
    db.session.commit()
    return invoice


def _prepare_invoice_context(invoice: models.Invoice) -> dict:
    invoice_lines = sorted(invoice.lines, key=lambda k: (k.group["position"], -k.rate))
    total_used_bookings_amount = 0
    total_contribution_amount = 0
    total_reimbursed_amount = 0
    invoice_groups = dict()
    for group, lines in itertools.groupby(invoice_lines, attrgetter("group")):
        invoice_groups[group["label"]] = (group, list(lines))

    groups = []
    for _group_label, group_and_lines in invoice_groups.items():
        group = group_and_lines[0]
        lines = group_and_lines[1]
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
            lines=lines,
        )
        groups.append(invoice_group)

    venue = offerers_repository.find_venue_by_siret(invoice.businessUnit.siret)
    return dict(
        invoice=invoice,
        groups=groups,
        venue=venue,
        total_used_bookings_amount=total_used_bookings_amount,
        total_contribution_amount=total_contribution_amount,
        total_reimbursed_amount=total_reimbursed_amount,
    )


def _generate_invoice_html(invoice: models.Invoice) -> str:
    context = _prepare_invoice_context(invoice)
    return render_template("invoices/invoice.html", **context)


def _store_invoice_pdf(invoice_storage_id: str, invoice_html: str):
    invoice_pdf = pdf_utils.generate_pdf_from_html(html_content=invoice_html)
    store_public_object(
        folder="invoices", object_id=invoice_storage_id, blob=invoice_pdf, content_type="application/pdf"
    )


def merge_cashflow_batches(
    batches_to_remove: list[models.CashflowBatch],
    target_batch: models.CashflowBatch,
):
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
