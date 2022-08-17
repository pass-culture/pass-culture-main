from typing import Any

import pytest

import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
def test_patch_user_identity(client: Any) -> None:
    user = users_factories.ProFactory(phoneNumber="0123456789")
    form_data = {"phoneNumber": "0678961233"}
    client = client.with_session_auth(user.email)
    response = client.patch("/users/phone", json=form_data)

    assert response.status_code == 200
    assert response.json == {"phoneNumber": "+33678961233"}
    assert user.phoneNumber == "+33678961233"


@pytest.mark.usefixtures("db_session")
def test_patch_user_identity_missing_fields(client: Any) -> None:
    user = users_factories.ProFactory(phoneNumber="0123456789")

    client = client.with_session_auth(user.email)
    response = client.patch("/users/phone", json={})

    assert response.status_code == 400
    assert user.phoneNumber == "+33123456789"


@pytest.mark.usefixtures("db_session")
def test_patch_user_identity_without_auth(client: Any) -> None:
    user = users_factories.ProFactory(phoneNumber="0123456789")
    form_data = {"firstName": "Barrack", "lastName": "Afrit"}
    response = client.patch("/users/phone", json=form_data)

    assert response.status_code == 401
    assert user.phoneNumber == "+33123456789"
