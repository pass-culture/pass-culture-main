import pytest

from pcapi.core.users import factories as users_factories


@pytest.mark.parametrize(
    ("nature", "format", "expected_capabilities"),
    [
        ("BIEN", "CD_VINYLE", ["TITLE", "DESCRIPTION", "IMAGE", "GTL_ID", "EAN", "PERFORMER"]),
        ("BIEN", "DVD_BLU_RAY", ["TITLE", "DESCRIPTION", "IMAGE", "GTL_ID", "EAN"]),
        ("BIEN", "INSTRUMENT_DE_MUSIQUE", ["TITLE", "DESCRIPTION", "IMAGE", "EAN"]),
        (
            "BIEN",
            "LIVRE_PAPIER",
            ["TITLE", "DESCRIPTION", "IMAGE", "EAN", "GTL_ID", "AUTHOR", "ACCESSIBILITY_ATTRIBUTE_LARGE_PRINT"],
        ),
        ("BIEN", "MATERIEL_ARTS_CREATIFS", ["TITLE", "DESCRIPTION", "IMAGE", "EAN"]),
        ("CARTE_ABONNEMENT", "CD_VINYLE", []),
        ("EVENEMENT", "CD_VINYLE", []),
        ("NUMERIQUE", "CD_VINYLE", []),
    ],
)
@pytest.mark.usefixtures("db_session")
def test_get_capabilities(client, nature, format, expected_capabilities):
    user = users_factories.ProFactory()
    client = client.with_session_auth(user.email)

    response = client.get(f"/capabilities?nature={nature}&format={format}")

    assert response.status_code == 200
    assert response.json == {"capabilities": expected_capabilities}
