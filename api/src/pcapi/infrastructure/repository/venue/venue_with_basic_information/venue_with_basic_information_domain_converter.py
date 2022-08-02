from pcapi.core.offerers.models import Venue
from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information import VenueWithBasicInformation


def to_domain(venue_sql_entity: Venue) -> VenueWithBasicInformation:
    return VenueWithBasicInformation(
        identifier=venue_sql_entity.id,
        name=venue_sql_entity.name,  # type: ignore [arg-type]
        siret=venue_sql_entity.siret,  # type: ignore [arg-type]
        publicName=venue_sql_entity.publicName,  # type: ignore [arg-type]
        bookingEmail=venue_sql_entity.bookingEmail,
    )
