import copy
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.connectors.entreprise import exceptions as sirene_exceptions
from pcapi.core.mails import testing as mails_testing
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE

from tests.conftest import TestClient
from tests.connectors import api_entreprise_test_data


pytestmark = pytest.mark.usefixtures("db_session")

URL = "/structure/summarise-signup"
VALID_SIRET = "44285836100029"
VALID_PAYLOAD = {
    "email": "test@example.com",
    "siret": VALID_SIRET,
    "isOpenToPublic": True,
    "targets": ["INDIVIDUAL"],
    "activity": "MUSEUM",
}


@pytest.mark.features(WIP_PRE_SIGNUP_SIMULATION=True)
class Returns200Test:
    def test_standard_case(self, client: TestClient):
        response = client.post(URL, json=VALID_PAYLOAD)

        assert response.status_code == 204
        assert len(mails_testing.outbox) == 1

        assert mails_testing.outbox[0]["To"] == "test@example.com"
        assert (
            mails_testing.outbox[0]["params"]["SIGNUP_LINK"]
            == f"http://localhost:3001/inscription/compte/creation?siret={VALID_SIRET}&isOpenToPublic=true&targets=INDIVIDUAL&activity=MUSEUM"
        )
        assert mails_testing.outbox[0]["params"]["ELIGIBILITY_DOCUMENTS"] == ["WEBSITE"]


@pytest.mark.features(WIP_PRE_SIGNUP_SIMULATION=True)
class Returns400Test:
    @patch(
        "pcapi.connectors.entreprise.api.get_siret_open_data", side_effect=sirene_exceptions.UnknownEntityException()
    )
    def test_siret_unknown(self, get_siret_open_data_mock: MagicMock, client: TestClient):
        response = client.post(URL, json=VALID_PAYLOAD)

        assert response.status_code == 400
        assert response.json == {"global": ["Le SIREN n’existe pas."]}

        get_siret_open_data_mock.assert_called_once_with(VALID_SIRET)

    @pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
    def test_inactive_siret(self, requests_mock, client: TestClient):
        requests_mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/diffusibles/{VALID_SIRET}",
            json=api_entreprise_test_data.RESPONSE_SIRET_INACTIVE_COMPANY,
        )

        response = client.post(URL, json=VALID_PAYLOAD)

        assert response.status_code == 400
        assert response.json == {"global": ["Ce SIRET n'est pas actif."]}

    @pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
    def test_siret_with_no_ape(self, requests_mock, client: TestClient):
        json = copy.deepcopy(api_entreprise_test_data.RESPONSE_SIRET_COMPANY)
        json["data"]["activite_principale"]["code"] = None
        requests_mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/diffusibles/{VALID_SIRET}", json=json
        )

        response = client.post(URL, json=VALID_PAYLOAD)

        assert response.status_code == 400
        assert response.json == {"global": ["Impossible d'effectuer une simulation pour ce SIRET."]}

    def test_invalid_siret(self, client: TestClient):
        data = {
            **VALID_PAYLOAD,
            "siret": "12345678912345",
        }
        response = client.post(URL, json=data)

        assert response.status_code == 400
        assert response.json == {"siret": ["Le SIRET est invalide"]}

    def test_duplicate_target(self, client: TestClient):
        data = {
            **VALID_PAYLOAD,
            "targets": ["COLLECTIVE", "COLLECTIVE"],
        }
        response = client.post(URL, json=data)

        assert response.status_code == 400
        assert response.json == {"targets": ["Une valeur est en doublon"]}

    def test_invalid_target(self, client: TestClient):
        data = {
            **VALID_PAYLOAD,
            "targets": ["bloup"],
        }
        response = client.post(URL, json=data)

        assert response.status_code == 400
        assert response.json == {"targets.0": ["Input should be 'COLLECTIVE' or 'INDIVIDUAL'"]}


class Returns404Test:
    @pytest.mark.features(WIP_PRE_SIGNUP_SIMULATION=False)
    def test_with_ff_off(self, client: TestClient):
        response = client.post(URL, json=VALID_PAYLOAD)

        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}
