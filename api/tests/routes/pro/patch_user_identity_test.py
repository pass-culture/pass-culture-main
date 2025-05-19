from typing import Any

import pytest

import pcapi.core.users.factories as users_factories
from pcapi.core.history import models as history_models


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

    assert len(user.action_history) == 1
    assert user.action_history[0].actionType == history_models.ActionType.INFO_MODIFIED
    assert user.action_history[0].user == user
    assert user.action_history[0].extraData["modified_info"] == {
        "firstName": {"new_info": "Axel", "old_info": "jean"},
        "lastName": {"new_info": "Ere", "old_info": "Kadre"},
    }


@pytest.mark.usefixtures("db_session")
def test_patch_user_identity_missing_fields(client: Any) -> None:
    user = users_factories.ProFactory(firstName="jean", lastName="Kadre")

    client = client.with_session_auth(user.email)
    response = client.patch("/users/identity", json={})

    assert response.status_code == 400
    assert user.firstName == "jean"
    assert user.lastName == "Kadre"
    assert len(user.action_history) == 0


@pytest.mark.usefixtures("db_session")
def test_patch_user_identity_without_auth(client: Any) -> None:
    user = users_factories.ProFactory(firstName="jean", lastName="Tours")
    form_data = {"firstName": "Barrack", "lastName": "Afrit"}
    response = client.patch("/users/identity", json=form_data)

    assert response.status_code == 401
    assert user.firstName == "jean"
    assert user.lastName == "Tours"
    assert len(user.action_history) == 0
