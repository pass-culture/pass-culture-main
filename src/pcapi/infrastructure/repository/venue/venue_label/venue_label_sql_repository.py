from typing import List

from pcapi.domain.venue.venue_label.venue_label import VenueLabel
from pcapi.domain.venue.venue_label.venue_label_repository import VenueLabelRepository
from pcapi.infrastructure.repository.venue.venue_label import venue_label_domain_converter
from pcapi.models import VenueLabelSQLEntity


class VenueLabelSQLRepository(VenueLabelRepository):
    def get_all(self) -> List[VenueLabel]:
        venue_labels_sql_entities = VenueLabelSQLEntity.query.all()
        return [venue_label_domain_converter.to_domain(venue_label) for venue_label in venue_labels_sql_entities]
