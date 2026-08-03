import copy
from unittest.mock import patch

import pytest

from pcapi.connectors.entreprise import exceptions as sirene_exceptions
from pcapi.core.offerers.structure_signup_api import EligibilityDocument
from pcapi.core.offerers.structure_signup_api import SignupSimulationMessageLevel
from pcapi.core.offerers.structure_signup_api import SignupSimulationMessageType
from pcapi.models.api_errors import OBJECT_NOT_FOUND_ERROR_MESSAGE

from tests.conftest import TestClient
from tests.connectors import api_entreprise_test_data


pytestmark = pytest.mark.usefixtures("db_session")


VALID_SIRET = "44265836100021"


@pytest.mark.features(WIP_PRE_SIGNUP_SIMULATION=True)
class Returns200Test:
    def test_standard_case(self, client: TestClient):
        """structure with default documents and no messages"""
        data = {
            "siret": VALID_SIRET,
            "isOpenToPublic": True,
            "targets": ["INDIVIDUAL"],
            "activity": "MUSEUM",
        }
        response = client.post("/structure/simulate-signup", json=data)

        assert response.status_code == 200
        assert response.json == {
            "eligibilityDocuments": [
                EligibilityDocument.WEBSITE.name,
                EligibilityDocument.DESCRIPTION.name,
            ],
            "messages": [],
        }

    def test_complex_case(self, client: TestClient):
        """single member bookstore with ape code not in whitelist, and collective target"""
        data = {
            "siret": "11141111122213",
            "isOpenToPublic": True,
            "targets": ["COLLECTIVE", "INDIVIDUAL"],
            "activity": "BOOKSTORE",
        }
        response = client.post("/structure/simulate-signup", json=data)

        assert response.status_code == 200
        assert response.json == {
            "eligibilityDocuments": [
                EligibilityDocument.WEBSITE.name,
                EligibilityDocument.DESCRIPTION.name,
                EligibilityDocument.RESUME_OR_PORTFOLIO.name,
                EligibilityDocument.DIPLOMAS.name,
                EligibilityDocument.SHOP_PICTURES.name,
            ],
            "messages": [
                {"level": SignupSimulationMessageLevel.INFO.name, "type": SignupSimulationMessageType.COLLECTIVE.name},
                {
                    "level": SignupSimulationMessageLevel.ALERT.name,
                    "type": SignupSimulationMessageType.UNUSUAL_APE_CODE.name,
                },
                {"level": SignupSimulationMessageLevel.ALERT.name, "type": SignupSimulationMessageType.BOOKSTORE.name},
            ],
        }


