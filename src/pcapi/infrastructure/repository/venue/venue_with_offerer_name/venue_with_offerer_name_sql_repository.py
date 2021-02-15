from typing import List
from typing import Optional

from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name_repository import VenueWithOffererNameRepository
from pcapi.infrastructure.repository.venue.venue_with_offerer_name import venue_with_offerer_name_domain_converter
from pcapi.models import Offerer
from pcapi.models import UserOfferer
from pcapi.models import Venue


class VenueWithOffererNameSQLRepository(VenueWithOffererNameRepository):
    def get_by_pro_identifier(
        self,
        pro_identifier: int,
        user_is_admin: bool,
        offerer_id: Optional[Identifier] = None,
    ) -> List[VenueWithOffererName]:
        query = Venue.query

        if not user_is_admin:
            query = (
                query.join(Offerer, Offerer.id == Venue.managingOffererId)
                .filter(Offerer.validationToken.is_(None))
                .join(UserOfferer, UserOfferer.offererId == Offerer.id)
                .filter(UserOfferer.validationToken.is_(None))
                .filter(UserOfferer.userId == pro_identifier)
            )

        if offerer_id:
            query = query.filter(Venue.managingOffererId == offerer_id.persisted)

        venue_sql_entities = query.order_by(Venue.name).all()
        return [
            venue_with_offerer_name_domain_converter.to_domain(venue_sql_entity)
            for venue_sql_entity in venue_sql_entities
        ]
