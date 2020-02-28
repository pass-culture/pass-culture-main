import geopandas as gpd
from geoalchemy2.shape import from_shape
from geopandas import GeoDataFrame, GeoSeries
from shapely.geometry import Point, Polygon

from models import IrisFrance
from repository import repository

WGS_SPATIAL_REFERENCE_IDENTIFIER = 4326


def import_iris_shape_file_to_table(file_path: str):
    filtered_iris_data = read_iris_shape_file(file_path)
    for iris_row in filtered_iris_data.iterrows():
        fill_iris_from(iris_row[1])


def read_iris_shape_file(file_path: str) -> GeoDataFrame:
    iris_data = gpd.read_file(file_path)
    filtered_iris_data = iris_data[['CODE_IRIS', 'geometry']]
    filtered_iris_data_in_wgs_format = filtered_iris_data.to_crs({'init': f'epsg:{WGS_SPATIAL_REFERENCE_IDENTIFIER}'})
    return filtered_iris_data_in_wgs_format


def fill_iris_from(iris_row: GeoSeries):
    iris = IrisFrance()

    iris.centroid = from_shape(create_centroid_from_polygon(iris_row['geometry']), srid=WGS_SPATIAL_REFERENCE_IDENTIFIER)
    iris.irisCode = iris_row['CODE_IRIS']
    iris.shape = from_shape(iris_row['geometry'], srid=WGS_SPATIAL_REFERENCE_IDENTIFIER)

    repository.save(iris)


def create_centroid_from_polygon(polygon: Polygon) -> Point:
    return polygon.centroid
