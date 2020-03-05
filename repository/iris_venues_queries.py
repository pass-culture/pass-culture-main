from typing import List

from models import IrisVenues
from models.db import db
from repository import repository


def find_iris_near_venue(venue_id: int) -> List:
    maximum_distance_in_meters = 100000
    query = f''' WITH venue_coordinates AS (SELECT longitude, latitude from venue WHERE id = {venue_id})
                 SELECT id from iris_france, venue_coordinates
                 WHERE ST_DISTANCE(centroid, CAST(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) AS GEOGRAPHY))
                 < {maximum_distance_in_meters} ;
    '''
    iris_ids = db.session.execute(query).fetchall()
    return [iris_id[0] for iris_id in iris_ids]


def insert_venue_in_iris_venues(venue_id: int, iris_ids_near_venue: List[int]) -> None:
    for iris_id in iris_ids_near_venue:
        iris_venue = IrisVenues()
        iris_venue.venueId = venue_id
        iris_venue.irisId = iris_id
        repository.save(iris_venue)
