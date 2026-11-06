import pytest

from pcapi.core import testing
from pcapi.core.nature_format_domain.nature_format_domain import FieldEnum
from pcapi.core.nature_format_domain.nature_format_domain import FormatEnum
from pcapi.core.nature_format_domain.nature_format_domain import NatureEnum
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


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize(
    "nature,format,capabilities,mandatory_fields",
    [
        (
            "BIEN",
            "CD_VINYLE",
            ["TITLE", "DESCRIPTION", "IMAGE", "GENRE_MUSIC", "PERFORMER", "EAN"],
            ["TITLE", "GENRE_MUSIC"],
        ),
        ("BIEN", "DVD_BLU_RAY", ["TITLE", "DESCRIPTION", "IMAGE", "EAN"], ["TITLE"]),
        ("BIEN", "INSTRUMENT_DE_MUSIQUE", ["TITLE", "DESCRIPTION", "IMAGE", "EAN"], ["TITLE"]),
        (
            "BIEN",
            "LIVRE_PAPIER",
            ["TITLE", "DESCRIPTION", "IMAGE", "EAN", "AUTHOR", "ACCESSIBILITY_ATTRIBUTE_LARGE_PRINT"],
            ["TITLE"],
        ),
        ("BIEN", "MATERIEL_ARTS_CREATIFS", ["TITLE", "DESCRIPTION", "IMAGE", "EAN"], ["TITLE"]),
        ("CARTE_ABONNEMENT", "LIVRE_PAPIER", [], []),
        ("EVENEMENT", "LIVRE_PAPIER", [], []),
        ("NUMERIQUE", "LIVRE_PAPIER", [], []),
    ],
)
def test_get_capabilities(client, nature, format, capabilities, mandatory_fields):
    user = users_factories.ProFactory()
    client = client.with_session_auth(user.email)

    with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
        response = client.get("/capabilities", params={"nature": nature, "format": format})

    assert response.status_code == 200
    assert response.json == {"capabilities": capabilities, "mandatoryFields": mandatory_fields}


@pytest.mark.usefixtures("db_session")
def test_get_capabilities_with_mandatory_fields(client, mocker):
    user = users_factories.ProFactory()
    client = client.with_session_auth(user.email)
    get_mandatory_fields = mocker.patch(
        "pcapi.core.nature_format_domain.nature_format_domain.get_mandatory_fields",
        return_value=[FieldEnum.TITLE, FieldEnum.EAN],
    )

    with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
        response = client.get("/capabilities", params={"nature": "BIEN", "format": "LIVRE_PAPIER"})

    assert response.status_code == 200
    assert response.json["mandatoryFields"] == ["TITLE", "EAN"]
    get_mandatory_fields.assert_called_once_with(nature=NatureEnum.BIEN, format=FormatEnum.LIVRE_PAPIER)
