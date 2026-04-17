import pytest

from pcapi.core.history import models as history_models
from pcapi.core.users import factories as users_factories

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


def test_patch_user_phone(client: TestClient) -> None:
    user = users_factories.ProFactory(phoneNumber="0123456789")
    form_data = {"phoneNumber": "0678961233"}
    client = client.with_session_auth(user.email)
    response = client.patch("/users/phone", json=form_data)

    assert response.status_code == 200
    assert response.json == {"phoneNumber": "+33678961233"}
    assert user.phoneNumber == "+33678961233"

    assert len(user.action_history) == 1
    assert user.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
    assert user.action_history[0].user == user
    assert user.action_history[0].extraData["modified_info"] == {
        "phoneNumber": {"new_info": "+33678961233", "old_info": "+33123456789"},
    }


def test_patch_user_phone_invalid(client: TestClient) -> None:
    user = users_factories.ProFactory(phoneNumber="0123456789")

    form_data = {"phoneNumber": "78961233"}
    client = client.with_session_auth(user.email)
    response = client.patch("/users/phone", json=form_data)

    assert response.status_code == 400
    assert response.json == {"phoneNumber": ["Numéro de téléphone invalide"]}
    assert user.phoneNumber == "+33123456789"
    assert len(user.action_history) == 0


def test_patch_user_phone_missing_fields(client: TestClient) -> None:
    user = users_factories.ProFactory(phoneNumber="0123456789")

    client = client.with_session_auth(user.email)
    response = client.patch("/users/phone", json={})

    assert response.status_code == 400
    assert response.json == {"phoneNumber": ["Ce champ est obligatoire"]}
    assert user.phoneNumber == "+33123456789"
    assert len(user.action_history) == 0


def test_patch_user_phone_without_auth(client: TestClient) -> None:
    user = users_factories.ProFactory(phoneNumber="0123456789")
    form_data = {"firstName": "Barrack", "lastName": "Afrit"}
    response = client.patch("/users/phone", json=form_data)

    assert response.status_code == 401
    assert user.phoneNumber == "+33123456789"
    assert len(user.action_history) == 0
