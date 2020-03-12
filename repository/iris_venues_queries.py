from typing import List

from models import IrisVenues
from models.db import db
from repository import repository

MAXIMUM_DISTANCE_IN_METERS = 100000


def find_ids_of_irises_located_near_venue(venue_id: int) -> List[int]:
    search_radius = MAXIMUM_DISTANCE_IN_METERS
    query = f''' WITH venue_coordinates AS (SELECT longitude, latitude from venue WHERE id = {venue_id})
                 SELECT id FROM iris_france, venue_coordinates
                 WHERE ST_DISTANCE(centroid, CAST(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) AS GEOGRAPHY))
                 < {search_radius} ;
    '''
    iris = db.session.execute(query).fetchall()
    return [iris.id for iris in iris]


def insert_venue_in_iris_venue(venue_id: int, iris_ids_near_venue: List[int]) -> None:
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


def get_iris_containing_user_location(latitude: float, longitude: float) -> int:
    query = f'''SELECT id FROM iris_france 
    WHERE ST_CONTAINS(shape, ST_SetSRID(ST_MakePoint({longitude}, {latitude}), 4326))
    ORDER BY id;'''

    return db.session.execute(query).scalar()


def find_venues_located_near_iris(iris_id: int) -> List[int]:
    iris_venues = IrisVenues.query.filter_by(irisId=iris_id).all()
    return [iris_venue.venueId for iris_venue in iris_venues]
