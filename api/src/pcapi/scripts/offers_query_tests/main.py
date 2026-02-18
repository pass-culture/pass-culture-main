"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=offers_query_tests \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import datetime
import logging
import os
import time

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm
from sqlalchemy.dialects import postgresql

from pcapi import settings
from pcapi.app import app
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.utils.date import get_naive_utc_now


logger = logging.getLogger(__name__)


# Event En instruction > Bien En instruction > Event Épuisé > Bien Épuisé > Event > bien actif
def _offer_score(offer: models.Offer) -> int:
    if offer.isEvent:
        if offer.validation == OfferValidationStatus.PENDING:
            return 6
        if offer.isSoldOut:
            return 4
        return 2
    else:
        if offer.validation == OfferValidationStatus.PENDING:
            return 5
        if offer.isSoldOut:
            return 3
        return 1


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--venue-id", type=int, action="append", required=True)
    args = parser.parse_args()

    venue_ids: list[int] = args.venue_id
    for venue_id in venue_ids:
        venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == venue_id).one_or_none()
        if venue is None:
            raise ValueError("Invalid venue id")

    number_of_days_options = (30, 60, 90)
    now = get_naive_utc_now()
    date_filter_options = tuple(now - datetime.timedelta(days=days) for days in number_of_days_options)

    results = []

    for venue_id in venue_ids:
        for date_filter, number_of_days in zip(date_filter_options, number_of_days_options):
            db.session.execute(sa.text("SET SESSION statement_timeout = '600s'"))  # 10 minutes

            offers_query = (
                db.session.query(models.Offer)
                .filter(
                    models.Offer.venueId == venue_id,
                    models.Offer.publicationDatetime >= date_filter,
                )
                # .order_by(models.Offer.publicationDatetime.desc())
                .options(sa_orm.joinedload(models.Offer.stocks))
                .limit(100)
            )

            offers_query_str = (
                str(
                    offers_query.statement.compile(compile_kwargs={"literal_binds": True}, dialect=postgresql.dialect())
                )
                + ";"
            )

            start = time.perf_counter()
            rows = db.session.execute(sa.text("EXPLAIN (analyze, buffers) " + offers_query_str)).fetchall()
            result = "\n".join((str(r) for r in rows))
            stop = time.perf_counter()

            results.append(
                {
                    "venue_id": venue_id,
                    "number_of_days": number_of_days,
                    "run_number": 1,
                    "time": f"{(stop - start):.6f}s",
                    "offers_count": "",
                    "query": offers_query_str,
                    "explain_analyze": result,
                }
            )

            # second run to see the effect of postgres buffer
            start = time.perf_counter()
            rows = db.session.execute(sa.text("EXPLAIN (analyze, buffers) " + offers_query_str)).fetchall()
            result = "\n".join((str(r) for r in rows))
            stop = time.perf_counter()

            count = offers_query.count()

            results.append(
                {
                    "venue_id": venue_id,
                    "number_of_days": number_of_days,
                    "run_number": 2,
                    "time": f"{(stop - start):.6f}s",
                    "offers_count": count,
                    "query": offers_query_str,
                    "explain_analyze": result,
                }
            )

            # sort timing
            offers = offers_query.all()
            start = time.perf_counter()
            offers = sorted(offers, key=_offer_score, reverse=True)
            stop = time.perf_counter()

            results.append(
                {
                    "venue_id": venue_id,
                    "number_of_days": number_of_days,
                    "run_number": "",
                    "time": f"{(stop - start):.6f}s",
                    "offers_count": count,
                    "query": "Python sort",
                    "explain_analyze": "",
                }
            )

            db.session.execute(sa.text(f"SET SESSION statement_timeout={settings.DATABASE_STATEMENT_TIMEOUT}"))

    with open(f"{os.environ.get('OUTPUT_DIRECTORY')}/result.csv", "w") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["venue_id", "number_of_days", "run_number", "time", "offers_count", "query", "explain_analyze"],
        )
        writer.writeheader()
        writer.writerows(results)
