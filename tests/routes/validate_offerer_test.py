import secrets
from unittest.mock import call, patch

from models import Offerer
from repository import repository
from tests.conftest import TestClient
import pytest
from tests.model_creators.generic_creators import create_offerer, create_user, \
    create_user_offerer, \
    create_venue


class Get:
    class Returns202:
        @patch('routes.validate.feature_queries.is_active')
        @pytest.mark.usefixtures("db_session")
        def expect_offerer_to_be_validated(self, mocked_feature, app):
            # Given
            mocked_feature.return_value = False
            offerer_token = secrets.token_urlsafe(20)
            offerer = create_offerer(validation_token=offerer_token)
            user = create_user()
            admin = create_user_offerer(user, offerer, is_admin=True)
            repository.save(admin)

            # When
            response = TestClient(app.test_client()) \
                .get(f'/validate/offerer/{offerer_token}',
                     headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 202
            offerer = Offerer.query \
                .filter_by(id=offerer.id) \
                .first()
            assert offerer.isValidated is True

        @patch('routes.validate.feature_queries.is_active')
        @patch('routes.validate.link_valid_venue_to_irises')
        @pytest.mark.usefixtures("db_session")
        def expect_link_venue_to_iris_if_valid_to_have_been_called_for_every_venue(self,
                                                                                   mocked_link_venue_to_iris_if_valid,
                                                                                   mocked_feature,
                                                                                   app):
            # Given
            mocked_feature.return_value = False
            offerer_token = secrets.token_urlsafe(20)
            offerer = create_offerer(validation_token=offerer_token)
            create_venue(offerer)
            create_venue(offerer, siret=f'{offerer.siren}65371')
            create_venue(offerer, is_virtual=True, siret=None)
            user = create_user()
            admin = create_user_offerer(user, offerer, is_admin=True)
            repository.save(admin)

            # When
            response = TestClient(app.test_client()) \
                .get(f'/validate/offerer/{offerer_token}',
                     headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 202
            assert mocked_link_venue_to_iris_if_valid.call_count == 3

        @patch('routes.validate.feature_queries.is_active')
        @patch('routes.validate.redis.add_venue_id')
        @pytest.mark.usefixtures("db_session")
        def expect_offerer_managed_venues_to_be_added_to_redis_when_feature_is_active(self, mocked_redis,
                                                                                      mocked_feature, app):
            # Given
            mocked_feature.return_value = True
            offerer_token = secrets.token_urlsafe(20)
            offerer = create_offerer(validation_token=offerer_token)
            create_venue(offerer, idx=1)
            create_venue(offerer, idx=2, siret=f'{offerer.siren}65371')
            create_venue(offerer, idx=3, is_virtual=True, siret=None)
            user = create_user()
            admin = create_user_offerer(user, offerer, is_admin=True)
            repository.save(admin)

            # When
            response = TestClient(app.test_client()) \
                .get(f'/validate/offerer/{offerer_token}',
                     headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 202
            assert mocked_redis.call_count == 3
            assert mocked_redis.call_args_list == [
                call(client=app.redis_client, venue_id=1),
                call(client=app.redis_client, venue_id=2),
                call(client=app.redis_client, venue_id=3),
            ]

        @patch('routes.validate.feature_queries.is_active')
        @patch('routes.validate.redis.add_venue_id')
        @pytest.mark.usefixtures("db_session")
        def expect_offerer_managed_venues_not_to_be_added_to_redis_when_feature_is_not_active(self,
                                                                                              mocked_redis,
                                                                                              mocked_feature,
                                                                                              app):
            # Given
            mocked_feature.return_value = False
            offerer_token = secrets.token_urlsafe(20)
            offerer = create_offerer(validation_token=offerer_token)
            create_venue(offerer)
            create_venue(offerer, siret=f'{offerer.siren}65371')
            create_venue(offerer, is_virtual=True, siret=None)
            user = create_user()
            admin = create_user_offerer(user, offerer, is_admin=True)
            repository.save(admin)

            # When
            response = TestClient(app.test_client()) \
                .get(f'/validate/offerer/{offerer_token}',
                     headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 202
            assert mocked_redis.call_count == 0

    class Returns404:
        @pytest.mark.usefixtures("db_session")
        def expect_offerer_not_to_be_validated_with_unknown_token(self, app):
            # When
            response = TestClient(app.test_client()) \
                .with_auth(email='pro@example.com') \
                .get('/validate/offerer/123')

            # Then
            assert response.status_code == 404
