from domain.venue.venue_label.venue_label import VenueLabel
from models import VenueLabelSQLEntity


def to_domain(venue_label_sql_entity: VenueLabelSQLEntity) -> VenueLabel:
    return VenueLabel(
        identifier=venue_label_sql_entity.id,
        label=venue_label_sql_entity.label
    )
