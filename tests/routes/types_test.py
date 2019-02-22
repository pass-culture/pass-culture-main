import pytest

from models import PcObject

from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_user


@pytest.mark.standalone
class Get:
    class Returns401:
        @clean_database
        def when_user_is_anonymous(self, app):
            # when
            response = TestClient().get(
                API_URL + '/types/')

            # then
            assert response.status_code == 401

    class Returns200:
        @clean_database
        def when_user_is_logged(self, app):
            # given
            user = create_user(email='test@email.com', password='testpsswd')

            PcObject.check_and_save(user)

            # when
            response = TestClient() \
                .with_auth('test@email.com', 'testpsswd') \
                .get(
                API_URL + '/types/')
            types = response.json()

            # then
            assert response.status_code == 200
            assert len(types) == 18

        @clean_database
        def when_user_is_admin(self, app):
            # given
            admin_user = create_user(email='pctest.admin93.0@btmx.fr', password='pctest.Admin93.0', is_admin=True, can_book_free_offers=False)
            PcObject.check_and_save(admin_user)

            # when
            response = TestClient() \
                .with_auth('pctest.admin93.0@btmx.fr', 'pctest.Admin93.0') \
                .get(
                API_URL + '/types/')
            types = response.json()

            # then
            assert response.status_code == 200
            assert len(types) == 20
            types_values = [type['value'] for type in types]
            assert 'ThingType.ACTIVATION' in types_values
            assert 'EventType.ACTIVATION' in types_values
