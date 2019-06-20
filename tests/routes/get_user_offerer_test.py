from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_user, \
    create_user_offerer, \
    create_offerer
from utils.human_ids import humanize


class Get:
    class Return200:
        @clean_database
        def test_get_user_offerer_should_return_only_user_offerer_from_current_user(self, app):
            # given
            user1 = create_user(email='patrick.fiori@test.com')
            user2 = create_user(email='celine.dion@test.com')
            offerer = create_offerer(siren='123456781')
            user_offerer1 = create_user_offerer(user1, offerer)
            user_offerer2 = create_user_offerer(user2, offerer)
            PcObject.save(user_offerer1, user_offerer2)

            # assert
            assert len(offerer.UserOfferers) == 2

            # when
            response = TestClient(app.test_client()) \
                .with_auth(email=user1.email) \
                .get('/userOfferers/' + humanize(offerer.id))

            # then
            assert response.status_code == 200
            assert response.json[0]['userId'] == humanize(user1.id)
