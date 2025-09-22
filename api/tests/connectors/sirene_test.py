import datetime

import pytest
import requests_mock

from pcapi.connectors.entreprise import exceptions
from pcapi.connectors.entreprise import sirene

from . import sirene_test_data


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
