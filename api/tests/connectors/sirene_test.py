import pytest
import requests_mock

from pcapi.connectors import sirene
from pcapi.core.testing import override_settings

from . import sirene_test_data


@override_settings(SIRENE_BACKEND="pcapi.connectors.sirene.InseeBackend")
def test_get_siren():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIREN_COMPANY,
        )
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3/siret/{siren}00017",
            json=sirene_test_data.RESPONSE_SIRET_COMPANY,
        )
        siren_info = sirene.get_siren(siren)
        assert siren_info.siren == siren
        assert siren_info.name == "LE PETIT RINTINTIN"
        assert siren_info.head_office_siret == "12345678900017"
        assert siren_info.ape_code == "47.61Z"
        assert siren_info.legal_category_code == "5499"
        assert siren_info.address.street == "1 BD POISSONIERE"
        assert siren_info.address.postal_code == "75002"
        assert siren_info.address.city == "PARIS"


@override_settings(SIRENE_BACKEND="pcapi.connectors.sirene.InseeBackend")
def test_get_siren_of_entreprise_individuelle():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIREN_ENTREPRISE_INDIVIDUELLE,
        )
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3/siret/{siren}00045",
            json=sirene_test_data.RESPONSE_SIRET_COMPANY,
        )
        siren_info = sirene.get_siren(siren)
        # Don't test everything again. The only difference is in how
        # the name is retrieved.
        assert siren_info.name == "PIERRE EXEMPLE"


@override_settings(SIRENE_BACKEND="pcapi.connectors.sirene.InseeBackend")
def test_get_siren_without_address():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIREN_COMPANY,
        )
        siren_info = sirene.get_siren(siren, with_address=False)
        assert siren_info.siren == siren
        assert siren_info.name == "LE PETIT RINTINTIN"
        assert siren_info.address is None


@override_settings(SIRENE_BACKEND="pcapi.connectors.sirene.InseeBackend")
def test_get_siret():
    siret = "12345678900017"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3/siret/{siret}",
            json=sirene_test_data.RESPONSE_SIRET_COMPANY,
        )
        siret_info = sirene.get_siret(siret)
        assert siret_info.siret == siret
        assert siret_info.name == "LE PETIT RINTINTIN"
        assert siret_info.address.street == "1 BD POISSONIERE"
        assert siret_info.address.postal_code == "75002"
        assert siret_info.address.city == "PARIS"


@override_settings(SIRENE_BACKEND="pcapi.connectors.sirene.InseeBackend")
def test_get_siret_of_entreprise_individuelle():
    siret = "12345678900045"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3/siret/{siret}",
            json=sirene_test_data.RESPONSE_SIRET_ENTREPRISE_INDIVIDUELLE,
        )
        siret_info = sirene.get_siret(siret)
        assert siret_info.siret == siret
        # Don't test everything again. The only difference is in how
        # the name is retrieved.
        assert siret_info.name == "PIERRE EXEMPLE"


@override_settings(SIRENE_BACKEND="pcapi.connectors.sirene.InseeBackend")
def test_get_legal_category():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIREN_COMPANY,
        )
        category = sirene.get_legal_category(siren)
        assert category == {
            "legal_category_code": "5499",
            "legal_category_label": "Société à responsabilité limitée (sans autre indication)",
        }


@override_settings(SIRENE_BACKEND="pcapi.connectors.sirene.InseeBackend")
def test_siret_is_active():
    siret = "12345678900017"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3/siret/{siret}",
            json=sirene_test_data.RESPONSE_SIRET_COMPANY,
        )
        active = sirene.siret_is_active(siret)
        assert active


@pytest.mark.parametrize(
    "status_code,expected_exception",
    [
        (301, sirene.UnknownEntityException),
        (400, sirene.InvalidFormatException),
        (403, sirene.NonPublicDataException),
        (404, sirene.UnknownEntityException),
        (500, sirene.SireneApiException),
        (503, sirene.SireneApiException),
    ],
)
@override_settings(SIRENE_BACKEND="pcapi.connectors.sirene.InseeBackend")
def test_error_handling(status_code, expected_exception):
    siret = "invalid"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3/siret/{siret}",
            status_code=status_code,
        )
        with pytest.raises(expected_exception):
            sirene.get_siret(siret)
