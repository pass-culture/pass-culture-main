"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-37593-api-pricer-les-finance-events-quand-le-pp-a-ete-ajoute-via-script/api/src/pcapi/scripts/fix_pending_finance_events/main.py

"""

import argparse
import csv
import logging
import os
import traceback
from collections.abc import Iterable
from datetime import datetime

import sqlalchemy as sa

import pcapi.core.educational.models as educational_models
import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.models as offerer_models
from pcapi.app import app
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import is_managed_transaction
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def read_csv_file(filename: str) -> Iterable[dict[str, str]]:
    namespace_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "flask",
        os.path.dirname(__file__).split("/")[-1],
    )
    try:
        with open(f"{namespace_dir}/{filename}", "r", encoding="utf-8") as csv_file:
            csv_rows = csv.DictReader(csv_file, delimiter=";")
            for row in csv_rows:
                yield row
    except FileNotFoundError:
        namespace_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            os.path.dirname(__file__).split("/")[-1],
        )
        with open(f"{namespace_dir}/{filename}", "r", encoding="utf-8") as csv_file:
            csv_rows = csv.DictReader(csv_file, delimiter=";")
            yield from csv_rows


@atomic()
def link_venue_to_pricing_point(
    venue: offerer_models.Venue,
) -> None:
    """
    Cloned from core.offerers.api.link_venue_to_pricing_point
    """
    current_link = (
        db.session.query(offerer_models.VenuePricingPointLink)
        .filter(
            offerer_models.VenuePricingPointLink.venueId == venue.id,
            offerer_models.VenuePricingPointLink.timespan.contains(datetime.utcnow()),
        )
        .one()
    )

    for from_tables, where_clauses, stock_datetime in (
        (
            "booking, stock",
            'finance_event."bookingId" is not null '
            'and booking.id = finance_event."bookingId" '
            'and stock.id = booking."stockId"',
            "beginningDatetime",
        ),
        (
            # use aliases to have the same `set` clause
            "collective_booking as booking, collective_stock as stock",
            'finance_event."collectiveBookingId" is not null '
            'and booking.id = finance_event."collectiveBookingId" '
            'and stock.id = booking."collectiveStockId"',
            educational_models.CollectiveStock.endDatetime.name,
        ),
    ):
        ppoint_update_result = db.session.execute(
            sa.text(
                f"""
              update finance_event
              set
                "pricingPointId" = :pricing_point_id,
                status = :finance_event_status_ready,
                "pricingOrderingDate" = greatest(
                  booking."dateUsed",
                  stock."{stock_datetime}",
                  :new_link_start
                )
              from {from_tables}
              where
                {where_clauses}
                and finance_event.status = :finance_event_status_pending
                and finance_event."pricingPointId" IS NULL
                and finance_event."venueId" = :venue_id
            """
            ),
            {
                "venue_id": venue.id,
                "pricing_point_id": current_link.pricingPointId,
                "finance_event_status_pending": finance_models.FinanceEventStatus.PENDING.value,
                "finance_event_status_ready": finance_models.FinanceEventStatus.READY.value,
                "new_link_start": datetime.utcnow(),
            },
        )
    if is_managed_transaction():
        db.session.flush()
    else:
        db.session.commit()

    logger.info(
        "Linked venue to pricing point",
        extra={
            "venue": venue.id,
            "new_pricing_point": current_link.pricingPointId,
            "previous_pricing_point": None,
            "updated_finance_events": ppoint_update_result.rowcount,
        },
    )


@atomic()
def main(dry_run: bool, venue_ids: list[int]) -> None:
    if dry_run:
        mark_transaction_as_invalid()
    for venue_id in venue_ids:
        try:
            venue = (
                db.session.query(offerer_models.Venue)
                .filter(offerer_models.Venue.id == venue_id)
                .execution_options(include_deleted=True)
                .one()
            )
            link_venue_to_pricing_point(venue)
            print(f"Processed venue {venue.id} - {venue.name}")
        except Exception:
            print(traceback.format_exc())


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    venue_ids = {int(row["venue_id"]) for row in read_csv_file("pricing_point.csv")}
    main(dry_run=not args.not_dry, venue_ids=venue_ids)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
