import dataclasses
import decimal
import pathlib

import pytest
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from shapely.geometry.base import BaseGeometry

from pcapi.core.geography import api
from pcapi.core.geography import models
from pcapi.models import db

import tests


DATA_DIR = pathlib.Path(tests.__path__[0]) / "files"


@dataclasses.dataclass
class FakeFionaGeometry:
    type: str
    coordinates: list


class FakeTransformer:
    def transform(self, *args):
        return args[::-1]


@pytest.mark.usefixtures("db_session")
class ImportIrisTest:
    def test_import_iris(self):
        path = DATA_DIR / "iris_min.7z"
        api.import_iris_from_7z(str(path))
        iris = db.session.query(models.IrisFrance).order_by(models.IrisFrance.code).all()
        assert len(iris) == 6
        iris_codes = [iri.code for iri in iris]
        assert iris_codes == ["975010000", "975020101", "975020102", "977010101", "977010102", "977010103"]
        assert isinstance(iris[0].shape, WKBElement)  # Assert that the shape stored is a PostGIS spatial object
        geom = to_shape(iris[0].shape)
        assert isinstance(geom, BaseGeometry)  # Assert that it converts to a Shapely geometry


def test_compute_distance():
    first_point = models.Coordinates(latitude=40, longitude=40)
    result = api.compute_distance(first_point, first_point)
    assert result == pytest.approx(0, abs=0.01)

    # float
    first_point = models.Coordinates(latitude=48.87, longitude=2.33)
    second_point = models.Coordinates(latitude=44.83, longitude=-0.57)
    result = api.compute_distance(first_point, second_point)
    assert result == pytest.approx(500, 1)  # Paris - Bordeaux

    # Decimal
    first_point = models.Coordinates(latitude=decimal.Decimal("48.87"), longitude=decimal.Decimal("2.33"))
    second_point = models.Coordinates(latitude=decimal.Decimal("-17.77"), longitude=decimal.Decimal("-143.90"))
    result = api.compute_distance(first_point, second_point)
    assert result == pytest.approx(15_416, 1)  # Paris - Papeete
