from typing import Dict
from typing import List

from pcapi.models import IrisVenues
from pcapi.models.db import db
from pcapi.repository import repository


def find_ids_of_irises_located_near_venue(venue_id: int, search_radius: int) -> List[int]:
    query = f""" WITH venue_coordinates AS (SELECT longitude, latitude from venue WHERE id = {venue_id})
                 SELECT id FROM iris_france, venue_coordinates
                 WHERE ST_DISTANCE(centroid, CAST(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) AS GEOGRAPHY))
                 < {search_radius} ;
    """
    iris = db.session.execute(query).fetchall()
    return [iris.id for iris in iris]


def insert_venue_in_iris_venue(venue_id: int, iris_ids_near_venue: List[int]) -> None:
    irises_venues = [{"venueId": venue_id, "irisId": iris_id} for iris_id in iris_ids_near_venue]
    _bulk_insert_iris_venues(irises_venues)


def delete_venue_from_iris_venues(venue_id: int) -> None:
    iris_venues_to_delete = IrisVenues.query.filter_by(venueId=venue_id).all()
    repository.delete(*iris_venues_to_delete)


def get_iris_containing_user_location(latitude: float, longitude: float) -> int:
    query = f"""SELECT id FROM iris_france 
    WHERE ST_CONTAINS(shape, ST_SetSRID(ST_MakePoint({longitude}, {latitude}), 4326))
    ORDER BY id;"""

    return db.session.execute(query).scalar()


def find_venues_located_near_iris(iris_id: int) -> List[int]:
    iris_venues = IrisVenues.query.filter_by(irisId=iris_id).all()
    return [iris_venue.venueId for iris_venue in iris_venues]


def _bulk_insert_iris_venues(iris_venue_information: List[Dict]) -> None:
    db.session.bulk_insert_mappings(IrisVenues, iris_venue_information)
    db.session.commit()
