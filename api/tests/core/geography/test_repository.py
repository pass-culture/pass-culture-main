import pathlib
from unittest.mock import patch

import pytest

from pcapi.connectors import api_adresse
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
class GetIrisFromAddressTest:
    @patch("pcapi.core.geography.repository.get_iris_from_coordinates")
    @patch(
        "pcapi.connectors.api_adresse.get_municipality_centroid",
        return_value=api_adresse.AddressInfo(
            id="unused",
            label="unused",
            postcode="unused",
            citycode="unused",
            score=1,
            latitude=17.900710,
            longitude=-62.834786,
            city="unused",
            street=None,
        ),
    )
    def test_get_iris_from_postcode_and_missing_address(
        self, mock_get_municipality_centroid, mock_get_iris_from_coordinates
    ):
        repository.get_iris_from_address(".", "97133", city="Gustavia")
        mock_get_municipality_centroid.assert_called_once_with(postcode="97133", city="Gustavia")
        mock_get_iris_from_coordinates.assert_called_once_with(lat=17.900710, lon=-62.834786)

    @pytest.mark.parametrize(
        "exception",
        [
            api_adresse.AdresseApiServerErrorException,
            api_adresse.NoResultException,
            api_adresse.InvalidFormatException,
        ],
    )
    @patch("pcapi.core.geography.repository.get_iris_from_coordinates")
    @patch(
        "pcapi.connectors.api_adresse.get_municipality_centroid",
        return_value=api_adresse.AddressInfo(
            id="unused",
            label="unused",
            postcode="unused",
            citycode="unused",
            score=1,
            latitude=17.900710,
            longitude=-62.834786,
            city="unused",
            street=None,
        ),
    )
    @patch("pcapi.connectors.api_adresse.get_address")
    def test_get_iris_from_after_address_causes_error(
        self, mock_get_address, mock_get_municipality_centroid, mock_get_iris_from_coordinates, exception
    ):
        mock_get_address.side_effect = exception()
        repository.get_iris_from_address("Il y a un problème ici", "97133", city="Gustavia")
        mock_get_address.assert_called_once()
        mock_get_municipality_centroid.assert_called_once_with(postcode="97133", city="Gustavia")
        mock_get_iris_from_coordinates.assert_called_once_with(lat=17.900710, lon=-62.834786)


@pytest.mark.usefixtures("db_session")
class SearchAddressesTest:
    def test_one_address_found(self):
        factories.AddressFactory(banId="un_Autre_ban_id", inseeCode=None)
        address = factories.AddressFactory(
            banId="75101_8635_00182",
            postalCode="75001",
            city="Paris",
            street="182 Rue Saint-Honoré",
            latitude=48.86696,
            longitude=2.31014,
        )

        result = repository.search_addresses(street="182 Rue Saint-Honoré", city="Paris", postal_code="75001")
        assert len(result) == 1
        assert result[0] == address

        # with latitude and longitude
        result2 = repository.search_addresses(
            street="182 Rue Saint-Honoré",
            city="Paris",
            postal_code="75001",
            latitude=48.86696,
            longitude=2.31014,
        )
        assert len(result2) == 1
        assert result2[0] == address

        # with too precise latitude and longitude
        result2 = repository.search_addresses(
            street="182 Rue Saint-Honoré",
            city="Paris",
            postal_code="75001",
            latitude=48.866957,  # round to 48.86696
            longitude=2.310142,  # round to 2.31014
        )
        assert len(result2) == 1
        assert result2[0] == address

    def test_multiple_address_found(self):
        address = factories.AddressFactory(
            banId="75101_8635_00182",
            postalCode="75001",
            city="Paris",
            street="182 Rue Saint-Honoré",
            latitude=48.86696,
            longitude=2.31014,
        )
        # address with different lat/long
        address2 = factories.AddressFactory(
            banId="un_Autre_ban_id",
            inseeCode=None,
            postalCode="75001",
            city="Paris",
            street="182 Rue Saint-Honoré",
            latitude=48.86697,
            longitude=2.31015,
        )

        result = repository.search_addresses(street="182 Rue Saint-Honoré", city="Paris", postal_code="75001")
        assert len(result) == 2
        assert result[0] == address
        assert result[1] == address2

        # with latitude and longitude
        result2 = repository.search_addresses(
            street="182 Rue Saint-Honoré",
            city="Paris",
            postal_code="75001",
            latitude=48.86696,
            longitude=2.31014,
        )
        assert len(result2) == 1
        assert result2[0] == address

        result3 = repository.search_addresses(
            street="182 Rue Saint-Honoré",
            city="Paris",
            postal_code="75001",
            latitude=48.86697,
            longitude=2.31015,
        )
        assert len(result3) == 1
        assert result3[0] == address2


class GetCoordinatesFromAddressTest:
    @patch(
        "pcapi.connectors.api_adresse.get_address",
        return_value=api_adresse.AddressInfo(
            id="unused",
            label="unused",
            postcode="unused",
            citycode="unused",
            score=1,
            latitude=17.900710,
            longitude=-62.834786,
            city="unused",
            street=None,
        ),
    )
    def test_get_coordinates_from_address(self, _mock_get_address):
        result = repository.get_coordinates_from_address("whatever", "97133")
        assert result == {"latitude": 17.900710, "longitude": -62.834786}

    def test_returns_none_if_no_postcode(self):
        result = repository.get_coordinates_from_address("1 rue du hasard", None)
        assert result is None
