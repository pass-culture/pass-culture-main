import pathlib

import pytest

from pcapi.core.geography import api
from pcapi.core.geography import factories
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


@pytest.mark.usefixtures("db_session")
class GetAddressByBanIdTest:

    def test_address_found(self):
        ban_id = "coucou_me_revoilou"
        factories.AddressFactory(banId="un_Autre_ban_id", inseeCode=None)
        address = factories.AddressFactory(
            banId=ban_id,
            inseeCode=None,
            postalCode="75001",
            city="Paris",
            street="182 Rue Saint-Honoré",
            latitude=48.8669567,
            longitude=2.310144,
        )

        result = repository.get_address_by_ban_id(ban_id)
        assert result == address

    def test_address_not_found(self):
        factories.AddressFactory()
        result = repository.get_address_by_ban_id("ban_id")

        assert result is None


@pytest.mark.usefixtures("db_session")
class GetAddressByLatLongTest:

    @pytest.mark.parametrize(
        "latitude,longitude",
        [
            (48.8669567, 2.310144),
            (48.86695670, 2.3101440),
            (48.86696, 2.31014),
        ],
    )
    def test_address_found(self, latitude, longitude):
        factories.AddressFactory(banId="un_Autre_ban_id", inseeCode=None)
        address = factories.AddressFactory(
            banId="un_Autre_ban_id",
            inseeCode=None,
            postalCode="75001",
            city="Paris",
            street="182 Rue Saint-Honoré",
            latitude=48.8669567,
            longitude=2.310144,
        )

        result = repository.get_address_by_lat_long(latitude=latitude, longitude=longitude)
        assert result == address

    def test_address_not_found(self):
        factories.AddressFactory()
        result = repository.get_address_by_lat_long(latitude=48.8669567, longitude=2.31014)

        assert result is None
