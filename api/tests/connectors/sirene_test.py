import copy
import datetime

import pytest
import requests_mock

from pcapi.connectors.entreprise import api as api_insee
from pcapi.connectors.entreprise import exceptions
from pcapi.connectors.entreprise import sirene

from . import sirene_test_data


@pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
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
        siren_info = api_insee.get_siren(siren)
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
        assert siren_info.creation_date == datetime.date(2022, 5, 24)
        assert siren_info.closure_date is None

    # Test cache, no HTTP request
    siren_info = api_insee.get_siren(siren)
    assert siren_info.siren == siren


@pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
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
        siren_info = api_insee.get_siren(siren)
        # Don't test everything again. The only difference is in how
        # the name is retrieved.
        assert siren_info.name == "PIERRE EXEMPLE"


@pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siren_without_address():
    siren = "123456789"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIREN_COMPANY,
        )
        siren_info = api_insee.get_siren(siren, with_address=False)
        assert siren_info.siren == siren
        assert siren_info.name == "LE PETIT RINTINTIN"
        assert siren_info.address is None


@pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siren_without_ape():
    siren = "194700936"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIREN_WITHOUT_APE,
        )
        siren_info = api_insee.get_siren(siren, with_address=False, raise_if_non_public=False)
        assert siren_info.siren == siren
        assert siren_info.name == "LYCEE D'ENSEIGNEMENT PROFESSIONNEL"
        assert siren_info.ape_code is None


@pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siren_closed():
    siren = "111111118"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIREN_CLOSED,
        )
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siren}00019",
            json=sirene_test_data.RESPONSE_SIRET_CLOSED,
        )
        siren_info = api_insee.get_siren(siren)
        assert siren_info.siren == siren
        assert siren_info.name == "ENTREPRISE FERMEE"
        assert siren_info.active is False
        assert siren_info.creation_date == datetime.date(2001, 1, 2)
        assert siren_info.closure_date == datetime.date(2025, 1, 24)


@pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siren_closing_soon():
    siren = "111111118"
    closure_date = datetime.date.today() + datetime.timedelta(days=15)
    siren_response = copy.deepcopy(sirene_test_data.RESPONSE_SIREN_CLOSED)
    siren_response["uniteLegale"]["periodesUniteLegale"][1]["dateFin"] = (
        closure_date - datetime.timedelta(days=1)
    ).isoformat()
    siren_response["uniteLegale"]["periodesUniteLegale"][0]["dateDebut"] = closure_date.isoformat()

    with requests_mock.Mocker() as mock:
        mock.get(f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}", json=siren_response)
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siren}00019",
            json=sirene_test_data.RESPONSE_SIRET_CLOSED,
        )
        siren_info = api_insee.get_siren(siren)
        assert siren_info.siren == siren
        assert siren_info.active is True
        assert siren_info.creation_date == datetime.date(2001, 1, 2)
        assert siren_info.closure_date == closure_date


@pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siren_opening_soon():
    siren = "111111118"

    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}", json=sirene_test_data.RESPONSE_FUTURE_SIREN
        )
        siren_info = api_insee.get_siren(siren, with_address=False, raise_if_non_public=False)
        assert siren_info.siren == siren
        assert siren_info.active is True
        assert siren_info.diffusible is False
        assert siren_info.creation_date == datetime.date.today() + datetime.timedelta(days=10)
        assert siren_info.closure_date is None


@pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siren_without_period_date():
    siren = "333333334"

    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siren/{siren}",
            json=sirene_test_data.RESPONSE_SIRENE_WITHOUT_PERIOD_DATE,
        )
        siren_info = api_insee.get_siren(siren, with_address=False, raise_if_non_public=False)
        assert siren_info.siren == siren
        assert siren_info.active is False
        assert siren_info.diffusible is True
        assert siren_info.creation_date == datetime.date(1968, 1, 1)
        assert siren_info.closure_date is None


@pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siret():
    siret = "12345678900017"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}",
            json=sirene_test_data.RESPONSE_SIRET_COMPANY,
        )
        siret_info = api_insee.get_siret(siret)
        assert siret_info.siret == siret
        assert siret_info.name == "LE PETIT RINTINTIN"
        assert siret_info.address.street == "1 BD POISSONIERE"
        assert siret_info.address.postal_code == "75002"
        assert siret_info.address.city == "PARIS"
        assert siret_info.ape_code == "47.61Z"
        assert siret_info.legal_category_code == "5499"

    # Test cache, no HTTP request
    siret_info = api_insee.get_siret(siret)
    assert siret_info.siret == siret


@pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siret_of_entreprise_individuelle():
    siret = "12345678900045"
    with requests_mock.Mocker() as mock:
        mock.get(
            f"https://api.insee.fr/entreprises/sirene/V3.11/siret/{siret}",
            json=sirene_test_data.RESPONSE_SIRET_ENTREPRISE_INDIVIDUELLE,
        )
        siret_info = api_insee.get_siret(siret)
        assert siret_info.siret == siret
        # Don't test everything again. The only difference is in how
        # the name is retrieved.
        assert siret_info.name == "PIERRE EXEMPLE"


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
@pytest.mark.settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_error_handling(status_code, expected_exception):
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://api.insee.fr/entreprises/sirene/V3.11/siren",
            status_code=status_code,
        )
        with pytest.raises(expected_exception):
            sirene.get_siren_closed_at_date(datetime.date(2025, 1, 21))


@pytest.mark.settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_error_handling_on_non_json_response():
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://api.insee.fr/entreprises/sirene/V3.11/siren",
            status_code=200,
            text="non-JSON content",
        )
        with pytest.raises(exceptions.ApiException):
            sirene.get_siren_closed_at_date(datetime.date(2025, 1, 21))


@pytest.mark.settings(SIRENE_BACKEND="pcapi.connectors.entreprise.backends.insee.InseeBackend")
def test_get_siren_closed_at_date():
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://api.insee.fr/entreprises/sirene/V3.11/siren?q=dateDernierTraitementUniteLegale:2025-01-21+AND+periode(etatAdministratifUniteLegale:C+AND+changementEtatAdministratifUniteLegale:true)&champs=siren,dateDebut,dateFin,etatAdministratifUniteLegale&curseur=*&nombre=1000",
            status_code=200,
            json=sirene_test_data.RESPONSE_CLOSED_SIREN_PAGE1,
        )
        mock.get(
            "https://api.insee.fr/entreprises/sirene/V3.11/siren?q=dateDernierTraitementUniteLegale:2025-01-21+AND+periode(etatAdministratifUniteLegale:C+AND+changementEtatAdministratifUniteLegale:true)&champs=siren,dateDebut,dateFin,etatAdministratifUniteLegale&curseur=AoEpODg5Mjg4Mzc5&nombre=1000",
            status_code=200,
            json=sirene_test_data.RESPONSE_CLOSED_SIREN_PAGE2,
        )
        siren_list = sirene.get_siren_closed_at_date(datetime.date(2025, 1, 21))

    assert siren_list == ["111111118", "222222226", "333333334", "555555556"]
