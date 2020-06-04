from domain.venue.venue_identifier.venue_identifier import VenueIdentifier
from models import VenueSQLEntity


def to_domain(venue_sql_entity: VenueSQLEntity) -> VenueIdentifier:
    return VenueIdentifier(id=venue_sql_entity.id,
                 name=venue_sql_entity.name,
                 siret=venue_sql_entity.siret,
                 )
