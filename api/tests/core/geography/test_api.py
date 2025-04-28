import dataclasses
import decimal
import pathlib

import pytest

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
        assert db.session.query(models.IrisFrance).count() == 6


def test_to_wkt_polygon():
    coordinates = [
        [[35, 10], [45, 45], [15, 40], [10, 20], [35, 10]],
        [[20, 30], [35, 35], [30, 20], [20, 30]],
    ]
    geom = FakeFionaGeometry("Polygon", coordinates)
    transformer = FakeTransformer()

    wkt = api._to_wkt(geom, transformer)

    assert wkt == "POLYGON ((35 10, 45 45, 15 40, 10 20, 35 10), (20 30, 35 35, 30 20, 20 30))"


def test_to_wkt_multipolygon():
    coordinates = [
        [[[40, 40], [20, 45], [45, 30], [40, 40]]],
        [
            [[20, 35], [10, 30], [10, 10], [30, 5], [45, 20], [20, 35]],
            [[30, 20], [20, 15], [20, 25], [30, 20]],
        ],
    ]
    geom = FakeFionaGeometry("MultiPolygon", coordinates)
    transformer = FakeTransformer()

    wkt = api._to_wkt(geom, transformer)

    assert (
        wkt
        == "MULTIPOLYGON (((40 40, 20 45, 45 30, 40 40)), ((20 35, 10 30, 10 10, 30 5, 45 20, 20 35), (30 20, 20 15, 20 25, 30 20)))"
    )


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
