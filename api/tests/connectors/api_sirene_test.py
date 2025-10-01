import datetime

import pytest
import requests_mock

from pcapi.connectors import api_sirene

from . import api_sirene_test_data


@pytest.mark.parametrize(
    "status_code,expected_exception",
    [
        (301, api_sirene.UnknownEntityException),
        (400, api_sirene.InvalidFormatException),
        (403, api_sirene.NonPublicDataException),
        (404, api_sirene.UnknownEntityException),
        (500, api_sirene.ApiException),
        (503, api_sirene.ApiException),
    ],
)
@pytest.mark.settings(SIRENE_BACKEND="pcapi.connectors.api_sirene.InseeBackend")
def test_error_handling(status_code, expected_exception):
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://api.insee.fr/api-sirene/3.11/siren",
            status_code=status_code,
        )
        with pytest.raises(expected_exception):
            api_sirene.get_siren_closed_at_date(datetime.date(2025, 1, 21))


@pytest.mark.settings(SIRENE_BACKEND="pcapi.connectors.api_sirene.InseeBackend")
def test_error_handling_on_non_json_response():
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://api.insee.fr/api-sirene/3.11/siren",
            status_code=200,
            text="non-JSON content",
        )
        with pytest.raises(api_sirene.ApiException):
            api_sirene.get_siren_closed_at_date(datetime.date(2025, 1, 21))


@pytest.mark.settings(SIRENE_BACKEND="pcapi.connectors.api_sirene.InseeBackend")
def test_get_siren_closed_at_date():
    with requests_mock.Mocker() as mock:
        mock.get(
            "https://api.insee.fr/api-sirene/3.11/siren?q=(dateDernierTraitementUniteLegale:2025-01-21+AND+periode(etatAdministratifUniteLegale:C+AND+changementEtatAdministratifUniteLegale:true))+OR+periode(etatAdministratifUniteLegale:C+AND+changementEtatAdministratifUniteLegale:true+AND+dateDebut:2025-01-21)&champs=siren,dateDebut,dateFin,etatAdministratifUniteLegale&curseur=*&nombre=1000",
            status_code=200,
            json=api_sirene_test_data.RESPONSE_CLOSED_SIREN_PAGE1,
        )
        mock.get(
            "https://api.insee.fr/api-sirene/3.11/siren?q=(dateDernierTraitementUniteLegale:2025-01-21+AND+periode(etatAdministratifUniteLegale:C+AND+changementEtatAdministratifUniteLegale:true))+OR+periode(etatAdministratifUniteLegale:C+AND+changementEtatAdministratifUniteLegale:true+AND+dateDebut:2025-01-21)&champs=siren,dateDebut,dateFin,etatAdministratifUniteLegale&curseur=AoEpODg5Mjg4Mzc5&nombre=1000",
            status_code=200,
            json=api_sirene_test_data.RESPONSE_CLOSED_SIREN_PAGE2,
        )
        siren_list = api_sirene.get_siren_closed_at_date(datetime.date(2025, 1, 21))

    assert siren_list == [
        {"siren": "222222226", "closure_date": datetime.date(2024, 12, 31)},
        {"siren": "555555556", "closure_date": datetime.date(2024, 1, 1)},
        {"siren": "666666667", "closure_date": datetime.date(2024, 1, 1)},
    ]
