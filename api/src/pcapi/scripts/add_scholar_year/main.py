import argparse
import datetime
import logging

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.adage_backends.adage import AdageHttpClient
from pcapi.models import db
from pcapi.utils import requests


logger = logging.getLogger(__name__)

app.app_context().push()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    years_in_db = educational_models.EducationalYear.query.filter(
        educational_models.EducationalYear.beginningDate > datetime.datetime.fromisoformat("2025-08-31"),
        educational_models.EducationalYear.beginningDate < datetime.datetime.fromisoformat("2025-09-02"),
    )
    if years_in_db.count() > 0:
        raise ValueError(
            f"There is already an educational year in db with start date {years_in_db.first().beginningDate}"
        )

    adage_client = AdageHttpClient()
    api_url = f"{adage_client.base_url}/v1/annees-scolaires"
    response = requests.get(
        api_url, headers={adage_client.header_key: adage_client.api_key, "Content-Type": "application/json"}
    )
    years = response.json()

    for adage_year in years:
        start = datetime.datetime.fromisoformat(adage_year["debut"])

        if start.year == 2025:
            logger.info("Found 2025-2026 year in adage : %s", adage_year)

            end = datetime.datetime.fromisoformat(adage_year["fin"])
            adage_id = adage_year["id"]

            educational_year = educational_models.EducationalYear(
                beginningDate=start, expirationDate=end, adageId=adage_id
            )
            db.session.add(educational_year)
            break

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
