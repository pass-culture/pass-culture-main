import pathlib

import pytest

from pcapi.core.geography import api
from pcapi.core.geography import models

import tests


DATA_DIR = pathlib.Path(tests.__path__[0]) / "files"


@pytest.mark.usefixtures("db_session")
class ImportIrisTest:
    def test_import_iris(self):
        path = DATA_DIR / "iris_min.7z"
        api.import_iris_from_7z(str(path))
        assert models.IrisFrance.query.count() == 6
