import pytest

from pcapi.core.artist.factories import ArtistFactory
from pcapi.core.favorites import factories as favorite_factories
from pcapi.core.favorites.factories import FavoriteArtistFactory
from pcapi.core.favorites.models import FavoriteArtist
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")

FAVORITES_BASE_URL = "/native/v2/me/favorites/artists"


class GetTest:
    class Returns200Test:
        def when_user_is_logged_in_but_has_no_favorites(self, client):
            # Given
            user = users_factories.UserFactory()

            # When
            response = client.with_token(user).get(FAVORITES_BASE_URL)
            assert response.status_code == 200

            # Then
            assert response.json == {"page": 1, "nbFavorites": 0, "favorites": []}

        def when_user_is_logged_in_and_has_favorite_artists(self, client):
            # Given
            user = users_factories.UserFactory()

            artists = []
            for _ in range(6):
                artists.append(ArtistFactory())

            for artist in artists:
                FavoriteArtistFactory(user=user, artist=artist)

            # When
            response = client.with_token(user).get(FAVORITES_BASE_URL)

            # Then
            assert response.status_code == 200
            favorites = response.json["favorites"]
            assert len(favorites) == 6

    class Returns401Test:
        def when_user_is_not_logged_in(self, client):
            # When
            with assert_num_queries(0):
                response = client.get(FAVORITES_BASE_URL)

            # Then
            assert response.status_code == 401


class CreateFavoriteTest:
    def when_user_creates_a_favorite(self, client):
        # Given
        user = users_factories.UserFactory()
        artist = ArtistFactory()

        # When
        response = client.with_token(user).post(FAVORITES_BASE_URL, json={"artistId": artist.id})

        # Then
        assert response.status_code == 200

        favorite = db.session.query(FavoriteArtist).first()
        assert favorite
        assert favorite.userId == user.id
        assert favorite.artist.id == artist.id

    def when_user_creates_a_favorite_twice(self, client):
        # Given
        user = users_factories.UserFactory()
        artist = ArtistFactory()

        # When
        response = client.with_token(user).post(FAVORITES_BASE_URL, json={"artistId": artist.id})
        assert response.status_code == 200
        assert db.session.query(FavoriteArtist).count() == 1

        # Then
        response = client.with_token(user).post(FAVORITES_BASE_URL, json={"artistId": artist.id})
        assert response.status_code == 200
        assert db.session.query(FavoriteArtist).count() == 1

    @pytest.mark.settings(MAX_FAVORITES=1)
    def when_user_creates_one_favorite_above_the_limit(self, client):
        # Given
        user = users_factories.UserFactory()
        artist = ArtistFactory()
        artist2 = ArtistFactory()

        # When
        response = client.with_token(user).post(FAVORITES_BASE_URL, json={"artistId": artist.id})
        assert response.status_code == 200
        assert db.session.query(FavoriteArtist).count() == 1

        # Then
        response = client.with_token(user).post(FAVORITES_BASE_URL, json={"artistId": artist2.id})
        assert response.status_code == 400

    def test_artist_does_not_exist(self, client):
        # Given
        user = users_factories.UserFactory()

        # When
        response = client.with_token(user).post(FAVORITES_BASE_URL, json={"artistId": "unknown"})

        # Then
        assert response.status_code == 404


class DeleteTest:
    class Returns204Test:
        def when_user_delete_its_favorite(self, client):
            # Given
            user = users_factories.UserFactory()
            artist = ArtistFactory()
            favorite = favorite_factories.FavoriteArtistFactory(user=user, artist=artist)

            assert db.session.query(FavoriteArtist).count() == 1

            # When
            response = client.with_token(user).delete(f"{FAVORITES_BASE_URL}/{favorite.id}")

            # Then
            assert response.status_code == 204
            assert db.session.query(FavoriteArtist).count() == 0

        def when_user_delete_another_user_favorite(self, client):
            # Given
            user = users_factories.UserFactory()
            user2 = users_factories.UserFactory()
            artist = ArtistFactory()
            favorite = favorite_factories.FavoriteArtistFactory(user=user, artist=artist)

            assert db.session.query(FavoriteArtist).count() == 1

            # When
            response = client.with_token(user2).delete(f"{FAVORITES_BASE_URL}/{favorite.id}")

            # Then
            assert response.status_code == 404
            assert db.session.query(FavoriteArtist).count() == 1

        def when_user_delete_non_existent_favorite(self, client):
            # Given
            user = users_factories.UserFactory()

            # When
            response = client.with_token(user).delete(f"{FAVORITES_BASE_URL}/1203481310")

            # Then
            assert response.status_code == 404
