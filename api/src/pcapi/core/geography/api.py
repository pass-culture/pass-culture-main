import logging
import math
import os.path
import pathlib
import tempfile
import typing

import fiona
import py7zr
import pyproj

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
    with fiona.open(path) as shapefile:
        count = 0
        transformer = pyproj.Transformer.from_crs(
            shapefile.crs,
            constants.WGS_SPATIAL_REFERENCE_IDENTIFIER,
        )
        for feature in shapefile.values():
            iris = models.IrisFrance(
                code=feature.properties["CODE_IRIS"],
                shape=_to_wkt(feature.geometry, transformer),
            )
            db.session.add(iris)
            count += 1
    return count


# If this function ever gets too complex, we could use the `geomet`
# Python package instead.
def _to_wkt(geometry: fiona.Geometry, transformer: pyproj.Transformer) -> str:
    def _polygon(rings: list) -> str:
        s = ""
        for ring in rings:
            s += "("
            for point in ring:
                lat, lon = transformer.transform(*point)
                # /!\ Order must be the same as in `get_iris_from_coordinates()`.
                s += f"{lon} {lat}, "
            s = s.rstrip(", ")
            s += "), "
        s = s.rstrip(", ")
        return s

    if geometry.type == "Polygon":
        return "POLYGON (%s)" % _polygon(geometry.coordinates)
    if geometry.type == "MultiPolygon":
        s = ", ".join(["(%s)" % _polygon(polygon) for polygon in geometry.coordinates])
        return f"MULTIPOLYGON ({s})"
    raise ValueError(f"Unsupported type of geometry: {geometry.type}")


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
