import pytest

import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models


@pytest.mark.usefixtures("db_session")
def test_existing_user_session_to_be_deleted(client):
    user = users_factories.ProFactory()

    client = client.with_session_auth(email=user.email)
    assert users_models.UserSession.query.filter_by(userId=user.id).count() == 1

    response = client.get("/users/signout")

    assert response.status_code == 200
    assert response.json == {"global": "Déconnecté"}
    assert users_models.UserSession.query.filter_by(userId=user.id).count() == 0
