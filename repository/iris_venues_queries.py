from typing import List

from models import IrisVenues
from models.db import db
from repository import repository

MAXIMUM_DISTANCE_IN_METERS = 100000


def find_irises_located_near_venue(venue_id: int) -> List:
    search_radius = MAXIMUM_DISTANCE_IN_METERS
    query = f''' WITH venue_coordinates AS (SELECT longitude, latitude from venue WHERE id = {venue_id})
                 SELECT id FROM iris_france, venue_coordinates
                 WHERE ST_DISTANCE(centroid, CAST(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) AS GEOGRAPHY))
                 < {search_radius} ;
    '''
    iris_ids = db.session.execute(query).fetchall()
    return [iris_id[0] for iris_id in iris_ids]


def insert_venue_in_iris_venues(venue_id: int, iris_ids_near_venue: List[int]) -> None:
    irises_venues = []
    for iris_id in iris_ids_near_venue:
        iris_venue = IrisVenues()
        iris_venue.venueId = venue_id
        iris_venue.irisId = iris_id
        irises_venues.append(iris_venue)

    repository.save(*irises_venues)


def delete_venue_from_iris_venues(venue_id: int) -> None:
    iris_venues_to_delete = IrisVenues.query \
        .filter_by(venueId=venue_id) \
        .all()
    repository.delete(*iris_venues_to_delete)
