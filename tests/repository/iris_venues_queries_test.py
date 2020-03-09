from shapely.geometry import Polygon

from models import IrisVenues
from repository import repository
from repository.iris_venues_queries import find_irises_located_near_venue, insert_venue_in_iris_venue, \
    delete_venue_from_iris_venues, link_user_to_iris

from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue, create_offerer, create_iris, create_iris_venue

WGS_SPATIAL_REFERENCE_IDENTIFIER = 4326


class FindIrisesLocatedNearVenueTest:
    @clean_database
    def test_should_return_ids_list_of_iris_located_near_given_venue(self, app):
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

    @clean_database
    def test_should_return_empty_list_when_no_iris_found_near_given_venue(self, app):
        # given
        offerer = create_offerer()
        venue_in_paris = create_venue(offerer=offerer, longitude=2.351499, latitude=48.856610)

        repository.save(venue_in_paris)

        # when
        iris_id = find_irises_located_near_venue(venue_in_paris.id)

        # then
        assert iris_id == []


class InsertVenueInIrisVenueTest:
    @clean_database
    def test_should_insert_venue_in_iris_venues(self, app):
        # Given
        polygon_1 = Polygon([(0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)])
        polygon_2 = Polygon([(0.1, 0.5), (0.6, 0.2), (0.8, 0.2), (0.9, 0.1)])

        iris_1 = create_iris(polygon_1)
        iris_2 = create_iris(polygon_2)

        offerer = create_offerer()
        venue = create_venue(offerer)

        repository.save(venue, iris_1, iris_2)

        iris_ids_near_to_venue = [iris_1.id, iris_2.id]

        # When
        insert_venue_in_iris_venue(venue.id, iris_ids_near_to_venue)

        # Then
        assert IrisVenues.query.count() == 2


class DeleteVenueFromIrisVenuesTest:
    @clean_database
    def test_should_delete_given_venue_from_iris_venues(self, app):
        # Given
        offerer = create_offerer()
        venue_1 = create_venue(offerer, siret='12345678912345')
        venue_2 = create_venue(offerer, siret='98765432198765')

        polygon_1 = Polygon([(0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)])
        polygon_2 = Polygon([(0.1, 0.5), (0.6, 0.2), (0.8, 0.2), (0.9, 0.1)])

        iris_1 = create_iris(polygon_1)
        iris_2 = create_iris(polygon_2)

        repository.save(iris_1, iris_2, venue_1, venue_2)

        iris_venue_1 = create_iris_venue(iris_1.id, venue_1.id)

        iris_venue_2 = create_iris_venue(iris_2.id, venue_2.id)

        repository.save(iris_venue_1, iris_venue_2)

        # When
        delete_venue_from_iris_venues(venue_1.id)

        # Then
        iris_venue = IrisVenues.query.all()

        assert len(iris_venue) == 1
        assert iris_venue[0].venueId == venue_2.id
        assert iris_venue[0].irisId == iris_2.id


class LinkUserToIrisTest:
    @clean_database
    def test_should_link_user_to_iris_when_his_location_is_in_one_iris(self, app):
        # Given
        user_latitude = 49.894171
        user_longitude = 2.295695

        polygon_1 = Polygon([(0, 0), (0, 2), (2, 0), (2, 2)])
        polygon_2 = Polygon([(2.195693, 49.994169), (2.195693, 47.894173),
                             (2.595697, 47.894173), (2.595697, 49.994169)])

        iris_1 = create_iris(polygon_1)
        iris_2 = create_iris(polygon_2)

        repository.save(iris_1, iris_2)

        # When
        iris_id = link_user_to_iris(user_latitude, user_longitude)

        # Then
        assert iris_id == iris_2.id

    @clean_database
    def test_should_link_user_to_first_iris_returned_when_his_location_is_in_two_irises(self, app):
        # Given
        user_latitude = 49.894171
        user_longitude = 2.295695

        polygon_1 = Polygon([(2.095693, 50.994169), (2.095693, 47.894173),
                             (2.795697, 47.894173), (2.795697, 50.994169)])
        polygon_2 = Polygon([(2.195693, 49.994169), (2.195693, 47.894173),
                             (2.595697, 47.894173), (2.595697, 49.994169)])

        iris_1 = create_iris(polygon_1)
        iris_2 = create_iris(polygon_2)

        repository.save(iris_1, iris_2)

        # When
        iris_id = link_user_to_iris(user_latitude, user_longitude)

        # Then
        assert iris_id == iris_1.id

    @clean_database
    def test_should_not_link_user_to_iris_if_no_iris_is_found(self, app):
        # Given
        user_latitude = 0
        user_longitude = 0

        # When
        iris_id = link_user_to_iris(user_latitude, user_longitude)

        # Then
        assert iris_id is None
