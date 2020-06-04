from domain.venue.venue_with_offerer_informations.venue_with_offerer_informations import VenueWithOffererInformations
from models import VenueSQLEntity


def to_domain(venue_sql_entity: VenueSQLEntity) -> VenueWithOffererInformations:
    return VenueWithOffererInformations(id=venue_sql_entity.id,
                 is_virtual=venue_sql_entity.isVirtual,
                 name=venue_sql_entity.name,
                 offerer_name=venue_sql_entity.managingOfferer.name,
                 )
