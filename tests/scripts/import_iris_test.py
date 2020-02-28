import os
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Polygon, Point

from models import IrisFrance
from scripts.import_iris import read_iris_shape_file, import_iris_shape_file_to_table, fill_iris_from, \
    create_centroid_from_polygon
from tests.conftest import clean_database


def test_read_iris_shape_file_should_read_shape_file_and_return_correct_data_in_wgs84_format():
    # given
    file_path = Path(os.path.dirname(os.path.realpath('tests/files/geolocation_data/test_guyane/test_guyane.shp')))

    # when
    iris_df = read_iris_shape_file(file_path)

    # then
    assert list(iris_df.columns) == ['CODE_IRIS', 'geometry']
    assert iris_df.shape[0] == 1
    assert iris_df.crs == {'init': 'epsg:4326'}


@clean_database
def test_fill_iris_from_should_save_iris_row_in_table(app):
    # Given
    iris_row = gpd.GeoSeries(data={'CODE_IRIS': '973020116',
                                   'geometry': Polygon([(0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)])})

    # When
    fill_iris_from(iris_row)

    # Check
    assert IrisFrance.query.count() == 1


@clean_database
def test_import_iris_shape_file_to_table_should_import_shape_from_file_and_write_on_iris_table(app):
    # Given
    filepath = Path(os.path.dirname(os.path.realpath('tests/files/geolocation_data/test_guyane/test_guyane.shp')))

    # When
    import_iris_shape_file_to_table(filepath)

    # Then
    assert IrisFrance.query.count() == 1


def test_create_centroid_from_polygon_should_return_the_centroid_of_given_polygon():
    # given
    polygon = Polygon([(0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1)])
    expected_centroid = Point(0.15, 0.15)

    # when
    centroid = create_centroid_from_polygon(polygon)

    # then
    assert centroid == expected_centroid
