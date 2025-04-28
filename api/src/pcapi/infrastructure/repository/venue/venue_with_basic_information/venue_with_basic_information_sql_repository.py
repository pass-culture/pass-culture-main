from pcapi.core.offerers.models import Venue
from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information import VenueWithBasicInformation
from pcapi.domain.venue.venue_with_basic_information.venue_with_basic_information_repository import (
    VenueWithBasicInformationRepository,
)
from pcapi.infrastructure.repository.venue.venue_with_basic_information import (
    venue_with_basic_information_domain_converter,
)
from pcapi.models import db


class VenueWithBasicInformationSQLRepository(VenueWithBasicInformationRepository):
    def find_by_dms_token(self, dms_token: str) -> VenueWithBasicInformation | None:
        venue_sql_entity = db.session.query(Venue).filter_by(dmsToken=dms_token).one_or_none()
        return venue_with_basic_information_domain_converter.to_domain(venue_sql_entity) if venue_sql_entity else None
