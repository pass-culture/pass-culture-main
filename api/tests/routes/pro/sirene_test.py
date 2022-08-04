from unittest import mock

from pcapi.connectors import sirene


def get_siren_raises(siren, with_address):
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
