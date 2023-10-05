import logging
import os
import os.path
import pathlib
import tempfile

from geoalchemy2.shape import from_shape
import geopandas as gpd
from py7zr import unpack_7zarchive

from pcapi.core.geography import models as geography_models
from pcapi.core.geography.constants import WGS_SPATIAL_REFERENCE_IDENTIFIER
from pcapi.models import db


logger = logging.getLogger(__name__)


def import_iris_from_7z(path: str) -> None:
    if not os.path.exists(path):
        message = f"archive not found for path {path}"
        logger.error(message)
        raise ValueError(message)

    with tempfile.TemporaryDirectory(prefix="import_iris_from_7z") as unpack_directory:
        imported = 0
        unpack_7zarchive(archive=path, path=unpack_directory)
        shp_files = pathlib.Path(unpack_directory).glob("**/*.shp")
        for shp_file in shp_files:
            imported += import_iris_from_shp_file(shp_file)
        db.session.commit()
        logger.info("successfuly imported %s iris", imported)


def import_iris_from_shp_file(path_obj: pathlib.Path) -> int:
    iris_data = gpd.read_file(path_obj)
    filtered_iris_data = iris_data[["CODE_IRIS", "geometry"]]
    count = 0
    for iris_row in filtered_iris_data.to_crs(WGS_SPATIAL_REFERENCE_IDENTIFIER).iterrows():
        count += 1
        iris = geography_models.IrisFrance(
            code=iris_row[1]["CODE_IRIS"],
            shape=from_shape(iris_row[1]["geometry"], srid=WGS_SPATIAL_REFERENCE_IDENTIFIER),
        )
        db.session.add(iris)
    logger.info("imported %s iris", count)
    return count
