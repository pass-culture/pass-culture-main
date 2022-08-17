from datetime import datetime
from datetime import timedelta
from typing import Any

import pytest

from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_get_user_email_pending_validation(app: Any, client: Any) -> None:
    user = users_factories.ProFactory(email="some@email.com")
    users_factories.EmailUpdateEntryFactory(user=user)
    client = client.with_session_auth(user.email)
    response = client.get("/users/email_pending_validation")

    assert response.status_code == 200

    assert response.json == {"newEmail": "some@email.com.update"}


def test_get_user_email_no_pending_validation(client: Any) -> None:
    user = users_factories.ProFactory()

    client = client.with_session_auth(user.email)
    response = client.get("/users/email_pending_validation")

    assert response.status_code == 200
    assert response.json == {"newEmail": None}


def test_get_user_email_no_active_pending_validation(client: Any) -> None:
    user = users_factories.ProFactory()
    now = datetime.utcnow()
    users_factories.EmailUpdateEntryFactory(user=user, creationDate=now - timedelta(hours=2))
    users_factories.EmailValidationEntryFactory(user=user, creationDate=now - timedelta(hours=1))

    client = client.with_session_auth(user.email)
    response = client.get("/users/email_pending_validation")

    assert response.status_code == 200
    assert response.json == {"newEmail": None}


def test_get_user_email_multiple_validations_with_pending(client: Any) -> None:
    user = users_factories.ProFactory()
    now = datetime.utcnow()
    users_factories.EmailUpdateEntryFactory(user=user, creationDate=now - timedelta(hours=2))
    users_factories.EmailValidationEntryFactory(user=user, creationDate=now - timedelta(hours=1))
    users_factories.EmailUpdateEntryFactory(
        user=user, creationDate=now - timedelta(minutes=30), newUserEmail="newSuperEmail", newDomainEmail="pc.cool"
    )

    client = client.with_session_auth(user.email)
    response = client.get("/users/email_pending_validation")

    assert response.status_code == 200
    assert response.json == {"newEmail": "newSuperEmail@pc.cool"}
