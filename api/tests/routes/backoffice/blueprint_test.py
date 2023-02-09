from flask import url_for
import pytest

from pcapi.core.auth.api import generate_token
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_cors_allowed(client):
    # given
    user = users_factories.UserFactory()
    auth_token = generate_token(user, [perm_models.Permissions.REVIEW_PUBLIC_ACCOUNT])

    # when
    response = client.with_explicit_token(auth_token).options(
        url_for("backoffice_blueprint.review_public_account", user_id=user.id),
        headers={"Origin": "https://backoffice.testauto.passculture.team"},
    )

    # then
    assert response.status_code == 200
    assert response.headers.get("Access-Control-Allow-Origin") == "https://backoffice.testauto.passculture.team"


def test_cors_disallowed(client):
    # given
    user = users_factories.UserFactory()
    auth_token = generate_token(user, [perm_models.Permissions.REVIEW_PUBLIC_ACCOUNT])

    # when
    response = client.with_explicit_token(auth_token).options(
        url_for("backoffice_blueprint.review_public_account", user_id=user.id),
        headers={"Origin": "https://example.com"},
    )

    # then
    assert response.status_code == 200
    assert response.headers.get("Access-Control-Allow-Origin") == None
