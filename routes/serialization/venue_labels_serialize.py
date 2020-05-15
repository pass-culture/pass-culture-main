from typing import Dict

from domain.venue.venue_label.venue_label import VenueLabel
from utils.human_ids import humanize


def serialize_venue_label(venue_label: VenueLabel) -> Dict:
    return {
        'id': humanize(venue_label.identifier),
        'label': venue_label.label,
    }
