from pcapi.domain.venue.venue_label.venue_label import VenueLabel
from pcapi.repository import repository
from tests.conftest import TestClient
import pytest
from pcapi.model_creators.generic_creators import create_user, \
    create_venue_type, create_venue_label


class Get:
    class Returns401:
        @pytest.mark.usefixtures("db_session")
        def when_the_user_is_not_authenticated(self, app):
            # When
            response = TestClient(app.test_client()).get('/venue-labels')

            # then
            assert response.status_code == 401

    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_the_user_is_authenticated(self, app):
            # Given
            user = create_user()
            venue_labels = [
                create_venue_label(label='Maison des illustres', idx=1),
                create_venue_label(label='Monuments historiques', idx=2)
            ]
            repository.save(user, *venue_labels)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get('/venue-labels')

            # then
            assert response.status_code == 200
            assert len(response.json) == 2
            assert response.json == [
                {'id': 'AE', 'label': 'Maison des illustres'},
                {'id': 'A9', 'label': 'Monuments historiques'}
            ]
