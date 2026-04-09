from pcapi import settings
from pcapi.routes.adage import security
from pcapi.routes.adage.v1 import blueprint
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.serialization.decorator import spectree_serialize


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


class QueryModel(HttpQueryParamsModel):
    field: int


@blueprint.adage_v1.route("/test-with-validation", methods=["GET"])
@security.adage_api_key_required
@spectree_serialize(api=blueprint.api, on_success_status=204)
def security_with_validation_endpoint(query: QueryModel):
    return "OK", 204


def test_with_validation_error_no_header(client):
    response = client.get("/adage/v1/test-with-validation?field=aaa")

    assert response.status_code == 401
    assert response.json == {"Authorization": ["Missing API key"]}


def test_with_validation_error_with_header(client):
    headers = {"Authorization": f"Bearer {settings.EAC_API_KEY}"}
    response = client.get("/adage/v1/test-with-validation?field=aaa", headers=headers)

    assert response.status_code == 400
    assert response.json == {"field": ["Saisissez un entier valide"]}


def test_with_validation_with_header(client):
    headers = {"Authorization": f"Bearer {settings.EAC_API_KEY}"}
    response = client.get("/adage/v1/test-with-validation?field=12", headers=headers)

    assert response.status_code == 204
