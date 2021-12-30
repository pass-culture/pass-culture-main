from pcapi.core.finance.models import BusinessUnit
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.repository import repository


def venue_have_at_least_one_offer(venue: int) -> bool:
    return db.session.query(
        Venue.query.join(Offer, Venue.id == Offer.venueId).filter(Venue.id == venue.id).exists()
    ).scalar()


def purge_virtual_venue_business_units():
    business_units = BusinessUnit.query.all()
    for business_unit in business_units:
        virtual_venues = [venue for venue in business_unit.venues if venue.isVirtual]
        if len(virtual_venues) > 0:
            virtual_venue = virtual_venues[0]
            lonely_venue = len(business_unit.venues) == 1
            have_offer = venue_have_at_least_one_offer(virtual_venue)
            if lonely_venue or not have_offer:
                virtual_venue.businessUnitId = None
                if lonely_venue:
                    repository.delete(business_unit)
