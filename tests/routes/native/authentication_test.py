from unittest.mock import patch

import pytest

from pcapi.core.users import factories as user_factories
from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


def test_user_logs_in_and_refreshes_token(app):
    data = {'identifier': 'user@test.com', 'password': user_factories.DEFAULT_PASSWORD}
    user_factories.UserFactory(email=data['identifier'], password=data['password'])
    test_client = TestClient(app.test_client())

    # Get the refresh and access token
    response = test_client.post('/native/v1/signin', json=data)
    assert response.status_code == 200
    assert response.json['refresh_token']
    assert response.json['access_token']

    refresh_token = response.json['refresh_token']
    access_token = response.json['access_token']

    # Ensure the access token is valid
    test_client.auth_header = {
        'Authorization': f'Bearer {access_token}'
    }
    response = test_client.get('/native/v1/protected')
    assert response.status_code == 200

    # Ensure the refresh token can generate a new access token
    test_client.auth_header = {
        'Authorization': f'Bearer {refresh_token}'
    }
    response = test_client.post('/native/v1/refresh_access_token', json={})
    assert response.status_code == 200, response.json
    assert response.json['access_token']
    access_token = response.json['access_token']

    # Ensure the new access token is valid
    test_client.auth_header = {
        'Authorization': f'Bearer {access_token}'
    }
    response = test_client.get('/native/v1/protected')
    assert response.status_code == 200


def test_user_logs_in_with_wrong_password(app):
    data = {'identifier': 'user@test.com', 'password': user_factories.DEFAULT_PASSWORD}
    user_factories.UserFactory(email=data['identifier'], password=data['password'])
    test_client = TestClient(app.test_client())

    # signin with invalid password and ensures the result messsage is generic
    data['password'] = data['password'][:-2]
    response = test_client.post('/native/v1/signin', json=data)
    assert response.status_code == 400
    assert response.json == {'general': ['Identifiant ou Mot de passe incorrect']}


def test_unknown_user_logs_in(app):
    data = {'identifier': 'user@test.com', 'password': user_factories.DEFAULT_PASSWORD}
    test_client = TestClient(app.test_client())

    # signin with invalid password and ensures the result messsage is generic
    response = test_client.post('/native/v1/signin', json=data)
    assert response.status_code == 400
    assert response.json == {'general': ['Identifiant ou Mot de passe incorrect']}


def test_user_logs_in_with_missing_fields(app):
    test_client = TestClient(app.test_client())

    response = test_client.post('/native/v1/signin', json={})
    assert response.status_code == 400
    assert response.json == {
        'identifier': ['Ce champ est obligatoire'],
        'password': ['Ce champ est obligatoire'],
    }
