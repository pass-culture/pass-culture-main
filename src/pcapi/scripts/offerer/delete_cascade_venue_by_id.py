import logging

from pcapi.core import search
from pcapi.core.bookings.exceptions import CannotDeleteVenueWithBookingsException
from pcapi.core.bookings.models import Booking
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import Favorite
from pcapi.models import AllocineVenueProvider
from pcapi.models import AllocineVenueProviderPriceRule
from pcapi.models import BankInformation
from pcapi.models import OfferCriterion
from pcapi.models import VenueProvider
from pcapi.models import db


logger = logging.getLogger(__name__)


def delete_cascade_venue_by_id(venue_id: int) -> None:
    venue_has_bookings = db.session.query(Booking.query.filter(Booking.venueId == venue_id).exists()).scalar()

    if venue_has_bookings:
        raise CannotDeleteVenueWithBookingsException()

    deleted_stocks_count = Stock.query.filter(Stock.offerId == Offer.id, Offer.venueId == venue_id).delete(
        synchronize_session=False
    )

    deleted_favorites_count = Favorite.query.filter(Favorite.offerId == Offer.id, Offer.venueId == venue_id).delete(
        synchronize_session=False
    )

    deleted_offer_criteria_count = OfferCriterion.query.filter(
        OfferCriterion.offerId == Offer.id, Offer.venueId == venue_id
    ).delete(synchronize_session=False)

    deleted_mediations_count = Mediation.query.filter(Mediation.offerId == Offer.id, Offer.venueId == venue_id).delete(
        synchronize_session=False
    )

    AllocineVenueProviderPriceRule.query.filter(
        AllocineVenueProviderPriceRule.allocineVenueProviderId == AllocineVenueProvider.id,
        AllocineVenueProvider.id == VenueProvider.id,
        VenueProvider.venueId == venue_id,
        Venue.id == venue_id,
    ).delete(synchronize_session=False)
    deleted_allocine_venue_providers_count = AllocineVenueProvider.query.filter(
        AllocineVenueProvider.id == VenueProvider.id,
        VenueProvider.venueId == venue_id,
        Venue.id == venue_id,
    ).delete(synchronize_session=False)

    offer_ids_to_delete = [id[0] for id in db.session.query(Offer.id).filter(Offer.venueId == venue_id).all()]

    deleted_offers_count = Offer.query.filter(Offer.venueId == venue_id).delete(synchronize_session=False)

    deleted_venue_providers_count = VenueProvider.query.filter(VenueProvider.venueId == venue_id).delete(
        synchronize_session=False
    )

    deleted_bank_informations_count = 0
    deleted_bank_informations_count += BankInformation.query.filter(BankInformation.venueId == venue_id).delete(
        synchronize_session=False
    )

    deleted_venues_count = Venue.query.filter(Venue.id == venue_id).delete(synchronize_session=False)

    deleted_bank_informations_count += BankInformation.query.filter(BankInformation.venueId == venue_id).delete(
        synchronize_session=False
    )

    db.session.commit()

    search.unindex_offer_ids(offer_ids_to_delete)
    search.unindex_venue_ids([venue_id])

    recap_data = {
        "offer_ids_to_unindex": offer_ids_to_delete,
        "venue_id": venue_id,
        "deleted_bank_informations_count": deleted_bank_informations_count,
        "deleted_venues_count": deleted_venues_count,
        "deleted_venue_providers_count": deleted_venue_providers_count,
        "deleted_allocine_venue_providers_count": deleted_allocine_venue_providers_count,
        "deleted_offers_count": deleted_offers_count,
        "deleted_mediations_count": deleted_mediations_count,
        "deleted_favorites_count": deleted_favorites_count,
        "deleted_offer_criteria_count": deleted_offer_criteria_count,
        "deleted_stocks_count": deleted_stocks_count,
    }
    logger.info("Deleted venue", extra=recap_data)

    return recap_data
