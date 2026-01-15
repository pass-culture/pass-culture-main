from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.low_queue)
def match_acceslibre_job(venue_id: int) -> None:
    if venue := db.session.get(offerers_models.Venue, venue_id):
        offerers_api.match_acceslibre(venue)
