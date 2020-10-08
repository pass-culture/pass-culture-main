from typing import List, Dict

from flask import json

from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from pcapi.utils.human_ids import humanize


def serialize_venues_with_offerer_name(venues: List[VenueWithOffererName]) -> json:
    return [serialize_venue_with_offerer_name(venue) for venue in venues]


def serialize_venue_with_offerer_name(venue: VenueWithOffererName) -> Dict:
    return {
        'id': humanize(venue.identifier),
        'name': venue.name,
        'offererName': venue.offerer_name,
        'isVirtual': venue.is_virtual,
    }
