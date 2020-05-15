from typing import List

from domain.venue.venue_label.venue_label import VenueLabel
from domain.venue.venue_label.venue_label_repository import VenueLabelRepository
from infrastructure.repository.venue.venue_label import venue_label_domain_converter
from models import VenueLabelSQLEntity


class VenueLabelSQLRepository(VenueLabelRepository):
    def get_all(self) -> List[VenueLabel]:
        venue_labels_sql_entities = VenueLabelSQLEntity.query.all()
        return [venue_label_domain_converter.to_domain(venue_label) for venue_label in venue_labels_sql_entities]
