from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer
from utils.human_ids import humanize


class Post:
    class Returns201:
        @clean_database
        def when_user_and_offerer_exists_in_database(self, app):
            # given
            user = create_user(email='patrick.fiori@test.com')
            offerer = create_offerer(siren='123456781')
            repository.save(user, offerer)
            payload = {
                "userId": humanize(user.id),
                "offererId": humanize(offerer.id)
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(email=user.email) \
                .post('/userOfferers', json=payload)

            # then
            assert response.status_code == 201
            user_offerer_response = response.json
            assert user_offerer_response['userId'] == humanize(user.id)
            assert 'validationToken' not in user_offerer_response

    class Returns400:
        @clean_database
        def when_user_id_is_not_present_in_payload(self, app):
            # given
            user = create_user(email='patrick.fiori@test.com')
            offerer = create_offerer(siren='123456781')
            repository.save(user, offerer)
            payload = {
                "offererId": humanize(offerer.id)
            }

            # when
            response = TestClient(app.test_client()) \
                .with_auth(email=user.email) \
                .post('/userOfferers', json=payload)

            # then
            assert response.status_code == 400
