"""This script exports Pricing objects (as CSV files) for the business
units listed in a file (if the business unit is validated and has
validated bank information) for all bookings that have been used in
2021.

Usage:

   $ python bulk_create_pricings_before_2022.py <path>

... where `<path>` is a file that contains one business unit id per
line.
"""
from pcapi.flask_app import app; app.app_context().push()  # fmt: skip

import collections
import datetime
import pathlib
import statistics
import sys
import time

import pytz
import sqlalchemy.orm as sqla_orm

import pcapi.core.bookings.models as bookings_models
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.utils as finance_utils
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.models as offers_models
import pcapi.core.payments.models as payments_models
import pcapi.domain.reimbursement
from pcapi.models import db


DATE_USED_SWITCH_DATE = datetime.datetime(2021, 8, 31)
TZ = pytz.timezone("Europe/Paris")


def log(msg, business_unit_id):
    timestamp = datetime.datetime.utcnow().astimezone(TZ)
    timestamp = timestamp.strftime("%H:%M:%S")
    print(f"{timestamp}:{business_unit_id}:{msg}")


def export_pricings(
    business_unit_id: int,
    min_date: datetime.datetime,
    max_date: datetime.datetime,
) -> finance_models.Pricing:
    business_unit = (
        finance_models.BusinessUnit.query.filter(
            finance_models.BusinessUnit.id == business_unit_id,
            finance_models.BusinessUnit.status == finance_models.BusinessUnitStatus.ACTIVE,
        )
    ).first()
    if not business_unit:
        log("Business unit not active or without bank info.", business_unit_id)
        return
    venues = offerers_models.Venue.query.filter_by(businessUnitId=business_unit_id).all()
    sirets = {venue.id: venue.siret for venue in venues}
    venue_ids = [venue.id for venue in venues]
    rule_finder = pcapi.domain.reimbursement.CustomRuleFinder()

    csv_rows = []

    sql = """
        SELECT
            booking.id as booking_id,
            booking.status as booking_status,
            booking.amount * booking.quantity as booking_total_amount,
            booking."dateUsed" as booking_use_date,
            booking."dateCreated" as booking_creation_date,
            booking."venueId" as venue_id,
            payment.id as payment_id,
            payment.amount as payment_amount,
            payment."reimbursementRule" as payment_standard_rule,
            payment."customReimbursementRuleId" as payment_custom_rule_id,
            array_remove(array_agg(payment_status.date), NULL) as payment_dates,
            array_remove(array_agg(payment_status.status), NULL) as payment_statuses
        FROM booking
        JOIN stock ON stock.id = booking."stockId"
        LEFT OUTER JOIN payment on payment."bookingId" = booking.id
        LEFT OUTER JOIN payment_status on payment_status."paymentId" = payment.id
        LEFT OUTER JOIN pricing on pricing."bookingId" = booking.id
        WHERE
            booking."venueId" IN :venue_ids
            AND booking."dateUsed" >= :min_date
            AND booking."dateUsed" < :max_date
            AND pricing.id IS NULL
        GROUP BY (payment.id, booking.id)
        ORDER BY booking."dateCreated"
    """
    params = {
        "venue_ids": tuple(venue_ids),
        "min_date": min_date,
        "max_date": max_date,
    }
    result = db.session.execute(sql, params)
    rows = result.fetchall()

    revenues = collections.defaultdict(lambda: 0)
    for row in rows:
        if row.payment_dates:
            first_payment_date = min(row.payment_dates)
            creation_date = first_payment_date
            if first_payment_date > DATE_USED_SWITCH_DATE:
                value_date = row.booking_use_date
            else:  # either before DATE_USED_SWITCH_DATE, or free booking
                value_date = row.booking_creation_date
        else:
            creation_date = datetime.datetime.utcnow()
            value_date = row.booking_use_date
        revenue_key = (row.venue_id, value_date.year)
        revenues[revenue_key] += finance_utils.to_eurocents(row.booking_total_amount)

        if row.payment_id:
            amount = row.payment_amount
            standard_rule = row.payment_standard_rule
            custom_rule_id = row.payment_custom_rule_id
            if "SENT" in row.payment_statuses:
                # Set as processed, we'll create a manual cashflow later.
                status = finance_models.PricingStatus.PROCESSED
            else:
                # Set as validated, a cashflow will be automatically created later.
                status = finance_models.PricingStatus.VALIDATED
        elif row.booking_status != "USED":
            # Check status after testing whether there is a payment.
            # Because if there is a payment, there must be a pricing,
            # even if the booking has been cancelled afterwards.
            continue
        elif row.booking_total_amount == 0:
            amount = 0
            standard_rule = "Offre gratuite"
            custom_rule_id = None
            status = finance_models.PricingStatus.PROCESSED
        else:
            # This is a non-free booking with no payment. It's
            # possible that the booking was not reimbursable. Or it
            # has not been reimbursed because we did not have banking
            # information.
            booking = bookings_models.Booking.query.options(
                sqla_orm.joinedload(bookings_models.Booking.stock, innerjoin=True).joinedload(
                    offers_models.Stock.offer, innerjoin=True
                )
            ).get(row.booking_id)
            if pcapi.domain.reimbursement.DigitalThingsReimbursement.is_relevant(None, booking):
                amount = 0
                standard_rule = "Pas de remboursement pour les offres digitales"
                custom_rule_id = None
                status = finance_models.PricingStatus.PROCESSED
            elif booking.stock.beginningDatetime and booking.stock.beginningDatetime > booking.dateUsed:
                # Some bookings have been marked as used before the
                # event date. This is rare but happens. We should
                # create a validated pricing now. A cashflow will be
                # generated after the event date.
                status = finance_models.PricingStatus.VALIDATED
                rule = pcapi.domain.reimbursement.get_reimbursement_rule(
                    booking, rule_finder, finance_utils.to_euros(revenues[revenue_key])
                )
                if isinstance(rule, payments_models.CustomReimbursementRule):
                    standard_rule = ""
                    custom_rule_id = rule.id
                else:
                    standard_rule = rule.description
                    custom_rule_id = None
                amount = rule.apply(booking)
            else:
                # FIXME: Gotcha! It's possible that an old rule has
                # been applied, e.g. MaxReimbursementByOfferer. It's
                # hard to detect automatically.
                log(f"Found no Payment for possibly reimbursable booking {row.booking_id}", business_unit_id)
                continue

        csv_rows.append(
            (
                # Values below are for information only.
                str(business_unit_id),
                str(row.venue_id),
                # Values below will be inserted INTO `pricing`.
                status.value,
                str(row.booking_id),
                str(business_unit_id),
                str(sirets.get(row.venue_id, business_unit.siret)),
                creation_date.isoformat(),
                value_date.isoformat(),
                str(-finance_utils.to_eurocents(amount)),
                standard_rule or "",
                str(custom_rule_id) if custom_rule_id else "[NULL]",
                str(revenues[revenue_key]),
            )
        )

    if csv_rows:
        path = f"/tmp/pricings_2021/{business_unit_id}.csv"
        with open(path, "w") as fp:
            fp.write("\n".join(";".join(csv_row) for csv_row in csv_rows))

    # FIXME: All pricing lines can be added in two SQL queries:
    #
    #   INSERT INTO pricing_line ("pricingId", amount, category)
    #     SELECT pricing.id, -100 * booking.amount * booking.quantity, 'offerer revenue'
    #     FROM pricing
    #     JOIN booking ON booking.id = pricing."bookingId"
    #     WHERE "valueDate" < '2021-12-31 23:00'
    #
    # and:
    #   INSERT INTO pricing_line ("pricingId", amount, category)
    #     SELECT pricing.id, pricing.amount + 100 * booking.amount * booking.quantity, 'offerer contribution'
    #     FROM pricing
    #     JOIN booking ON booking.id = pricing."bookingId"
    #     WHERE "valueDate" < '2021-12-31 23:00'
    #
    # Beware: UNTESTED CODE (but that's the idea).


def _get_eta(end, current, elapsed_per_batch):
    left_to_do = end - current
    eta = left_to_do * statistics.mean(elapsed_per_batch)
    eta = datetime.datetime.now() + datetime.timedelta(seconds=eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    eta = eta.strftime("%d/%m/%Y %H:%M:%S")
    return eta


if __name__ == "__main__":
    path_with_ids = pathlib.Path(sys.argv[1])
    lines = path_with_ids.read_text().split()
    elapsed_per_business_unit = []
    for current, line in enumerate(lines, 1):
        business_unit_id = int(line)
        start_time = time.perf_counter()

        # Year 2021 (UTC)
        min_date = datetime.datetime(2020, 12, 31, 23, 0)
        max_date = datetime.datetime(2021, 12, 31, 23, 0)
        export_pricings(business_unit_id, min_date, max_date)

        elapsed_per_business_unit.append(int(time.perf_counter() - start_time))
        eta = _get_eta(len(lines), current, elapsed_per_business_unit)
        timestamp = datetime.datetime.utcnow().astimezone(pytz.timezone("Europe/Paris"))
        timestamp = timestamp.isoformat().split(".")[0]
        if current % 100 == 0:
            print(f"{timestamp}:{business_unit_id}:ETA={eta}")
