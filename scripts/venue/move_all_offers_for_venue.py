from models import VenueSQLEntity
from repository import repository


def move_all_offers_from_venue_to_other_venue(origin_venue_id: str, destination_venue_id: str) -> None:
    origin_venue = VenueSQLEntity.query.filter_by(id=origin_venue_id).one()
    offers = origin_venue.offers
    for o in offers:
        o.venueId = destination_venue_id
    repository.save(*offers)
