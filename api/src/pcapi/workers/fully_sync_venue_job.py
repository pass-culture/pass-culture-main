from pcapi.core.offerers import models as offerers_models
from pcapi.scripts.stock.fully_sync_venue import fully_sync_venue
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.low_queue)
def fully_sync_venue_job(venue_id: int) -> None:
    venue = offerers_models.Venue.query.filter_by(id=venue_id).one()
    fully_sync_venue(venue)
