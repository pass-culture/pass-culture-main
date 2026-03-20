"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=add_educational_year \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import datetime
import logging

import pytz

from pcapi.app import app
from pcapi.core.educational import models
from pcapi.core.educational.adage.backends.adage import AdageHttpClient
from pcapi.models import db
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)

START_YEAR = 2026


def main() -> None:
    years_in_db = db.session.query(models.EducationalYear).filter(
        models.EducationalYear.beginningDate > datetime.datetime.fromisoformat(f"{START_YEAR}-08-30"),
        models.EducationalYear.beginningDate < datetime.datetime.fromisoformat(f"{START_YEAR}-09-02"),
    )
    if years_in_db.count() > 0:
        raise ValueError(f"There is already an educational year in db with start year {START_YEAR}")

    adage_client = AdageHttpClient()
    api_url = f"{adage_client.base_url}/v1/annees-scolaires"
    response = adage_client._make_get_request(url=api_url)
    years = response.json()

    for adage_year in years:
        # we receive datetimes in ISO format without time zone
        # but they represent METROPOLE_TIMEZONE local datetimes
        start = pytz.timezone(date_utils.METROPOLE_TIMEZONE).localize(
            datetime.datetime.fromisoformat(adage_year["debut"])
        )

        if start.year == START_YEAR:
            logger.info("Found educational year in adage: %s", adage_year)

            end = pytz.timezone(date_utils.METROPOLE_TIMEZONE).localize(
                datetime.datetime.fromisoformat(adage_year["fin"])
            )
            adage_id = adage_year["id"]

            logger.info(
                "Adding EducationalYear with adageId %s, start %s, end %s", adage_id, start.isoformat(), end.isoformat()
            )
            educational_year = models.EducationalYear(beginningDate=start, expirationDate=end, adageId=adage_id)
            db.session.add(educational_year)
            db.session.flush()
            break


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main()

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
