from unittest.mock import patch

import pytest

import pcapi.core.offerers.structure_signup_api as structure_signup
from pcapi.connectors.entreprise import exceptions as sirene_exceptions

from tests.connectors import api_entreprise_test_data


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    collective_message = {"importanceLevel": "INFO", "content": "COLLECTIVE"}
    unusual_ape_code = {"importanceLevel": "ALERT", "content": "UNUSUAL_APE_CODE"}
    bookstore_message = {"importanceLevel": "ALERT", "content": "BOOKSTORE"}

    def test_standard_case(self, client):
        """structure sans message specifique et sans document supplementaire"""
        data = {
            "siret": "11151111111111",
            "isOpenToPublic": True,
            "targets": ["INDIVIDUAL"],
            "activity": "MUSEUM",
        }
        response = client.post("/structure/signup_simulation", json=data)
        assert response.json["eligibilityDocuments"] == [
            structure_signup.EligibilityDocuments.WEBSITE.name,
            structure_signup.EligibilityDocuments.DESCRIPTION.name,
        ]
        assert response.json["messages"] == []

    def test_complex_case(self, client):
        """librairie uninomiale a code ape suspect, qui fait du collectf"""
        data = {
            "siret": "11111111111111",
            "isOpenToPublic": True,
            "targets": ["COLLECTIVE", "INDIVIDUAL"],
            "activity": "BOOKSTORE",
        }
        response = client.post("/structure/signup_simulation", json=data)
        assert response.json["eligibilityDocuments"] == [
            structure_signup.EligibilityDocuments.WEBSITE.name,
            structure_signup.EligibilityDocuments.DESCRIPTION.name,
            structure_signup.EligibilityDocuments.RESUME_OR_PORTFOLIO.name,
            structure_signup.EligibilityDocuments.DIPLOMAS.name,
            structure_signup.EligibilityDocuments.SHOP_PICTURES.name,
        ]
        assert self.bookstore_message in response.json["messages"]
        assert self.unusual_ape_code in response.json["messages"]
        assert self.collective_message in response.json["messages"]


class Returns400Test:
    @patch(
        "pcapi.connectors.entreprise.api.get_siret_open_data", side_effect=sirene_exceptions.UnknownEntityException()
    )
    def test_siret_unknown(self, _get_siret_open_data_mock, client):
        data = {
            "siret": "11111111111111",
            "isOpenToPublic": True,
            "targets": ["COLLECTIVE", "INDIVIDUAL"],
            "activity": "BOOKSTORE",
        }
        response = client.post("/structure/signup_simulation", json=data)

        assert response.status_code == 400

    @pytest.mark.settings(ENTREPRISE_BACKEND="pcapi.connectors.entreprise.backends.api_entreprise.EntrepriseBackend")
    def test_inactive_siret(self, requests_mock, client):
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
        response = client.post("/structure/signup_simulation", json=data)

        assert response.status_code == 400
        assert response.json == {"global": ["Ce SIRET n'est pas actif."]}

    def test_no_open_to_public(self, client):
        data = {
            "siret": "11111111111111",
            "targets": ["INDIVIDUAL"],
            "activity": "BOOKSTORE",
        }
        response = client.post("/structure/signup_simulation", json=data)
        assert response.status_code == 400
        assert response.json == {"isOpenToPublic": ["Ce champ est obligatoire"]}

    def test_no_target(self, client):
        data = {
            "siret": "11111111111111",
            "isOpenToPublic": True,
            "targets": [],
            "activity": "BOOKSTORE",
        }
        response = client.post("/structure/signup_simulation", json=data)
        assert response.status_code == 400
        assert response.json == {"targets": ["Cette liste doit avoir une taille minimum de 1"]}

    def test_no_activity(self, client):
        data = {
            "siret": "11111111111111",
            "isOpenToPublic": True,
            "targets": ["COLLECTIVE", "INDIVIDUAL"],
            "activity": None,
        }
        response = client.post("/structure/signup_simulation", json=data)
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


class Returns500Test:
    @patch("pcapi.connectors.entreprise.api.get_siret_open_data", side_effect=sirene_exceptions.ApiException())
    def test_sirene_api_ko(self, _get_siret_open_data_mock, client):
        data = {
            "siret": "11151111111111",
            "isOpenToPublic": True,
            "targets": ["INDIVIDUAL"],
            "activity": "MUSEUM",
        }
        response = client.post("/structure/signup_simulation", json=data)

        assert response.status_code == 500
