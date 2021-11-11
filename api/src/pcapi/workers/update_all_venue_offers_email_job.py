import pcapi.core.offers.api as offers_api
from pcapi.core.offers.models import Offer
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.low_queue)
def update_all_venue_offers_email_job(venue, email: str) -> None:
    query = Offer.query.filter(Offer.venueId == venue.id)

    offers_api.batch_update_offers(query, {"bookingEmail": email})
