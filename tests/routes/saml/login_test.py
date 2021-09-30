import pytest


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_educonnect_login(client):
    response = client.get("/saml/educonnect/login")
    assert response.status_code == 302
    assert response.location.startswith("https://pr4.educonnect.phm.education.gouv.fr/idp")
