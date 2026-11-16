import pytest

from pcapi.core.favorites import factories as favorite_factories
from pcapi.core.favorites.models import FavoriteVenue
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")

FAVORITES_BASE_URL = "/native/v2/me/favorites/venues"


class GetTest:
    class Returns200Test:
        def when_user_is_logged_in_but_has_no_favorites(self, client):
            user = users_factories.UserFactory()

            response = client.with_token(user).get(FAVORITES_BASE_URL)

            assert response.status_code == 200
            assert response.json == {"page": 1, "nbFavorites": 0, "favorites": []}

        def when_user_is_logged_in_and_has_favorite_venues(self, client):
            user = users_factories.UserFactory()
            venue = offerers_factories.VenueFactory(
                name="Cinéma du centre",
                _bannerUrl="https://example.com/banner.jpg",
            )
            favorite = favorite_factories.FavoriteVenueFactory(user=user, venue=venue)
            # favorite of another user: not returned
            favorite_factories.FavoriteVenueFactory()

            response = client.with_token(user).get(FAVORITES_BASE_URL)

            assert response.status_code == 200
            assert response.json == {
                "page": 1,
                "nbFavorites": 1,
                "favorites": [
                    {
                        "id": favorite.id,
                        "venue": {
                            "id": venue.id,
                            "name": venue.name,
                            "image": "https://example.com/banner.jpg",
                        },
                    }
                ],
            }

        def test_number_of_queries_does_not_depend_on_the_number_of_favorites(self, client):
            user = users_factories.UserFactory()
            favorite_factories.FavoriteVenueFactory.create_batch(5, user=user)
            client = client.with_token(user)
            db.session.expire_all()

            # 1. user
            # 2. favorites with their venue
            with assert_num_queries(2):
                response = client.get(FAVORITES_BASE_URL)
                assert response.status_code == 200

            assert response.json["nbFavorites"] == 5

    class Returns401Test:
        def when_user_is_not_logged_in(self, client):
            with assert_num_queries(0):
                response = client.get(FAVORITES_BASE_URL)

            assert response.status_code == 401


class CreateFavoriteTest:
    def when_user_creates_a_favorite(self, client):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(name="Librairie du coin", _bannerUrl=None)

        response = client.with_token(user).post(FAVORITES_BASE_URL, json={"venueId": venue.id})

        assert response.status_code == 200
        favorite = db.session.query(FavoriteVenue).one()
        assert favorite.userId == user.id
        assert favorite.venueId == venue.id
        assert response.json == {
            "id": favorite.id,
            "venue": {"id": venue.id, "name": "Librairie du coin", "image": venue.bannerUrl},
        }

    def when_user_creates_a_favorite_twice(self, client):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        client = client.with_token(user)

        first_response = client.post(FAVORITES_BASE_URL, json={"venueId": venue.id})
        second_response = client.post(FAVORITES_BASE_URL, json={"venueId": venue.id})

        assert first_response.status_code == 200
        assert second_response.status_code == 200
        assert second_response.json["id"] == first_response.json["id"]
        assert db.session.query(FavoriteVenue).count() == 1

    @pytest.mark.settings(MAX_FAVORITES=1)
    def when_user_creates_one_favorite_above_the_limit(self, client):
        user = users_factories.UserFactory()
        favorite_factories.FavoriteVenueFactory(user=user)
        venue = offerers_factories.VenueFactory()

        response = client.with_token(user).post(FAVORITES_BASE_URL, json={"venueId": venue.id})

        assert response.status_code == 400
        assert response.json == {"code": "MAX_FAVORITES_REACHED"}
        assert db.session.query(FavoriteVenue).filter(FavoriteVenue.venueId == venue.id).count() == 0

    def test_venue_does_not_exist(self, client):
        user = users_factories.UserFactory()

        response = client.with_token(user).post(FAVORITES_BASE_URL, json={"venueId": 0})

        assert response.status_code == 404
        assert db.session.query(FavoriteVenue).count() == 0

    def when_user_is_not_logged_in(self, client):
        venue = offerers_factories.VenueFactory()

        response = client.post(FAVORITES_BASE_URL, json={"venueId": venue.id})

        assert response.status_code == 401
        assert db.session.query(FavoriteVenue).count() == 0


class DeleteTest:
    class Returns204Test:
        def when_user_deletes_its_favorite(self, client):
            user = users_factories.UserFactory()
            favorite = favorite_factories.FavoriteVenueFactory(user=user)

            response = client.with_token(user).delete(f"{FAVORITES_BASE_URL}/{favorite.id}")

            assert response.status_code == 204
            assert db.session.query(FavoriteVenue).count() == 0

    class Returns404Test:
        def when_user_deletes_another_user_favorite(self, client):
            favorite = favorite_factories.FavoriteVenueFactory()
            other_user = users_factories.UserFactory()

            response = client.with_token(other_user).delete(f"{FAVORITES_BASE_URL}/{favorite.id}")

            assert response.status_code == 404
            assert db.session.query(FavoriteVenue).count() == 1

        def when_favorite_does_not_exist(self, client):
            user = users_factories.UserFactory()

            response = client.with_token(user).delete(f"{FAVORITES_BASE_URL}/1203481310")

            assert response.status_code == 404

    class Returns401Test:
        def when_user_is_not_logged_in(self, client):
            favorite = favorite_factories.FavoriteVenueFactory()

            response = client.delete(f"{FAVORITES_BASE_URL}/{favorite.id}")

            assert response.status_code == 401
            assert db.session.query(FavoriteVenue).count() == 1
