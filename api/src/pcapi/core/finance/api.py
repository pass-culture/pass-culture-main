import csv
import datetime
import decimal
import logging
import pathlib
import tempfile
import typing
import zipfile

import pytz
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm
import sqlalchemy.sql.functions as sqla_func

from pcapi import settings
import pcapi.core.bookings.models as bookings_models
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.payments.models as payments_models
import pcapi.core.payments.utils as payments_utils
from pcapi.domain import reimbursement
from pcapi.models import db
from pcapi.models.bank_information import BankInformation
from pcapi.models.bank_information import BankInformationStatus
from pcapi.repository import transaction
from pcapi.repository import user_queries
from pcapi.utils import human_ids

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
    # The upper bound on `dateUsed` avoids selecting a very recent booking
    # that may have been COMMITed to the database just before another
    # booking with a slightly older `dateUsed`.
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
        .join(models.BusinessUnit.bankAccount)
        .filter(BankInformation.status == BankInformationStatus.ACCEPTED)
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
                sqla_orm.joinedload(bookings_models.Booking.venue, innerjoin=True)
                .joinedload(offerers_models.Venue.businessUnit, innerjoin=True)
                .joinedload(models.BusinessUnit.bankAccount, innerjoin=True),
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

        business_unit = booking.venue.businessUnit
        # FIXME (dbaty, 2021-12-08): we can get rid of this condition
        # once BusinessUnit.siret is set as NOT NULLable.
        if not business_unit.siret:
            return None
        if business_unit.status != models.BusinessUnitStatus.ACTIVE:
            return None
        if business_unit.bankAccount.status != BankInformationStatus.ACCEPTED:
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
    latest_pricing = (
        models.Pricing.query.filter_by(siret=siret)
        .filter(models.Pricing.valueDate.between(*revenue_period))
        .order_by(models.Pricing.valueDate.desc())
        .first()
    )
    current_revenue = latest_pricing.revenue if latest_pricing else 0
    return siret, current_revenue


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
    siret = booking.venue.siret or booking.venue.businessUnit.siret
    query = models.Pricing.query.filter(
        models.Pricing.siret == siret,
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
    pricings = models.Pricing.query.filter(models.Pricing.id.in_(pricing_ids))
    pricings.delete(synchronize_session=False)
    logger.info(
        log_message,
        extra={
            "booking_being_priced": booking.id,
            "booking_already_priced": [p.bookingId for p in pricings],
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
    batch = models.CashflowBatch(cutoff=cutoff)
    db.session.add(batch)
    db.session.flush()
    batch_id = batch.id  # access _before_ COMMIT to avoid extra SELECT
    db.session.commit()

    filters = (
        models.Pricing.status == models.PricingStatus.VALIDATED,
        models.Pricing.valueDate < cutoff,
        models.CashflowPricing.pricingId.is_(None),
    )

    business_unit_ids_and_bank_account_ids = (
        models.Pricing.query.filter(
            models.BusinessUnit.bankAccountId.isnot(None),
            *filters,
        )
        .join(models.Pricing.businessUnit)
        .outerjoin(models.CashflowPricing)
        .with_entities(models.Pricing.businessUnitId, models.BusinessUnit.bankAccountId)
        .distinct()
    )
    for business_unit_id, bank_account_id in business_unit_ids_and_bank_account_ids:
        try:
            with transaction():
                pricings = models.Pricing.query.outerjoin(models.CashflowPricing).filter(
                    models.Pricing.businessUnitId == business_unit_id,
                    *filters,
                )
                total = pricings.with_entities(sqla.func.sum(models.Pricing.amount)).scalar()
                # FIXME: do we want to update Pricing.status? `CASHFLOWED`?!
                if not total:
                    continue
                cashflow = models.Cashflow(
                    batchId=batch_id,
                    bankAccountId=bank_account_id,
                    status=models.CashflowStatus.PENDING,
                    amount=total,
                )
                db.session.add(cashflow)
                links = [models.CashflowPricing(cashflowId=cashflow.id, pricingId=pricing.id) for pricing in pricings]
                db.session.bulk_save_objects(links)
                db.session.commit()
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
    file_paths["business_units"] = _generate_business_units_file()
    file_paths["payments"] = _generate_payments_file(batch_id)
    file_paths["wallets"] = _generate_wallets_file()
    logger.info(
        "Finance files have been generated",
        extra={"paths": [str(path) for path in file_paths.values()]},
    )

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
        with zipfile.ZipFile(compressed_path, "w") as zfile:
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
        row.business_unit_siret,
        row.business_unit_name,
        row.venue_name,
        row.iban,
        row.bic,
    )
    return _write_csv("business_units", header, rows=query, row_formatter=row_formatter)


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
        models.Pricing.query.filter_by(status=models.PricingStatus.VALIDATED)
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
    elif sql_row.individual_booking_id is not None:
        booking_type = "PC"
    else:
        raise ValueError("Unknown booking type (not educational nor individual)")

    booking_total_amount = sql_row.booking_amount * sql_row.booking_quantity
    reimbursed_amount = utils.to_euros(-sql_row.pricing_amount)
    reimbursement_rate = (reimbursed_amount / booking_total_amount).quantize(decimal.Decimal("0.01"))
    return (
        human_ids.humanize(sql_row.business_unit_venue_id),
        sql_row.business_unit_siret,
        sql_row.business_unit_venue_name,
        human_ids.humanize(sql_row.offer_venue_id),
        sql_row.offer_venue_name,
        sql_row.offer_id,
        sql_row.offer_name,
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
    return _write_csv("soldes_des_utilisateurs", header, rows=query, row_formatter=row_formatter)


def edit_business_unit(business_unit: models.BusinessUnit, siret: str) -> None:
    if business_unit.siret:
        raise ValueError("Cannot edit a business unit that already has a SIRET.")

    validation.check_business_unit_siret(business_unit, siret)

    business_unit.siret = siret
    db.session.add(business_unit)
    db.session.commit()
