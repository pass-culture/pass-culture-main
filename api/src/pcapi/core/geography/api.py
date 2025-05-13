import logging
import math
import os.path
import pathlib
import tempfile
import typing

import py7zr
import pyproj
import shapefile
from shapely.geometry import shape as shapely_shape
from shapely.ops import transform as shapely_transform

from pcapi.models import db

from . import constants
from . import models


if typing.TYPE_CHECKING:
    from pcapi.core.educational import models as educational_models
    from pcapi.core.offerers import models as offerers_models

logger = logging.getLogger(__name__)


def import_iris_from_7z(path: str) -> None:
    if not os.path.exists(path):
        message = f"archive not found for path {path}"
        logger.error(message)
        raise ValueError(message)

    with tempfile.TemporaryDirectory(prefix="import_iris_from_7z") as unpack_directory:
        imported = 0
        py7zr.unpack_7zarchive(archive=path, path=unpack_directory)
        shp_files = pathlib.Path(unpack_directory).glob("**/*.shp")
        for shp_file in shp_files:
            imported += import_iris_from_shp_file(shp_file)
        db.session.commit()
        logger.info("successfuly imported %s iris", imported)


def import_iris_from_shp_file(path: pathlib.Path) -> int:
    sf = shapefile.Reader(str(path))
    fields = [field[0] for field in sf.fields[1:]]  # skip DeletionFlag
    count = 0

    # Source projection from .prj file
    prj_path = path.with_suffix(".prj")
    if not prj_path.exists():
        raise ValueError(f"Missing .prj file for {path}")

    with open(prj_path) as f:
        prj_text = f.read()
        source_crs = pyproj.CRS.from_wkt(prj_text)

    target_crs = pyproj.CRS.from_epsg(constants.WGS_SPATIAL_REFERENCE_IDENTIFIER)
    transformer = pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True)

    project = lambda x, y: transformer.transform(x, y)

    for sr in sf.shapeRecords():
        geom = shapely_shape(sr.shape.__geo_interface__)
        reprojected = shapely_transform(project, geom)
        props = dict(zip(fields, sr.record))

        iris = models.IrisFrance(
            code=props["CODE_IRIS"],
            shape=reprojected.wkt,
        )
        db.session.add(iris)
        count += 1

    return count


def compute_distance(first_point: models.Coordinates, second_point: models.Coordinates) -> float:
    """
    Spherical law of cosines with coordinates
    Return the distance between two points in kilometers
    """

    earth_radius_km = 6371.01
    first_lat = math.radians(first_point.latitude)
    first_lon = math.radians(first_point.longitude)
    second_lat = math.radians(second_point.latitude)
    second_lon = math.radians(second_point.longitude)
    return earth_radius_km * math.acos(
        math.sin(first_lat) * math.sin(second_lat)
        + math.cos(first_lat) * math.cos(second_lat) * math.cos(first_lon - second_lon)
    )


def get_coordinates(
    item: "educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate | offerers_models.Venue",
) -> models.Coordinates | None:
    if item.offererAddress is None:
        return None

    return models.Coordinates(
        latitude=item.offererAddress.address.latitude, longitude=item.offererAddress.address.longitude
    )
