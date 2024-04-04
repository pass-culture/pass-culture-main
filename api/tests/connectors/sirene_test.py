import pytest
import requests_mock

from pcapi.connectors.entreprise import exceptions
from pcapi.connectors.entreprise import sirene
from pcapi.core.testing import override_settings

from . import sirene_test_data


@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siren():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIREN_COMPANY,
        )
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siren}00017",
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
        assert siren_info.active
        assert siren_info.diffusible

    # Test cache, no HTTP request
    siren_info = sirene.get_siren(siren)
    assert siren_info.siren == siren


@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siren_of_entreprise_individuelle():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIREN_ENTREPRISE_INDIVIDUELLE,
        )
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siren}00045",
            json=sirene_test_data.RESPONSE_SIRET_COMPANY,
        )
        siren_info = sirene.get_siren(siren)
        # Don't test everything again. The only difference is in how
        # the name is retrieved.
        assert siren_info.name == "PIERRE EXEMPLE"


@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siren_without_address():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIREN_COMPANY,
        )
        siren_info = sirene.get_siren(siren, with_address=False)
        assert siren_info.siren == siren
        assert siren_info.name == "LE PETIT RINTINTIN"
        assert siren_info.address is None


@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siren_with_non_public_data():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIREN_COMPANY_WITH_NON_PUBLIC_DATA,
        )
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siren}00001",
            json=sirene_test_data.RESPONSE_SIRET_COMPANY_WITH_NON_PUBLIC_DATA,
        )
        with pytest.raises(exceptions.NonPublicDataException):
            sirene.get_siren(siren)


@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siren_with_non_public_data_do_not_raise():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIREN_COMPANY_WITH_NON_PUBLIC_DATA,
        )
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siren}00001",
            json=sirene_test_data.RESPONSE_SIRET_COMPANY_WITH_NON_PUBLIC_DATA,
        )
        siren_info = sirene.get_siren(siren, raise_if_non_public=False)
        assert siren_info.siren == siren
        assert siren_info.name == "[ND]"
        assert siren_info.active is True
        assert siren_info.diffusible is False


@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siren_without_ape():
    siren = "194700936"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIREN_WITHOUT_APE,
        )
        siren_info = sirene.get_siren(siren, with_address=False, raise_if_non_public=False)
        assert siren_info.siren == siren
        assert siren_info.name == "LYCEE D'ENSEIGNEMENT PROFESSIONNEL"
        assert siren_info.ape_code is None


@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siret():
    siret = "12345678900017"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}",
            json=sirene_test_data.RESPONSE_SIRET_COMPANY,
        )
        siret_info = sirene.get_siret(siret)
        assert siret_info.siret == siret
        assert siret_info.name == "LE PETIT RINTINTIN"
        assert siret_info.address.street == "1 BD POISSONIERE"
        assert siret_info.address.postal_code == "75002"
        assert siret_info.address.city == "PARIS"
        assert siret_info.ape_code == "47.61Z"
        assert siret_info.legal_category_code == "5499"

    # Test cache, no HTTP request
    siret_info = sirene.get_siret(siret)
    assert siret_info.siret == siret


@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siret_of_entreprise_individuelle():
    siret = "12345678900045"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}",
            json=sirene_test_data.RESPONSE_SIRET_ENTREPRISE_INDIVIDUELLE,
        )
        siret_info = sirene.get_siret(siret)
        assert siret_info.siret == siret
        # Don't test everything again. The only difference is in how
        # the name is retrieved.
        assert siret_info.name == "PIERRE EXEMPLE"


@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siret_with_non_public_data():
    siret = "12345678900017"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}",
            json=sirene_test_data.RESPONSE_SIRET_COMPANY_WITH_NON_PUBLIC_DATA,
        )
        with pytest.raises(exceptions.NonPublicDataException):
            sirene.get_siret(siret)


@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siret_with_non_public_data_do_not_raise():
    siret = "12345678900017"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}",
            json=sirene_test_data.RESPONSE_SIRET_COMPANY_WITH_NON_PUBLIC_DATA,
        )
        siret_info = sirene.get_siret(siret, raise_if_non_public=False)
        assert siret_info.siret == siret
        assert siret_info.name == "[ND]"
        assert siret_info.active is True
        assert siret_info.diffusible is False


@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_siret_is_active():
    siret = "12345678900017"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}",
            json=sirene_test_data.RESPONSE_SIRET_COMPANY,
        )
        active = sirene.siret_is_active(siret)
        assert active


@pytest.mark.parametrize(
    "status_code,expected_exception",
    [
        (301, exceptions.UnknownEntityException),
        (400, exceptions.InvalidFormatException),
        (403, exceptions.NonPublicDataException),
        (404, exceptions.UnknownEntityException),
        (500, exceptions.ApiException),
        (503, exceptions.ApiException),
    ],
)
@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_error_handling(status_code, expected_exception):
    siret = "invalid"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}",
            status_code=status_code,
        )
        with pytest.raises(expected_exception):
            sirene.get_siret(siret)


@override_settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_error_handling_on_non_json_response():
    siret = "anything"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}",
            status_code=200,
            text="non-JSON content",
        )
        with pytest.raises(exceptions.ApiException):
            sirene.get_siret(siret)
