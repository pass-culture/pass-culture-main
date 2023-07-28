from datetime import datetime

from freezegun import freeze_time
import pytest

import pcapi.core.users.factories as users_factories
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.routes.native.security import authenticated_maybe_inactive_user_required

from tests.serialization.serialization_decorator_test import test_blueprint


pytestmark = pytest.mark.usefixtures("db_session")


@test_blueprint.route("/authenticated_and_active_user_required", methods=["GET"])
@authenticated_and_active_user_required
def authenticated_and_active_user_required_route(*args, **kwargs) -> None:
    return "", 204


@test_blueprint.route("/authenticated_maybe_inactive_user_required", methods=["GET"])
@authenticated_maybe_inactive_user_required
def authenticated_maybe_inactive_user_required_route(*args, **kwargs) -> None:
    return "", 204


@pytest.mark.parametrize(
    "path",
    [
        "/test-blueprint/authenticated_and_active_user_required",
        "/test-blueprint/authenticated_maybe_inactive_user_required",
    ],
)
def test_get_active_user(client, path):
    user = users_factories.UserFactory(isActive=True)

    client.with_token(user.email)
    response = client.get(path)
    assert response.status_code == 204


@pytest.mark.parametrize(
    "path",
    [
        "/test-blueprint/authenticated_and_active_user_required",
        "/test-blueprint/authenticated_maybe_inactive_user_required",
    ],
)
def test_get_unauthenticated_active_user(client, path):
    response = client.get(path)
    assert response.status_code == 401


def test_inactive_user_when_active_required(client):
    user = users_factories.UserFactory(isActive=False)
    path = "/test-blueprint/authenticated_and_active_user_required"

    client.with_token(user.email)
    response = client.get(path)
    assert response.status_code == 403


def test_inactive_user_when_may_be_inactive(client):
    user = users_factories.UserFactory(isActive=False)
    path = "/test-blueprint/authenticated_maybe_inactive_user_required"

    client.with_token(user.email)
    response = client.get(path)
    assert response.status_code == 204


@pytest.mark.parametrize(
    "path",
    [
        "/test-blueprint/authenticated_and_active_user_required",
        "/test-blueprint/authenticated_maybe_inactive_user_required",
    ],
)
@freeze_time("2023-07-28")
def test_success_when_token_is_issued_after_password_update_date(client, path):
    user = users_factories.UserFactory(password_date_updated=datetime.fromisoformat("2023-01-01"))
    client.with_token(user.email)
    response = client.get(path)

    assert response.status_code == 204


@pytest.mark.parametrize(
    "path",
    [
        "/test-blueprint/authenticated_and_active_user_required",
        "/test-blueprint/authenticated_maybe_inactive_user_required",
    ],
)
@freeze_time("2023-07-27")
def test_error_when_when_token_is_issued_before_password_update_date(client, path):
    user = users_factories.UserFactory(password_date_updated=datetime.fromisoformat("2023-07-28"))
    client.with_token(user.email)
    response = client.get(path)

    assert response.status_code == 401
    assert response.json == {
        "code": "INVALID_TOKEN_AFTER_PASSWORD_CHANGE",
        "message": "Token invalide suite à une modification de mot de passe",
    }
