from sqlalchemy import func

from pcapi.core.offerers.models import Venue
from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information import VenueWithBasicInformation
from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information_repository import (
    VenueWithBasicInformationRepository,
)
from pcapi.infrastructure.repository.venue.venue_with_basic_information import (
    venue_with_basic_information_domain_converter,
)


class VenueWithBasicInformationSQLRepository(VenueWithBasicInformationRepository):
    def find_by_siret(self, siret: str) -> VenueWithBasicInformation | None:
        venue_sql_entity = Venue.query.filter_by(siret=siret).one_or_none()
        return venue_with_basic_information_domain_converter.to_domain(venue_sql_entity) if venue_sql_entity else None

    def find_by_name(self, name: str, offerer_id: int) -> list[VenueWithBasicInformation]:
        venue_sql_entities = (
            Venue.query.filter_by(managingOffererId=offerer_id)
            .filter(Venue.siret.is_(None))
            .filter(func.lower(Venue.name) == func.lower(name))
            .all()
        )
        return [
            venue_with_basic_information_domain_converter.to_domain(venue_sql_entity)
            for venue_sql_entity in venue_sql_entities
        ]
