from datetime import datetime
import logging

import click

from pcapi.core.subscription.ubble.archive_past_identification_pictures import archive_past_identification_pictures
from pcapi.utils.blueprint import Blueprint


logger = logging.getLogger(__name__)
blueprint = Blueprint(__name__, __name__)

# FIXME (jsdupuis 2022-03-03): delete this script when the images of past identifications have been archived


@blueprint.cli.command("archive_past_identifications")
@click.argument("start_date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.argument("end_date", type=click.DateTime(formats=["%Y-%m-%d"]), required=True)
@click.argument("limit", type=int, required=False)
@click.argument("status", type=bool, required=False)
def ubble_archive_past_identifications(
    start_date: datetime, end_date: datetime, limit: int, status: bool | None
) -> None:
    result = archive_past_identification_pictures(start_date, end_date, limit, status)
    print("Done :")
    print(f"Total records : ....................... {result.total}")
    print(f"archive successful : .................. {result.pictures_archived}")
    print(f"not archived (see logs for details) : . {result.pictures_not_archived}")
    print(f"errors (see logs for details) : ....... {result.errors}")
