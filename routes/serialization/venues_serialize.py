from typing import List, Dict

from flask import json

from domain.venue.venue_with_offerer_informations.venue_with_offerer_informations import VenueWithOffererInformations
from utils.human_ids import humanize


def serialize_venues_with_offerer_informations(venues: List[VenueWithOffererInformations]) -> json:
    return [serialize_venue_with_offerer_informations(venue) for venue in venues]


def serialize_venue_with_offerer_informations(venue: VenueWithOffererInformations) -> Dict:
    return {
        'id': humanize(venue.id),
        'name': venue.name,
        'offererName': venue.offerer_name,
        'isVirtual': venue.is_virtual,
    }
