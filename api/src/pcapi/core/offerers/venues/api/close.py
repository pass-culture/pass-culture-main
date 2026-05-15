from pcapi.core import search
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import models as offers_models
from pcapi.models import db


def put_venue_offers_to_halt(venue: models.Venue) -> None:
    """Deactivate, unindex offers and deactivate any related synchronization

    > Please keep in mind that no booking will be cancelled here.
    > And no email will be sent to the users with a related booking.
      They should be notified at the cancel step (done before or after
      this one).
    """
    offer_ids = {o.id for o in venue.offers}
    query = db.session.query(offers_models.Offer).filter(offers_models.Offer.id.in_(offer_ids))

    offers_api.batch_update_offers(query=query, update_fields={"publicationDatetime": None})
    search.unindex_offer_ids(offer_ids)
    offerers_api.delete_venue_pivots(venue.id)
