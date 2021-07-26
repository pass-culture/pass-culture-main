from flask import current_app as app

from pcapi.scripts.offerer.delete_cascade_offerer_by_id import delete_cascade_offerer_by_id
from pcapi.scripts.offerer.delete_cascade_venue_by_id import delete_cascade_venue_by_id


@app.manager.option(
    "-i", "--id", dest="offerer_id", required=True, help="Id of the offerer to cascade delete", type=int
)
def delete_offerer(offerer_id: int) -> None:
    delete_cascade_offerer_by_id(offerer_id)


@app.manager.option("-i", "--id", dest="venue_id", required=True, help="Id of the venue to cascade delete", type=int)
def delete_venue(venue_id: int) -> None:
    delete_cascade_venue_by_id(venue_id)
