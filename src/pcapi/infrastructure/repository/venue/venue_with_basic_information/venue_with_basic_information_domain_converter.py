from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information import VenueWithBasicInformation
from pcapi.models import VenueSQLEntity


def to_domain(venue_sql_entity: VenueSQLEntity) -> VenueWithBasicInformation:
    return VenueWithBasicInformation(identifier=venue_sql_entity.id,
                                     name=venue_sql_entity.name,
                                     siret=venue_sql_entity.siret,
                                     )
