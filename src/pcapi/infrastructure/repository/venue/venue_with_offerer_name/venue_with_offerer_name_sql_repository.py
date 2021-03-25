from typing import List
from typing import Optional

from pcapi.core.offerers.models import Offerer
from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name_repository import VenueWithOffererNameRepository
from pcapi.infrastructure.repository.venue.venue_with_offerer_name import venue_with_offerer_name_domain_converter
from pcapi.models import UserOfferer
from pcapi.models import Venue


class VenueWithOffererNameSQLRepository(VenueWithOffererNameRepository):
    def get_by_pro_identifier(
        self,
        pro_identifier: int,
        user_is_admin: bool,
        active_offerers_only: bool,
        offerer_id: Optional[Identifier] = None,
        validated_offerer: Optional[bool] = None,
        validated_offerer_for_user: Optional[bool] = None,
    ) -> List[VenueWithOffererName]:
        query = Venue.query.join(Offerer, Offerer.id == Venue.managingOffererId).join(
            UserOfferer, UserOfferer.offererId == Offerer.id
        )
        if not user_is_admin:
            query = query.filter(UserOfferer.userId == pro_identifier)

        if validated_offerer is not None:
            if validated_offerer:
                query = query.filter(Offerer.validationToken.is_(None))
            else:
                query = query.filter(Offerer.validationToken.isnot(None))
        if validated_offerer_for_user is not None:
            if validated_offerer_for_user:
                query = query.filter(UserOfferer.validationToken.is_(None))
            else:
                query = query.filter(UserOfferer.validationToken.isnot(None))

        if active_offerers_only:
            query = query.filter(Offerer.isActive.is_(True))

        if offerer_id:
            query = query.filter(Venue.managingOffererId == offerer_id.persisted)

        venue_sql_entities = query.order_by(Venue.name).all()
        return [
            venue_with_offerer_name_domain_converter.to_domain(venue_sql_entity)
            for venue_sql_entity in venue_sql_entities
        ]
