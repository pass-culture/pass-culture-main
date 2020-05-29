from domain.venue.venue import Venue
from models import VenueSQLEntity


def to_domain(venue_sql_entity: VenueSQLEntity) -> Venue:
    return Venue(id=venue_sql_entity.id,
                 is_virtual=venue_sql_entity.isVirtual,
                 name=venue_sql_entity.name,
                 siret=venue_sql_entity.siret,
                 )
