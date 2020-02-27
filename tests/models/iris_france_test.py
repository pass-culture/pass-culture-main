from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon
from shapely.geometry.multipolygon import MultiPolygon

from models import IrisFrance
from repository import repository
from tests.conftest import clean_database


@clean_database
def test_iris_creation_should_save_a_multipolygon_in_iris_france_table(app):
    # given
    iris = IrisFrance()

    iris.irisCode = '908765437'
    iris.irisType = 'H'
    iris.shape = from_shape(MultiPolygon(
        [(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)), [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))])]),
        srid=4326)

    # when
    repository.save(iris)

    # then
    assert IrisFrance.query.count() == 1


@clean_database
def test_iris_creation_should_save_a_polygon_in_iris_france_table(app):
    # given
    iris = IrisFrance()

    iris.irisCode = '908765437'
    iris.irisType = 'H'
    iris.shape = from_shape(Polygon([(0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)]), srid=4326)

    # when
    repository.save(iris)

    # then
    assert IrisFrance.query.count() == 1
