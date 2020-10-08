from repository import repository
from tests.conftest import TestClient
import pytest
from model_creators.generic_creators import create_user, \
    create_venue_type


class Get:
    class Returns401:
        @pytest.mark.usefixtures("db_session")
        def when_the_user_is_not_authenticated(self, app):
            # When
            response = TestClient(app.test_client()).get('/venue-types')

            # then
            assert response.status_code == 401

    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_the_user_is_authenticated(self, app):
            # Given
            user = create_user()
            venue_types = [
                create_venue_type(label='Centre culturel', idx=1),
                create_venue_type(label='Musée', idx=2)
            ]
            repository.save(user, *venue_types)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get('/venue-types')

            # then
            assert response.status_code == 200
            assert len(response.json) == 2
            assert response.json == [
                {'id': 'AE', 'label': 'Centre culturel'},
                {'id': 'A9', 'label': 'Musée'}
            ]
