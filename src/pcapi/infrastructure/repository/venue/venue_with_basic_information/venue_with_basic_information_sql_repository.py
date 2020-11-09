from typing import List

from sqlalchemy import func

from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information import VenueWithBasicInformation
from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information_repository import (
    VenueWithBasicInformationRepository,
)
from pcapi.infrastructure.repository.venue.venue_with_basic_information import (
    venue_with_basic_information_domain_converter,
)
from pcapi.models import VenueSQLEntity


class VenueWithBasicInformationSQLRepository(VenueWithBasicInformationRepository):
    def find_by_siret(self, siret: str) -> VenueWithBasicInformation:
        venue_sql_entity = VenueSQLEntity.query \
            .filter_by(siret=siret) \
            .one_or_none()
        return venue_with_basic_information_domain_converter.to_domain(venue_sql_entity) if venue_sql_entity else None

    def find_by_name(self, name: str, offerer_id: int) -> List[VenueWithBasicInformation]:
        venue_sql_entities = VenueSQLEntity.query \
            .filter_by(managingOffererId=offerer_id) \
            .filter(VenueSQLEntity.siret == None) \
            .filter(func.lower(VenueSQLEntity.name) == func.lower(name)) \
            .all()
        return [venue_with_basic_information_domain_converter.to_domain(venue_sql_entity) for venue_sql_entity in venue_sql_entities]
