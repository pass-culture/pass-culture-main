"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-44666-backend-script-global-de-rattrapage \
  -f NAMESPACE=close_closed_venues \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import enum
import itertools
import logging
import typing
from collections.abc import Mapping

import pydantic
from google.cloud import bigquery
from google.cloud.bigquery import ArrayQueryParameter

from pcapi import settings
from pcapi.connectors.big_query.queries.base import MalformedRow
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


Row = bigquery.table.Row
RowIterator = typing.Generator[Row]


class ClosedVenueStatusEnum(enum.Enum):
    A = "A"
    F = "F"


class ClosedVenueSirenModel(pydantic.BaseModel):
    siret: str
    status: ClosedVenueStatusEnum


def run_query(query: str, page_size: int, sirets: tuple[str]) -> RowIterator:
    client = bigquery.Client()
    job_config = bigquery.QueryJobConfig(query_parameters=[ArrayQueryParameter("sirets", "STRING", sirets)])
    query_job = client.query(query, job_config=job_config)
    return (row for row in query_job.result(page_size))


def execute_query(sirets: tuple[str], page_size: int = 1_000) -> typing.Iterator[ClosedVenueSirenModel]:
    raw_query = f"""
        SELECT
            siret,
            etatAdministratifEtablissement as status,
        FROM
            `{settings.BIG_QUERY_CLEANED_TABLE_BASENAME}.siret_data`
        WHERE
            siret IN @sirets AND etatAdministratifEtablissement = 'F'
    """
    rows = run_query(raw_query, page_size=page_size, sirets=sirets)
    for index, row in enumerate(rows):
        try:
            yield ClosedVenueSirenModel(**typing.cast(Mapping, row))
        except (pydantic.ValidationError, TypeError) as err:
            raise MalformedRow(msg=str(row), index=index, model=ClosedVenueSirenModel, raw_query=raw_query) from err


def main(apply: bool) -> None:
    # get all sirets
    sirets = [
        siret
        for (siret,) in db.session.query(offerers_models.Venue.siret).filter(
            offerers_models.Venue.siret.is_not(None),
        )
    ]

    # process by batches
    for batched_siret in itertools.batched(sirets, 10_000):
        for siret, status in execute_query(batched_siret):
            with atomic(apply=apply):
                venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.siret == siret).one()
                if not venue.is_closed and not offerers_api._has_been_tagged_as_closed(venue):
                    offerers_api._mark_as_closed_and_send_warning_email(venue, apply=apply)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main(apply=args.apply)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
