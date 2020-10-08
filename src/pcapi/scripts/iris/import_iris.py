import geopandas as gpd
from geoalchemy2.shape import from_shape
from geopandas import GeoDataFrame, GeoSeries
from shapely.geometry import Point, Polygon

from pcapi.models import IrisFrance
from pcapi.repository import repository

WGS_SPATIAL_REFERENCE_IDENTIFIER = 4326


def import_iris_shape_file_to_table(file_path: str) -> None:
    iris = {}
    filtered_iris_data = read_iris_shape_file(file_path)
    for iris_row in filtered_iris_data.iterrows():
        iris[iris_row[0]] = fill_iris_from(iris_row[1])

    repository.save(*iris.values())


def read_iris_shape_file(file_path: str) -> GeoDataFrame:
    iris_data = gpd.read_file(file_path)
    filtered_iris_data = iris_data[['CODE_IRIS', 'geometry']]
    return filtered_iris_data.to_crs({'init': f'epsg:{WGS_SPATIAL_REFERENCE_IDENTIFIER}'})


def fill_iris_from(iris_row: GeoSeries) -> IrisFrance:
    iris = IrisFrance()

    iris.centroid = from_shape(create_centroid_from_polygon(iris_row['geometry']), srid=WGS_SPATIAL_REFERENCE_IDENTIFIER)
    iris.irisCode = iris_row['CODE_IRIS']
    iris.shape = from_shape(iris_row['geometry'], srid=WGS_SPATIAL_REFERENCE_IDENTIFIER)

    return iris


def create_centroid_from_polygon(polygon: Polygon) -> Point:
    return polygon.centroid
