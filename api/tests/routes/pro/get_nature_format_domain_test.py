import pytest

from pcapi.core import testing
from pcapi.core.nature_format_domain import nature_format_domain
from pcapi.core.users import factories as users_factories


@pytest.mark.usefixtures("db_session")
def test_get_nature_format_domain(client):
    user = users_factories.ProFactory()
    client = client.with_session_auth(user.email)

    with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
        response = client.get("/nature-format-domain")

    assert response.status_code == 200
    natures_by_name = {nature["nature"]: nature for nature in response.json}
    formats_by_nature = {
        nature_name: {format_["format"]: format_ for format_ in nature["formats"]}
        for nature_name, nature in natures_by_name.items()
    }

    assert set(natures_by_name) == {nature.value for nature in nature_format_domain.NatureEnum}
    assert formats_by_nature["BIEN"]["CD"]["domains"] == []
    assert formats_by_nature["NUMERIQUE"]["MEDIA"] == {
        "format": "MEDIA",
        "label": "Média",
        "domains": [],
    }

    expected_domains = [
        {"domain": "ART_VISUEL", "label": "Art visuel"},
        {"domain": "BIBLIOTHEQUE_MEDIATHEQUE", "label": "Bibliothèque, Médiathèque"},
        {"domain": "CINEMA", "label": "Cinéma"},
        {"domain": "CIRQUE_ARTS_RUE", "label": "Cirque et Arts de la rue"},
        {"domain": "COMEDIE_MUSICALE", "label": "Comédie musicale"},
        {"domain": "CULTURE_SCIENTIFIQUE", "label": "Culture scientifique"},
        {"domain": "DANSE", "label": "Danse"},
        {"domain": "JEUX_VIDEO", "label": "Jeux vidéo"},
        {"domain": "LITTERATURE", "label": "Littérature"},
        {"domain": "MEDIA_PRESSE_RADIO", "label": "Média, Presse, Radio"},
        {"domain": "MEDIA_PRESSE_RADIO_EN_LIGNE", "label": "Média, Presse, Radio en ligne"},
        {"domain": "MULTI_DOMAINES_CARTE_JEUNE", "label": "Multi-domaines (carte jeune)"},
        {"domain": "MUSEE_PATRIMOINE_ARCHITECTURE", "label": "Musée, Patrimoine, Architecture"},
        {"domain": "MUSIQUE", "label": "Musique"},
        {"domain": "OPERA", "label": "Opéra"},
        {"domain": "STAND_UP", "label": "Stand up"},
        {"domain": "STREAMING_MUSIQUE", "label": "Streaming de musique"},
        {"domain": "THEATRE", "label": "Théâtre"},
        {"domain": "VOD", "label": "Vidéo à la demande"},
    ]
    assert formats_by_nature["CARTE_ABONNEMENT"]["CARTE"]["domains"] == expected_domains
    assert formats_by_nature["CARTE_ABONNEMENT"]["ABONNEMENT"]["domains"] == expected_domains


@pytest.mark.usefixtures("db_session")
def test_get_nature_format_domain_unauthenticated(client):
    with testing.assert_num_queries(0):
        response = client.get("/nature-format-domain")

    assert response.status_code == 401
    assert response.json == {"global": ["Authentification nécessaire"]}


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize(
    "nature,format,capabilities,mandatory_fields",
    [
        (
            "BIEN",
            "CD",
            ["GENRE_MUSIC", "PERFORMER"],
            ["GENRE_MUSIC"],
        ),
        (
            "BIEN",
            "VINYLE",
            ["GENRE_MUSIC", "PERFORMER"],
            ["GENRE_MUSIC"],
        ),
        ("BIEN", "DVD_BLU_RAY", [], []),
        ("BIEN", "INSTRUMENT_DE_MUSIQUE", [], []),
        (
            "BIEN",
            "LIVRE_PAPIER",
            ["AUTHOR", "ACCESSIBILITY_ATTRIBUTE_LARGE_PRINT"],
            [],
        ),
        ("BIEN", "MATERIEL_ARTS_CREATIFS", [], []),
        ("CARTE_ABONNEMENT", "LIVRE_PAPIER", [], []),
        ("EVENEMENT", "LIVRE_PAPIER", [], []),
        ("NUMERIQUE", "LIVRE_PAPIER", [], []),
    ],
)
def test_get_capabilities(client, nature, format, capabilities, mandatory_fields):
    if nature == "BIEN":
        capabilities = [
            "BOOKING_LIMIT",
            "BOOKING_OPENING_DATE",
            "COMPLEMENTARY_INFO",
            "EMAIL_NOTIFICATION",
            "IMAGE",
            "NO_CREDIT_LINK",
            "PRICE",
            "PROGRAM_PUBLICATION",
            "ACCESSIBILITY_VENUE",
            "COUNTERMARK",
            "DESCRIPTION",
            "EAN",
            "LOCATION",
            "PICKUP_30_DAYS",
            "STOCK",
            "TITLE_BIEN",
        ] + capabilities
        mandatory_fields = ["PRICE", "TITLE", "LOCATION", "PICKUP_30_DAYS", "STOCK"] + mandatory_fields

    user = users_factories.ProFactory()
    client = client.with_session_auth(user.email)

    with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
        response = client.get("/capabilities", params={"nature": nature, "format": format})

    assert response.status_code == 200
    assert response.json == {"capabilities": capabilities, "mandatoryFields": mandatory_fields}
