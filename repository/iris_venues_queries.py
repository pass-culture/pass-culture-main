from typing import List

from models.db import db


def find_iris_near_venue(venueId: int) -> List:
    query = f''' WITH venue_coordinates AS (SELECT longitude, latitude from venue WHERE id = {venueId})
                 SELECT id from iris_france, venue_coordinates
                 WHERE ST_DISTANCE(centroid, CAST(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) AS GEOGRAPHY))
                 < 100000 ;
    '''
    return db.session.execute(query).fetchall()


# query_1 = f''' WITH iris_centroid AS (
#                 SELECT centroid from iris_france WHERE id = {iris_id}
#                 )
#                 SELECT id FROM venue, iris_centroid
#                 WHERE ST_DISTANCE(
#                 centroid,
#                 CAST(ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) AS GEOGRAPHY)
#                 ) < 100000;'''

