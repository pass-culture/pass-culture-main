import pytest

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_user


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
            user = create_user(email='test@email.com')

            PcObject.save(user)

            # when
            response = TestClient() \
                .with_auth('test@email.com') \
                .get(
                API_URL + '/types/')
            types = response.json()

            # then
            assert response.status_code == 200
            types_values = [type['value'] for type in types]
            assert 'ThingType.ACTIVATION' not in types_values
            assert 'EventType.ACTIVATION' not in types_values
            assert 'ThingType.OEUVRE_ART' in types_values
            assert 'ThingType.INSTRUMENT' in types_values
            assert 'ThingType.LIVRE_AUDIO' in types_values

        @clean_database
        def when_user_is_admin(self, app):
            # given
            admin_user = create_user(email='pctest.admin93.0@btmx.fr', can_book_free_offers=False, is_admin=True)
            PcObject.save(admin_user)

            # when
            response = TestClient() \
                .with_auth('pctest.admin93.0@btmx.fr') \
                .get(
                API_URL + '/types/')
            types = response.json()

            # then
            assert response.status_code == 200
            types_values = [type['value'] for type in types]
            assert 'ThingType.ACTIVATION' in types_values
            assert 'EventType.ACTIVATION' in types_values

        @clean_database
        def when_user_returns_types_labels(self, app):
            # given
            user = create_user(email='test@email.com')

            PcObject.save(user)

            # when
            response = TestClient() \
                .with_auth('test@email.com') \
                .get(
                API_URL + '/types/')
            types = response.json()

            # then
            assert response.status_code == 200
            labels_values = [type['proLabel'] for type in types]
            user_seen_labels_values = [type['appLabel'] for type in types]

            assert "Livre - format papier ou numérique, abonnements lecture" in labels_values
            assert "Conférences, rencontres et découverte des métiers" in labels_values
            assert "Musées, arts visuels & patrimoine" in labels_values
            assert "Pratique — séances d’essai et stages ponctuels" in labels_values
            assert "Livre audio numérique" in labels_values
            assert "Vente d’instruments de musique" in labels_values
            assert "Vente d'œuvres d'art" in labels_values

            assert "Achat d'œuvres d’art" in user_seen_labels_values
            assert "Achat d’instruments de musique" in user_seen_labels_values
            assert "Livres, cartes bibliothèque ou médiathèque" in user_seen_labels_values
