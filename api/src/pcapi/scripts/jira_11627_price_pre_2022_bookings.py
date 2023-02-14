# fmt: off
# isort: off
from pcapi.flask_app import app; app.app_context().push()

# --- 8-> ---
# Monkey-patch pricing code
class FakePricingPointLink:
    def __init__(self, pricing_point_id):
        self.pricingPointId = pricing_point_id


# Before 2022, the pricing point of a venue was the venue itself.
# Here we return a fake object that `_get_pricing_point_id_and_current_revenue()`
# can handle.
def custom_get_pricing_point_link(booking):
    return FakePricingPointLink(pricing_point_id=booking.venueId)


import pcapi.core.finance.api as finance_api

finance_api._get_pricing_point_link = custom_get_pricing_point_link
# End of monkey patch
# --- 8-> ---


# fmt: on
# isort: on

import datetime
import math
import pathlib
import sys
import time

import pytz
import sqlalchemy as sqla

import pcapi.core.bookings.models as bookings_models
import pcapi.core.finance.models as finance_models
import pcapi.core.finance.utils as finance_utils
import pcapi.core.offers.models as offers_models
from pcapi.models import db


BATCH_SIZE = 1_000
REPORT_EVERY = 300
CSV_OUT_PATH = pathlib.Path("/tmp/jira_11627_output_summary.csv")


def _get_eta(end, current, elapsed):
    left_to_do = end - current
    eta = left_to_do / current * elapsed
    eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=eta)
    eta = eta.astimezone(pytz.timezone("Europe/Paris"))
    eta = eta.strftime("%H:%M:%S")
    return eta


def get_bookings(venue_id, date_min_included, date_max_excluded):
    return (
        bookings_models.Booking.query.outerjoin(bookings_models.Booking.pricings)
        .filter(
            bookings_models.Booking.venueId == venue_id,
            bookings_models.Booking.status == bookings_models.BookingStatus.USED,
            bookings_models.Booking.dateUsed >= date_min_included,
            bookings_models.Booking.dateUsed < date_max_excluded,
            finance_models.Pricing.id.is_(None),
        )
        .order_by(bookings_models.Booking.dateUsed)
    )


def process_venue_bookings(year, venue_id):
    """Create all missing pricings and pricing lines for all bookings
    used during the requested year.

    Pricing status is set as PENDING so that we have a chance to
    review them before we generate cashflows.
    """
    date_min_included = datetime.datetime(year - 1, 12, 31, 23, 0)  # UTC
    date_max_excluded = datetime.datetime(year, 12, 31, 23, 0)  # UTC

    query = get_bookings(venue_id, date_min_included, date_max_excluded)
    n_bookings = query.count()
    print(f"Found {n_bookings} bookings")

    start = time.perf_counter()
    loops = math.ceil(n_bookings / BATCH_SIZE)
    last_booking_id = None
    done = 0
    while loops > 0:
        if last_booking_id:
            bookings = query.filter(bookings_models.Booking.id > last_booking_id)
        else:
            bookings = query
        bookings = bookings.join(bookings_models.Booking.stock).join(offers_models.Stock.offer)
        bookings = bookings.limit(BATCH_SIZE)
        for booking in bookings:
            pricing = finance_api._price_booking(booking)
            pricing.status = finance_models.PricingStatus.PENDING
            db.session.add(pricing)
            done += 1
            if done % REPORT_EVERY == 0:
                elapsed = time.perf_counter() - start
                eta = _get_eta(n_bookings, done, elapsed)
                print(f"{done} of {n_bookings} / ETA = {eta}")
        db.session.commit()
        db.session.expunge_all()
        loops -= 1

    year_pricings = finance_models.Pricing.query.filter(
        finance_models.Pricing.pricingPointId == venue_id,
        finance_models.Pricing.valueDate >= date_min_included,
        finance_models.Pricing.valueDate < date_max_excluded,
    )
    previous_total = -finance_utils.to_euros(
        year_pricings.filter(
            finance_models.Pricing.status != finance_models.PricingStatus.PENDING,
        ).with_entities(
            sqla.func.sum(finance_models.Pricing.amount)
        )[0][0]
        or 0
    )
    new_total = -finance_utils.to_euros(
        year_pricings.with_entities(sqla.func.sum(finance_models.Pricing.amount))[0][0] or 0
    )
    with CSV_OUT_PATH.open("a", encoding="utf-8") as fp:
        fp.write(f"{venue_id};{n_bookings};{previous_total};{new_total}\n")


def main():
    year, venue_id = int(sys.argv[1]), int(sys.argv[2])
    assert 2017 < year < 2022
    process_venue_bookings(year, venue_id)


if __name__ == "__main__":
    main()
