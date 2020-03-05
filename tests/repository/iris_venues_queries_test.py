from shapely.geometry import Polygon, Point

from repository import repository
from repository.iris_venues_queries import find_iris_near_venue
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue, create_offerer, create_iris

WGS_SPATIAL_REFERENCE_IDENTIFIER = 4326


@clean_database
def test_find_iris_near_venue_should_return_iris_ids_located_near_to_given_venue(app):
    # given
    offerer = create_offerer()
    venue_in_paris = create_venue(offerer=offerer, longitude=2.351499, latitude=48.856610, siret='12345678912345')

    centroid_1 = Point(2.295695, 49.894171)
    polygon_1 = Polygon([(0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)])

    centroid_2 = Point(2.086670, 49.440900)
    polygon_2 = Polygon([(0.2, 0.2), (0.3, 0.2), (0.3, 0.3), (0.3, 0.2)])

    iris_amiens = create_iris(centroid_1, polygon_1)
    iris_beauvais = create_iris(centroid_2, polygon_2)

    repository.save(iris_amiens, iris_beauvais, venue_in_paris)

    # when
    iris_id = find_iris_near_venue(venue_in_paris.id)

    # then
    assert iris_id == [iris_beauvais.id]
