import dataclasses
import pathlib

import pytest

from pcapi.core.geography import api
from pcapi.core.geography import models

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
        assert models.IrisFrance.query.count() == 6


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
