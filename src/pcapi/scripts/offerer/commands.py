from flask import current_app as app

from pcapi.scripts.offerer.delete_cascade_offerer_by_id import delete_cascade_offerer_by_id


@app.manager.option(
    "-i", "--id", dest="offerer_id", required=True, help="Id of the offerer to cascade delete", type=int
)
def delete_offerer(offerer_id: int) -> None:
    delete_cascade_offerer_by_id(offerer_id)
