import copy

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_user, API_URL


class Get:
    class Returns401:
        @clean_database
        def test_reusing_cookies_after_a_sign_out_is_unauthorized(self, app):
            # given
            user = create_user(email='test@mail.com')
            PcObject.save(user)
            original_auth_request = TestClient().with_auth(email=user.email)
            spoofed_auth_request = copy.deepcopy(original_auth_request)

            assert original_auth_request.get(API_URL + '/bookings').status_code == 200
            spoofed_auth_request.session.cookies = copy.deepcopy(original_auth_request.session.cookies)
            original_auth_request.get(API_URL + '/users/signout')

            # when
            spoofed_response = spoofed_auth_request.get(API_URL + '/bookings')

            # then
            assert spoofed_response.status_code == 401
