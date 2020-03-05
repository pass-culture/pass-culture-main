from shapely.geometry import Polygon, Point

from models import IrisVenues
from repository import repository
from repository.iris_venues_queries import find_irises_located_near_venue, insert_venue_in_iris_venues
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue, create_offerer, create_iris

WGS_SPATIAL_REFERENCE_IDENTIFIER = 4326


class FindIrisesLocatedNearVenueTest:
    @clean_database
    def test_should_return_ids_list_of_iris_located_near_to_given_venue(self, app):
        # given
        offerer = create_offerer()
        venue_in_paris = create_venue(offerer=offerer, longitude=2.351499, latitude=48.856610)

        polygon_amiens = Polygon([(2.295693, 49.894169), (2.295693, 49.894173),
                                  (2.295697, 49.894173), (2.295697, 49.894169)])

        polygon_beauvais = Polygon([(2.086668, 49.440898), (2.086668, 49.440902),
                                    (2.086672, 49.440902), (2.086672, 49.440898)])

        iris_amiens = create_iris(polygon_amiens)
        iris_beauvais = create_iris(polygon_beauvais)

        repository.save(iris_amiens, iris_beauvais, venue_in_paris)

        # when
        iris_id = find_irises_located_near_venue(venue_in_paris.id)

        # then
        assert iris_id == [iris_beauvais.id]


class InsertVenueInIrisVenuesTest:
    @clean_database
    def test_should_insert_venue_in_iris_venues(self, app):
        # Given
        polygon_1 = Polygon([(0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)])
        polygon_2 = Polygon([(0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)])

        iris_1 = create_iris(polygon_1)
        iris_2 = create_iris(polygon_2)

        offerer = create_offerer()
        venue = create_venue(offerer)

        repository.save(venue, iris_1, iris_2)

        iris_ids_near_to_venue = [iris_1.id, iris_2.id]

        # When
        insert_venue_in_iris_venues(venue.id, iris_ids_near_to_venue)

        # Then
        assert IrisVenues.query.count() == 2
