import pytest

from domain.show_types import show_types
from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_user

@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def when_list_show_types(self, app):
            # given
            user = create_user()
            PcObject.save(user)

            # when
            response = TestClient().with_auth(user.email)\
                                   .get(API_URL + '/showTypes')

            # then
            response_json = response.json()
            assert response.status_code == 200
            assert response_json == show_types
