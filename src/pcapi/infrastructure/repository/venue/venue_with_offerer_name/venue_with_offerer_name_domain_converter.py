from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from pcapi.models import VenueSQLEntity


def to_domain(venue_sql_entity: VenueSQLEntity) -> VenueWithOffererName:
    venue_name = venue_sql_entity.publicName if venue_sql_entity.publicName else venue_sql_entity.name
    return VenueWithOffererName(identifier=venue_sql_entity.id,
                                is_virtual=venue_sql_entity.isVirtual,
                                name=venue_name,
                                offerer_name=venue_sql_entity.managingOfferer.name)
