import pytest

from pcapi.core import testing
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
def test_get_nature_format_domain(client):
    user = users_factories.ProFactory()
    client = client.with_session_auth(user.email)

    with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
        response = client.get("/nature-format-domain")

    assert response.status_code == 200
    assert response.json == [
        {
            "name": "BIEN",
            "label": "Biens",
            "formats": [
                {"format": "CD_VINYLE", "label": "CD, Vinyle"},
                {"format": "DVD_BLU_RAY", "label": "DVD, Blu-ray"},
                {"format": "INSTRUMENT_DE_MUSIQUE", "label": "Instrument de musique"},
                {"format": "LIVRE_PAPIER", "label": "Livre papier"},
                {"format": "MATERIEL_ARTS_CREATIFS", "label": "Matériel arts créatifs"},
            ],
        },
        {
            "name": "CARTE_ABONNEMENT",
            "label": "Cartes d'abonnement",
            "formats": [],
        },
        {
            "name": "EVENEMENT",
            "label": "Événements",
            "formats": [],
        },
        {
            "name": "NUMERIQUE",
            "label": "Offre numérique",
            "formats": [],
        },
    ]


@pytest.mark.usefixtures("db_session")
def test_get_nature_format_domain_unauthenticated(client):
    with testing.assert_num_queries(0):
        response = client.get("/nature-format-domain")

    assert response.status_code == 401
    assert response.json == {"global": ["Authentification nécessaire"]}
