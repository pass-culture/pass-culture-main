from pcapi import settings
from pcapi.routes.adage import security
from pcapi.routes.adage.v1 import blueprint


@blueprint.adage_v1.route("/test", methods=["GET"])
@security.adage_api_key_required
def security_endpoint():
    return "OK", 204


def test_with_correct_http_header(client):
    headers = {"Authorization": f"Bearer {settings.EAC_API_KEY}"}
    response = client.get("/adage/v1/test", headers=headers)
    assert response.status_code == 204


def test_with_incorrect_http_header(client):
    headers = {"Authorization": "Bearer incorrect-value"}
    response = client.get("/adage/v1/test", headers=headers)
    assert response.status_code == 401
    assert response.json == {"Authorization": ["Wrong API key"]}


def test_without_http_header(client):
    response = client.get("/adage/v1/test")
    assert response.status_code == 401
    assert response.json == {"Authorization": ["Missing API key"]}
