from unittest import mock

import pytest

from pcapi.connectors import sirene
import pcapi.core.users.factories as users_factories


def get_siren_raises(siren, with_address):
    raise sirene.NonPublicDataException()


def get_siret_raises(siret):
    raise sirene.NonPublicDataException()


class GetSirenTest:
    def test_siren_ok(self, client):
        siren = "123456789"
        response = client.get(f"/sirene/siren/{siren}")
        assert response.status_code == 200
        assert response.json == {
            "siren": siren,
            "name": "MINISTERE DE LA CULTURE",
            "address": {
                "street": "3 RUE DE VALOIS",
                "postalCode": "75001",
                "city": "Paris",
            },
        }

    @mock.patch("pcapi.connectors.sirene.get_siren", get_siren_raises)
    def test_siren_error(self, client):
        siren = "123456789"
        response = client.get(f"/sirene/siren/{siren}")
        assert response.status_code == 400
        msg = "Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles."
        assert response.json == {"global": [msg]}


class GetSiretTest:
    @pytest.mark.usefixtures("db_session")
    def test_siret_ok(self, client):
        pro = users_factories.ProFactory()
        siret = "12345678900001"

        client = client.with_session_auth(pro.email)
        response = client.get(f"/sirene/siret/{siret}")

        assert response.status_code == 200
        assert response.json == {
            "siret": siret,
            "name": "MINISTERE DE LA CULTURE",
            "address": {
                "street": "3 RUE DE VALOIS",
                "postalCode": "75001",
                "city": "Paris",
            },
        }

    @pytest.mark.usefixtures("db_session")
    @mock.patch("pcapi.connectors.sirene.get_siret", get_siret_raises)
    def test_siret_error(self, client):
        pro = users_factories.ProFactory()
        siret = "12345678900001"

        client = client.with_session_auth(pro.email)
        response = client.get(f"/sirene/siret/{siret}")

        assert response.status_code == 400
        msg = "Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles."
        assert response.json == {"global": [msg]}

    def test_unauthenticated(self, client):
        siret = "12345678900001"
        response = client.get(f"/sirene/siret/{siret}")
        assert response.status_code == 401
