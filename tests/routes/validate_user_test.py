from models import User
from repository.repository import Repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user


class Patch:
    class Returns204:
        @clean_database
        def expect_validation_token_to_be_set_to_none(self, app):
            # Given
            user = create_user()
            user.generate_validation_token()
            Repository.save(user)
            user_id = user.id

            # When
            response = TestClient(app.test_client()).patch('/validate/user/' + user.validationToken,
                                                           headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 204
            assert User.query.get(user_id).isValidated

    class Returns404:
        @clean_database
        def when_validation_token_is_not_found(self, app):
            # Given
            random_token = '0987TYGHHJMJ'

            # When
            response = TestClient(app.test_client()).patch('/validate/user/' + random_token,
                                                           headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 404
            assert response.json['global'] == ['Ce lien est invalide']
