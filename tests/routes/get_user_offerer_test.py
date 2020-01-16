from repository.repository import Repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_user_offerer
from utils.human_ids import humanize


class Get:
    class Returns200:
        @clean_database
        def test_get_user_offerer_should_return_only_user_offerer_from_current_user(self, app):
            # given
            user1 = create_user(email='patrick.fiori@test.com')
            user2 = create_user(email='celine.dion@test.com')
            offerer = create_offerer(siren='123456781')
            user_offerer1 = create_user_offerer(user1, offerer)
            user_offerer2 = create_user_offerer(user2, offerer)
            Repository.save(user_offerer1, user_offerer2)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(email=user1.email) \
                .get('/userOfferers/' + humanize(offerer.id))

            # then
            assert response.status_code == 200
            user_offerer_response = response.json[0]
            assert user_offerer_response['userId'] == humanize(user1.id)
            assert 'validationToken' not in user_offerer_response

        @clean_database
        def when_offerer_id_does_not_exist(self, app):
            # given
            user1 = create_user(email='patrick.fiori@test.com')
            user2 = create_user(email='celine.dion@test.com')
            offerer = create_offerer(siren='123456781')
            user_offerer1 = create_user_offerer(user1, offerer)
            user_offerer2 = create_user_offerer(user2, offerer)
            Repository.save(user_offerer1, user_offerer2)
            non_existing_offerer_id = 'B9'

            # when
            response = TestClient(app.test_client()) \
                .with_auth(email=user1.email) \
                .get('/userOfferers/' + non_existing_offerer_id)

            # then
            assert response.status_code == 200
            assert response.json == []
