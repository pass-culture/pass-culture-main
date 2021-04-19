from pcapi.models import IrisVenues
from pcapi.models.db import db
from pcapi.repository import repository


def find_ids_of_irises_located_near_venue(venue_id: int, search_radius: int) -> list[int]:
    query = """
    WITH venue_coordinates AS (SELECT longitude, latitude from venue WHERE id = :venue_id)
    SELECT id FROM iris_france, venue_coordinates
    WHERE
      ST_DISTANCE(centroid, CAST(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) AS GEOGRAPHY))
      < :search_radius
    """
    params = {"venue_id": venue_id, "search_radius": search_radius}
    iris = db.session.execute(query, params).fetchall()
    return [iris.id for iris in iris]


def insert_venue_in_iris_venue(venue_id: int, iris_ids_near_venue: list[int]) -> None:
    irises_venues = [{"venueId": venue_id, "irisId": iris_id} for iris_id in iris_ids_near_venue]
    _bulk_insert_iris_venues(irises_venues)


def delete_venue_from_iris_venues(venue_id: int) -> None:
    iris_venues_to_delete = IrisVenues.query.filter_by(venueId=venue_id).all()
    repository.delete(*iris_venues_to_delete)


def _bulk_insert_iris_venues(iris_venue_information: list[dict]) -> None:
    db.session.bulk_insert_mappings(IrisVenues, iris_venue_information)
    db.session.commit()
