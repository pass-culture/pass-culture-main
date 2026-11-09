import pytest

from pcapi.core.users import factories as users_factories


@pytest.mark.parametrize(
    ("nature", "format", "expected_capabilities", "expected_mandatory_fields"),
    [
        (
            "BIEN",
            "CD",
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
        ("CARTE_ABONNEMENT", "CD", [], []),
        ("EVENEMENT", "CD", [], []),
        ("NUMERIQUE", "CD", [], []),
    ],
)
@pytest.mark.usefixtures("db_session")
def test_get_capabilities(client, nature, format, expected_capabilities, expected_mandatory_fields):
    user = users_factories.ProFactory()
    client = client.with_session_auth(user.email)

    response = client.get(f"/capabilities?nature={nature}&format={format}")

    assert response.status_code == 200
    assert response.json == {
        "capabilities": expected_capabilities,
        "mandatoryFields": expected_mandatory_fields,
    }
