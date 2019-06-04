from models import UserSession, PcObject
from tests.conftest import TestClient, clean_database
from tests.test_utils import API_URL, create_user


class Get:
    class Returns200:
        @clean_database
        def expect_the_existing_user_session_to_be_deleted_deleted(self, app):
            # given
            user = create_user(email='test@mail.com')
            PcObject.save(user)
            auth_request = TestClient().with_auth(email=user.email)

            assert auth_request.get(API_URL + '/bookings').status_code == 200

            # when
            response = auth_request.get(API_URL + '/users/signout')

            # then
            assert response.status_code == 200
            session = UserSession.query.filter_by(userId=user.id).first()
            assert session is None
