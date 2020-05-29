from typing import List, Dict

from flask import json

from domain.venue.venue import Venue
from utils.human_ids import humanize


def serialize_venues(venues: List[Venue]) -> json:
    return [serialize_venue(venue) for venue in venues]


def serialize_venue(venue: Venue) -> Dict:
    return {
        'id': humanize(venue.id),
        'name': venue.name,
        'isVirtual': venue.is_virtual,
    }