@pytest.mark.features(WIP_PRE_SIGNUP_SIMULATION=True)
class Returns400Test:
    @patch(
        "pcapi.connectors.entreprise.api.get_siret_open_data", side_effect=sirene_exceptions.UnknownEntityException()
    )
    def test_siret_unknown(self, _get_siret_open_data_mock, client: TestClient):
        data = {
            "siret": VALID_SIRET,
            "isOpenToPublic": True,
            "targets": ["COLLECTIVE", "INDIVIDUAL"],
            "activity": "BOOKSTORE",
        }
        response = client.post("/structure/simulate-signup", json=data)

        assert response.status_code == 400
        assert response.json == {"global": ["Le SIREN n’existe pas."]}

    @pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
    def test_inactive_siret(self, requests_mock, client: TestClient):
        siret = "77789988100026"

        requests_mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/diffusibles/{siret}",
            json=api_entreprise_test_data.RESPONSE_SIRET_INACTIVE_COMPANY,
        )
        data = {
            "siret": siret,
            "isOpenToPublic": True,
            "targets": ["COLLECTIVE", "INDIVIDUAL"],
            "activity": "BOOKSTORE",
        }
        response = client.post("/structure/simulate-signup", json=data)

        assert response.status_code == 400
        assert response.json == {"global": ["Ce SIRET n'est pas actif."]}

    @pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
    def test_siret_with_no_ape(self, requests_mock, client: TestClient):
        siret = "77789988100026"
        json = copy.deepcopy(api_entreprise_test_data.RESPONSE_SIRET_COMPANY)
        json["data"]["activite_principale"]["code"] = None

        requests_mock.get(
            f"https://entreprise.api.gouv.fr/v3/insee/sirene/etablissements/diffusibles/{siret}", json=json
        )
        data = {
            "siret": siret,
            "isOpenToPublic": True,
            "targets": ["COLLECTIVE", "INDIVIDUAL"],
            "activity": "BOOKSTORE",
        }
        response = client.post("/structure/simulate-signup", json=data)

        assert response.status_code == 400
        assert response.json == {"global": ["Impossible d'effectuer une simulation pour ce SIRET."]}

    def test_invalid_siret(self, client: TestClient):
        data = {
            "siret": "12345678912345",
            "isOpenToPublic": True,
            "targets": ["COLLECTIVE", "INDIVIDUAL"],
            "activity": "BOOKSTORE",
        }
        response = client.post("/structure/simulate-signup", json=data)

        assert response.status_code == 400
        assert response.json == {"siret": ["Le SIRET est invalide"]}

    def test_no_open_to_public(self, client: TestClient):
        data = {
            "siret": VALID_SIRET,
            "targets": ["INDIVIDUAL"],
            "activity": "BOOKSTORE",
        }
        response = client.post("/structure/simulate-signup", json=data)

        assert response.status_code == 400
        assert response.json == {"isOpenToPublic": ["Ce champ est obligatoire"]}

    def test_no_target(self, client: TestClient):
        data = {
            "siret": VALID_SIRET,
            "isOpenToPublic": True,
            "targets": [],
            "activity": "BOOKSTORE",
        }
        response = client.post("/structure/simulate-signup", json=data)

        assert response.status_code == 400
        assert response.json == {"targets": ["Cette liste doit avoir une taille minimum de 1"]}

    def test_no_activity(self, client: TestClient):
        data = {
            "siret": VALID_SIRET,
            "isOpenToPublic": True,
            "targets": ["COLLECTIVE", "INDIVIDUAL"],
            "activity": None,
        }
        response = client.post("/structure/simulate-signup", json=data)

        assert response.status_code == 400
        assert response.json == {
            "activity.enum[ActivityNotOpenToPublic]": [
                "Input should be 'ARTISTIC_COMPANY', 'ARTISTIC_PRACTICE', "
                "'CULTURAL_MEDIATION', 'FESTIVAL', 'HERITAGE_SITE', 'HIGHER_EDUCATION_INSTITUTION', 'MUNICIPALITY_CULTURAL_DEPARTMENT', 'OTHER', 'PRESS_OR_MEDIA', "
                "'PRODUCTION_OR_PROMOTION_COMPANY', 'PUBLISHING_HOUSE', 'RADIO_OR_MUSIC_STREAMING', 'SCIENTIFIC_CULTURE', "
                "'TELEVISION_OR_VIDEO_STREAMING' or 'TRAVELLING_CINEMA'",
            ],
            "activity.enum[ActivityOpenToPublic]": [
                "Input should be 'ART_GALLERY', 'ARTISTIC_PRACTICE', 'ARTS_CENTRE', "
                "'BOOKSTORE', 'CINEMA', 'COMMUNITY_CENTRE', 'CREATIVE_ARTS_STORE', "
                "'CULTURAL_CENTRE', 'DISTRIBUTION_STORE', 'FESTIVAL', 'HERITAGE_SITE', 'HIGHER_EDUCATION_INSTITUTION', "
                "'LIBRARY', 'MUSEUM', 'MUSIC_INSTRUMENT_STORE', 'OTHER', "
                "'PERFORMANCE_HALL', 'PUBLISHING_HOUSE', 'RECORD_STORE', 'SCIENTIFIC_CULTURE' or "
                "'TOURIST_INFORMATION_CENTRE'",
            ],
        }

    def test_duplicate_target(self, client: TestClient):
        data = {
            "siret": VALID_SIRET,
            "isOpenToPublic": True,
            "targets": ["COLLECTIVE", "COLLECTIVE"],
            "activity": "OTHER",
        }
        response = client.post("/structure/simulate-signup", json=data)

        assert response.status_code == 400
        assert response.json == {"targets": ["Une valeur est en doublon"]}

    def test_invalid_target(self, client: TestClient):
        data = {
            "siret": VALID_SIRET,
            "isOpenToPublic": True,
            "targets": ["bloup"],
            "activity": "OTHER",
        }
        response = client.post("/structure/simulate-signup", json=data)

        assert response.status_code == 400
        assert response.json == {"targets.0": ["Input should be 'COLLECTIVE' or 'INDIVIDUAL'"]}


class Returns404Test:
    @pytest.mark.features(WIP_PRE_SIGNUP_SIMULATION=False)
    def test_with_ff_off(self, client: TestClient):
        data = {
            "siret": VALID_SIRET,
            "isOpenToPublic": True,
            "targets": ["INDIVIDUAL"],
            "activity": "MUSEUM",
        }
        response = client.post("/structure/simulate-signup", json=data)

        assert response.status_code == 404
        assert response.json == {"global": [OBJECT_NOT_FOUND_ERROR_MESSAGE]}
