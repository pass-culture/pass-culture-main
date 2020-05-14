from typing import Callable, List

from models.venue_label import VenueLabel


def get_venue_labels(get_all_venue_labels: Callable) -> List[VenueLabel]:
    return get_all_venue_labels()
