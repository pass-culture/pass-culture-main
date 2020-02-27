import geopandas as gpd
from geoalchemy2.shape import from_shape
from geopandas import GeoDataFrame, GeoSeries

from models import IrisFrance
from repository import repository


def import_iris_shape_file_to_table(file_path: str):
    filtered_iris_data = read_iris_shape_file(file_path)
    for iris_row in filtered_iris_data.iterrows():
        fill_iris_from(iris_row[1])


def read_iris_shape_file(file_path: str) -> GeoDataFrame:
    iris_data = gpd.read_file(file_path)
    filtered_iris_data = iris_data[['CODE_IRIS', 'TYP_IRIS', 'geometry']]
    filtered_iris_data = filtered_iris_data.to_crs({'init': 'epsg:4326'})
    return filtered_iris_data


def fill_iris_from(iris_row: GeoSeries):
    iris = IrisFrance()

    iris.irisCode = iris_row['CODE_IRIS']
    iris.irisType = iris_row['TYP_IRIS']
    iris.shape = from_shape(iris_row['geometry'], srid=4326)

    repository.save(iris)
