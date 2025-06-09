from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.scripts.acceslibre.match_acceslibre import match_acceslibre
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.low_queue)
def match_acceslibre_job(venue_id: int) -> None:
    if venue := db.session.get(offerers_models.Venue, venue_id):
        match_acceslibre(venue)
