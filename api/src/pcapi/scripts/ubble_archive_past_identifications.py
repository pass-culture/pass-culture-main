import datetime
import logging

import click

from pcapi.core.subscription.ubble.archive_past_identification_pictures import archive_past_identification_pictures
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("archive_past_identifications")
@click.argument("start_date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.argument("end_date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.argument("limit", type=int, required=False)
@click.argument("status", type=bool, required=False)
def ubble_archive_past_identifications(
    start_date: datetime.datetime, end_date: datetime.datetime, limit: int, status: bool | None
) -> None:
    result = archive_past_identification_pictures(start_date, end_date, status, limit)
    print("Done :")
    print(f"Total records : ....................... {result.total}")
    print(f"archive successful : .................. {result.pictures_archived}")
    print(f"not archived (see logs for details) : . {result.pictures_not_archived}")
    print(f"errors (see logs for details) : ....... {result.errors}")


@blueprint.cli.command("archive_past_identifications_automation")
def ubble_archive_past_identifications_automation() -> None:
    # call the archive function on the last 6 months for the statuses "None"
    # (the archive process has never been executed)
    # and "False" (the archive process has executed but failed)
    end_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    start_date = end_date - datetime.timedelta(days=186)
    archive_past_identification_pictures(start_date, end_date, None)
    archive_past_identification_pictures(start_date, end_date, False)
