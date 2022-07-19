from typing import Any

import pytest

import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
def test_patch_user_identity(client: Any) -> None:
    user = users_factories.ProFactory(firstName="jean", lastName="Kadre")
    form_data = {"firstName": "Axel", "lastName": "Ere"}
    client = client.with_session_auth(user.email)
    response = client.patch("/users/identity", json=form_data)

    assert response.status_code == 200
    assert response.json == {"firstName": "Axel", "lastName": "Ere"}
    assert user.firstName == "Axel"
    assert user.lastName == "Ere"


@pytest.mark.usefixtures("db_session")
def test_patch_user_identity_missing_fields(client: Any) -> None:
    user = users_factories.ProFactory(firstName="jean", lastName="Kadre")

    client = client.with_session_auth(user.email)
    response = client.patch("/users/identity", json={})

    assert response.status_code == 400
    assert user.firstName == "jean"
    assert user.lastName == "Kadre"


@pytest.mark.usefixtures("db_session")
def test_patch_user_identity_without_auth(client: Any) -> None:
    user = users_factories.ProFactory(firstName="jean", lastName="Tours")
    form_data = {"firstName": "Barrack", "lastName": "Afrit"}
    response = client.patch("/users/identity", json=form_data)

    assert response.status_code == 401
    assert user.firstName == "jean"
    assert user.lastName == "Tours"
