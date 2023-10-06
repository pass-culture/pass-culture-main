import pathlib

import pytest

from pcapi.core.geography import api
from pcapi.core.geography import repository

import tests


DATA_DIR = pathlib.Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class GetIrisFromCoordinatesTest:
    @classmethod
    def setup_class(cls):
        path = DATA_DIR / "iris_min.7z"
        api.import_iris_from_7z(str(path))

    def test_get_iris_from_coordinates_found(self):
        # in a polygon
        result = repository.get_iris_from_coordinates(lat=17.900710, lon=-62.834786)
        assert result.code == "977010102"  # Saint-Barthélemy

        # in a multi-polygon
        result = repository.get_iris_from_coordinates(lat=47.03589297809895, lon=-56.33341471630671)
        assert result.code == "975010000"  # Miquelon-Langlade

    def test_get_iris_from_coordinates_not_found(self):
        result = repository.get_iris_from_coordinates(lon=0, lat=0)
        assert result is None
