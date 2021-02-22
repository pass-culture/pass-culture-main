from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from pcapi.models import Venue


def to_domain(venue_sql_entity: Venue) -> VenueWithOffererName:
    return VenueWithOffererName(
        identifier=venue_sql_entity.id,
        is_virtual=venue_sql_entity.isVirtual,
        managing_offerer_identifier=venue_sql_entity.managingOffererId,
        name=venue_sql_entity.name,
        offerer_name=venue_sql_entity.managingOfferer.name,
        public_name=venue_sql_entity.publicName,
        booking_email=venue_sql_entity.bookingEmail,
    )
