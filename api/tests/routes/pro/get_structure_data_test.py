from unittest.mock import patch

import pytest

import pcapi.core.users.factories as users_factories
from pcapi import settings
from pcapi.connectors import api_adresse
from pcapi.connectors.entreprise import exceptions as sirene_exceptions
from pcapi.core.testing import assert_num_queries


GET_STRUCTURE_DATA_URL = "/structure/search/"
DIFFUSIBLE_SIRET = "12345678900001"
PARTIALLY_DIFFUSIBLE_SIRET = "92345678900001"
INACTIVE_SIRET = "12349978900001"
INVALID_SIRET = "123456789"


class Returns200Test:
    @pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.TestingBackend")
    def test_find_diffusible_structure_by_siret(self, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(pro.email)

        response = client.get(f"{GET_STRUCTURE_DATA_URL}{DIFFUSIBLE_SIRET}")

        assert response.status_code == 200
        found_structure = response.json
        assert found_structure.get("siret") == DIFFUSIBLE_SIRET
        assert found_structure.get("isDiffusible") is True
        assert found_structure.get("name") is not None
        assert found_structure.get("address") is not None

    @patch("pcapi.connectors.api_adresse.find_ban_address", side_effect=api_adresse.AdresseException())
    def test_find_diffusible_structure_by_siret_with_no_address(self, _find_ban_address_mock, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(pro.email)

        response = client.get(f"{GET_STRUCTURE_DATA_URL}{DIFFUSIBLE_SIRET}")

        assert response.status_code == 200
        found_structure = response.json
        assert found_structure.get("siret") == DIFFUSIBLE_SIRET
        assert found_structure.get("isDiffusible") is True
        assert found_structure.get("name") is not None
        assert found_structure.get("address") is None

    @pytest.mark.features(WIP_2025_SIGN_UP_PARTIALLY_DIFFUSIBLE=True)
    @pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.TestingBackend")
    def test_find_partially_diffusible_structure_by_siret(self, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(pro.email)

        response = client.get(f"{GET_STRUCTURE_DATA_URL}{PARTIALLY_DIFFUSIBLE_SIRET}")

        assert response.status_code == 200
        found_structure = response.json
        assert found_structure.get("siret") == PARTIALLY_DIFFUSIBLE_SIRET
        assert found_structure.get("isDiffusible") is False
        assert found_structure.get("name") is None
        assert found_structure.get("address") is not None
        assert found_structure.get("address").get("street") == "Adresse non diffusée"

    @pytest.mark.features(WIP_2025_SIGN_UP_PARTIALLY_DIFFUSIBLE=True)
    @patch("pcapi.connectors.api_adresse.find_ban_city", side_effect=api_adresse.AdresseException())
    def test_find_partially_diffusible_structure_by_siret_with_no_address(self, _find_ban_city_mock, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(pro.email)

        response = client.get(f"{GET_STRUCTURE_DATA_URL}{PARTIALLY_DIFFUSIBLE_SIRET}")

        assert response.status_code == 200
        found_structure = response.json
        assert found_structure.get("siret") == PARTIALLY_DIFFUSIBLE_SIRET
        assert found_structure.get("isDiffusible") is False
        assert found_structure.get("name") is None
        assert found_structure.get("address") is None


class Returns400Test:
    @pytest.mark.features(WIP_2025_SIGN_UP_PARTIALLY_DIFFUSIBLE=False)
    def test_search_partially_diffusible_structure(self, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(pro.email)

        response = client.get(f"{GET_STRUCTURE_DATA_URL}{PARTIALLY_DIFFUSIBLE_SIRET}")

        assert response.status_code == 400
        message = "Le propriétaire de ce SIRET s'oppose à la diffusion de ses données au public."
        assert response.json == {"global": [message]}

    def test_search_structure_by_invalid_siret(self, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(pro.email)

        response = client.get(f"{GET_STRUCTURE_DATA_URL}{INVALID_SIRET}")

        assert response.status_code == 400
        message = "Le format de ce SIREN ou SIRET est incorrect."
        assert response.json == {"global": [message]}

    def test_search_structure_by_pass_culture_siret(self, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(pro.email)

        response = client.get(f"{GET_STRUCTURE_DATA_URL}{settings.PASS_CULTURE_SIRET}")

        assert response.status_code == 400
        message = "Le format de ce SIREN ou SIRET est incorrect."
        assert response.json == {"global": [message]}

    def test_search_inactive_siret(self, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(pro.email)

        response = client.get(f"{GET_STRUCTURE_DATA_URL}{INACTIVE_SIRET}")

        assert response.status_code == 400
        message = "Ce SIRET n'est pas actif."
        assert response.json == {"global": [message]}

    @patch(
        "pcapi.connectors.entreprise.api.get_siret_open_data",
        side_effect=sirene_exceptions.UnknownEntityException(),
    )
    def test_search_unknown_siret(self, _get_siret_open_data_mock, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(pro.email)

        response = client.get(f"{GET_STRUCTURE_DATA_URL}{DIFFUSIBLE_SIRET}")

        assert response.status_code == 400
        message = "Le SIREN n’existe pas."
        assert response.json == {"global": [message]}


class Returns401Test:
    def test_unauthenticated_user(self, client):
        with assert_num_queries(0):
            response = client.get(f"{GET_STRUCTURE_DATA_URL}{DIFFUSIBLE_SIRET}")

        assert response.status_code == 401


class Returns500Test:
    @patch("pcapi.connectors.entreprise.api.get_siret_open_data", side_effect=sirene_exceptions.ApiUnavailable())
    def test_unavailable_data_source(self, _get_siret_open_data_mock, client):
        pro = users_factories.ProFactory()
        client = client.with_session_auth(pro.email)

        with assert_num_queries(2):
            response = client.get(f"{GET_STRUCTURE_DATA_URL}{DIFFUSIBLE_SIRET}")

        assert response.status_code == 500
        message = (
            "Les informations relatives à ce SIREN ou SIRET n'ont pas pu être vérifiées, veuillez réessayer plus tard."
        )
        assert response.json == {"global": [message]}
