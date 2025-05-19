import pcapi.core.offers.api as offers_api
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.workers import worker
from pcapi.workers.decorators import job


@job(worker.low_queue)
def update_all_venue_offers_accessibility_job(venue: Venue, accessibility: dict[str, bool]) -> None:
    offer_query = db.session.query(Offer).filter(Offer.venueId == venue.id)
    collective_offer_query = db.session.query(CollectiveOffer).filter(CollectiveOffer.venueId == venue.id)
    collective_offer_template_query = db.session.query(CollectiveOfferTemplate).filter(
        CollectiveOfferTemplate.venueId == venue.id
    )

    offers_api.batch_update_offers(offer_query, accessibility)
    educational_api_offer.batch_update_collective_offers(collective_offer_query, accessibility)
    educational_api_offer.batch_update_collective_offers_template(collective_offer_template_query, accessibility)
