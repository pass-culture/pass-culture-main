from typing import Dict
from typing import List

from flask import json
from pydantic import BaseModel

from pcapi.domain.venue.venue_with_offerer_name.venue_with_offerer_name import VenueWithOffererName
from pcapi.utils.human_ids import humanize


def serialize_venues_with_offerer_name(venues: List[VenueWithOffererName]) -> json:
    return [serialize_venue_with_offerer_name(venue) for venue in venues]


def serialize_venue_with_offerer_name(venue: VenueWithOffererName) -> Dict:
    return {
        "id": humanize(venue.identifier),
        "managingOffererId": humanize(venue.managing_offerer_identifier),
        "name": venue.name,
        "offererName": venue.offerer_name,
        "publicName": venue.public_name,
        "isVirtual": venue.is_virtual,
        "bookingEmail": venue.booking_email,
    }


class VenueStatsResponseModel(BaseModel):
    activeBookingsQuantity: int
    activeOffersQuantity: int
    usedBookingsQuantity: int
