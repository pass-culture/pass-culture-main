from typing import Dict

from pcapi.domain.venue.venue_label.venue_label import VenueLabel
from pcapi.utils.human_ids import humanize


def serialize_venue_label(venue_label: VenueLabel) -> Dict:
    return {
        'id': humanize(venue_label.identifier),
        'label': venue_label.label,
    }
