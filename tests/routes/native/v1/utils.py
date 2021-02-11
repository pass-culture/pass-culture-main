from flask_jwt_extended.utils import create_access_token

from pcapi.core.users import factories as users_factories

from tests.conftest import TestClient


def create_user_and_test_client(app, email, **kwargs):
    user = users_factories.UserFactory(email=email, **kwargs)

    access_token = create_access_token(identity=email)
    test_client = TestClient(app.test_client())
    test_client.auth_header = {"Authorization": f"Bearer {access_token}"}

    return user, test_client
