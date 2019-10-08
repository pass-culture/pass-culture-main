from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_user


class Get:
    class Returns200:
        @clean_database
        def when_current_user_is_admin(self, app):
            # Given
            user = create_user(is_admin=True, can_book_free_offers=False)
            PcObject.save(user)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # When
            response = auth_request.get('/dashboard')

            # Then
            assert response.status_code == 200
            assert '<a href="/dashboard/users">' in response.data.decode('utf-8')

    class Returns401:
        @clean_database
        def when_user_is_not_logged_in(self, app):
            # When
            response = TestClient(app.test_client()).get('/dashboard')

            # Then
            assert response.status_code == 401

    class Returns403:
        @clean_database
        def when_current_user_is_not_admin(self, app):
            # Given
            user = create_user(is_admin=False)
            PcObject.save(user)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # When
            response = auth_request.get('/dashboard')

            # Then
            assert response.status_code == 403
