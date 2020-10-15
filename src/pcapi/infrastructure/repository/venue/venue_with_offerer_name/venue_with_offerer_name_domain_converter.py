from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from pcapi.models import VenueSQLEntity


def to_domain(venue_sql_entity: VenueSQLEntity) -> VenueWithOffererName:
    return VenueWithOffererName(identifier=venue_sql_entity.id,
                                is_virtual=venue_sql_entity.isVirtual,
                                name=venue_sql_entity.name,
                                offerer_name=venue_sql_entity.managingOfferer.name,
                                public_name=venue_sql_entity.publicName)
