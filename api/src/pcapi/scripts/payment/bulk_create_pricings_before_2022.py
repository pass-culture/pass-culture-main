"""This script exports Pricing objects (as CSV files) for the venues
in a file, for all bookings that have been used in 2021.

Usage:

   $ python bulk_create_pricings_before_2022_v2.py <path>

... where `<path>` is a file that contains one venue id per line.

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
import pcapi.domain.reimbursement
from pcapi.models import db


DATE_USED_SWITCH_DATE = datetime.datetime(2021, 8, 31)
TZ = pytz.timezone("Europe/Paris")


def log(msg, venue_id):
    timestamp = datetime.datetime.utcnow().astimezone(TZ)
    timestamp = timestamp.strftime("%H:%M:%S")
    print(f"{timestamp}:{venue_id}:{msg}")


def export_pricings(
    venue_id: int,
    min_date: datetime.datetime,
    max_date: datetime.datetime,
) -> finance_models.Pricing:
    venue = offerers_models.Venue.query.get(venue_id)
    if not venue:
        log("Venue not found.", venue_id)
        return
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
        LEFT OUTER JOIN payment on payment."bookingId" = booking.id
        LEFT OUTER JOIN payment_status on payment_status."paymentId" = payment.id
        LEFT OUTER JOIN pricing on pricing."bookingId" = booking.id
        WHERE
            booking."venueId" = :venue_id
            AND booking."dateUsed" >= :min_date
            AND booking."dateUsed" < :max_date
            AND pricing.id IS NULL
        GROUP BY (payment.id, booking.id)
        ORDER BY booking."dateCreated"
    """
    params = {
        "venue_id": venue_id,
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
            amount_in_euros = row.payment_amount
            standard_rule = row.payment_standard_rule
            custom_rule_id = row.payment_custom_rule_id
            if "SENT" in row.payment_statuses:
                # Set as processed, to AVOID including this pricing
                # the next time we generate cashflows.
                status = finance_models.PricingStatus.PROCESSED
            elif row.booking_status == "USED":
                # Set as validated, so that this pricing WILL be
                # included the next time we generate cashflow.
                status = finance_models.PricingStatus.VALIDATED
            else:
                # We tried a payment for a booking that was "used",
                # the payment did not succeed, and the booking was
                # then cancelled.
                continue
        elif row.booking_status != "USED":
            # Check status after testing whether there is a payment.
            # Because if there is a payment, there must be a pricing,
            # even if the booking has been cancelled afterwards.
            continue
        elif row.booking_total_amount == 0:
            amount_in_euros = 0
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
            if pcapi.domain.reimbursement.DigitalThingsReimbursement.is_relevant(None, booking, revenues[revenue_key]):
                amount_in_euros = 0
                standard_rule = "Pas de remboursement pour les offres digitales"
                custom_rule_id = None
                status = finance_models.PricingStatus.PROCESSED
            elif booking.stock.beginningDatetime and booking.stock.beginningDatetime > booking.dateUsed:
                # Some bookings are marked as used before the event
                # date. This is not the norm but happens. We should
                # create a validated pricing now. A cashflow will be
                # generated after the event date.
                status = finance_models.PricingStatus.VALIDATED
                rule = pcapi.domain.reimbursement.get_reimbursement_rule(
                    booking, rule_finder, finance_utils.to_euros(revenues[revenue_key])
                )
                if isinstance(rule, finance_models.CustomReimbursementRule):
                    standard_rule = ""
                    custom_rule_id = rule.id
                else:
                    standard_rule = rule.description
                    custom_rule_id = None
                amount_in_euros = rule.apply(booking)
            else:
                # FIXME: Gotcha! It's possible that an old rule has
                # been applied, e.g. MaxReimbursementByOfferer. It's
                # hard to detect automatically.
                log(f"Found no Payment for possibly reimbursable booking {row.booking_id}", venue_id)
                continue

        signed_amount_in_cents = -finance_utils.to_eurocents(amount_in_euros)
        # Build a CSV that can be injected with the following command:
        #
        #  \copy pricing (
        #      status, "bookingId", "venueId", "pricingPointId", "creationDate", "valueDate", amount,
        #    "standardRule", "customRuleId", revenue
        #  )
        #  FROM 'xxx.csv' WITH DELIMITER ';' NULL '[NULL]'
        csv_rows.append(
            (
                # Values below will be inserted INTO `pricing`.
                status.value,  # status
                str(row.booking_id),  # bookingId
                str(venue_id),  # venueId
                str(venue_id),  # venueId
                creation_date.isoformat(),
                value_date.isoformat(),
                str(signed_amount_in_cents),
                standard_rule or "",
                str(custom_rule_id) if custom_rule_id else "[NULL]",
                str(revenues[revenue_key]),
            )
        )

    if csv_rows:
        path = f"/tmp/pricings_2021/{venue_id}.csv"
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
    elapsed_per_venue = []
    for current, line in enumerate(lines, 1):
        venue_id = int(line)
        start_time = time.perf_counter()

        # Year 2021 (UTC)
        min_date = datetime.datetime(2020, 12, 31, 23, 0)  # included
        max_date = datetime.datetime(2021, 12, 31, 23, 0)  # excluded
        export_pricings(venue_id, min_date, max_date)

        elapsed_per_venue.append(int(time.perf_counter() - start_time))
        eta = _get_eta(len(lines), current, elapsed_per_venue)
        timestamp = datetime.datetime.utcnow().astimezone(pytz.timezone("Europe/Paris"))
        timestamp = timestamp.isoformat().split(".")[0]
        if current % 100 == 0:
            print(f"{timestamp}:{venue_id}:ETA={eta}")
