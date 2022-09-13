from urllib.parse import urlencode

from pcapi import settings
from pcapi.core.bookings.models import Booking
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers.models import Offer
from pcapi.utils.human_ids import humanize


def generate_firebase_dynamic_link(path: str, params: dict | None) -> str:
    universal_link_url = f"{settings.WEBAPP_V2_URL}/{path}"
    if params:
        universal_link_url = universal_link_url + f"?{urlencode(params)}"

    firebase_dynamic_query_string = urlencode({"link": universal_link_url})
    return f"{settings.FIREBASE_DYNAMIC_LINKS_URL}/?{firebase_dynamic_query_string}"


def booking_app_link(booking: Booking) -> str:
    return f"{settings.WEBAPP_V2_URL}/reservation/{booking.id}/details"


def build_pc_pro_offer_link(offer: CollectiveOffer | CollectiveOfferTemplate | Offer) -> str:
    if isinstance(offer, CollectiveOffer):
        return f"{settings.PRO_URL}/offre/{humanize(offer.id)}/collectif/edition"

    if isinstance(offer, CollectiveOfferTemplate):
        return f"{settings.PRO_URL}/offre/T-{humanize(offer.id)}/collectif/edition"

    return f"{settings.PRO_URL}/offre/{humanize(offer.id)}/individuel/edition"


def build_pc_pro_offerer_link(offerer: offerers_models.Offerer) -> str:
    return f"{settings.PRO_URL}/accueil?structure={humanize(offerer.id)}"


def build_pc_pro_venue_link(venue: offerers_models.Venue) -> str:
    if venue.isVirtual:
        return build_pc_pro_offerer_link(venue.managingOfferer)
    return f"{settings.PRO_URL}/structures/{humanize(venue.managingOffererId)}/lieux/{humanize(venue.id)}"


def build_pc_pro_venue_bookings_link(venue: offerers_models.Venue) -> str:
    return f"{settings.PRO_URL}/reservations?offerVenueId={humanize(venue.id)}"
