from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_favorite
from pcapi.models import FavoriteSQLEntity
from pcapi.repository import repository

from tests.conftest import TestClient

from . import utils


pytestmark = pytest.mark.usefixtures("db_session")

FAVORITES_URL = "/native/v1/me/favorites"


class Get:
    class Returns200:
        def when_user_is_logged_in_but_has_no_favorites(self, app):
            # Given
            _, test_client = utils.create_user_and_test_client(app)

            # When
            response = test_client.get(FAVORITES_URL)

            # Then
            assert response.status_code == 200
            assert response.json == {"page": 1, "nbFavorites": 0, "favorites": []}

        def when_user_is_logged_in_and_has_favorite_offers(self, app):
            # Given
            now = datetime.now()
            yesterday = now - timedelta(days=1)
            tomorow = now + timedelta(days=1)
            user, test_client = utils.create_user_and_test_client(app)
            offerer = offers_factories.OffererFactory()
            venue = offers_factories.VenueFactory(managingOfferer=offerer)
            offer1 = offers_factories.EventOfferFactory(venue=venue)
            favorite1 = create_favorite(offer=offer1, user=user)
            # should be ignored because of the date in the past
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=tomorow, price=20)
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=now, price=30)
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=yesterday, price=40)
            offer2 = offers_factories.EventOfferFactory(venue=venue, product__thumbCount=666)
            favorite2 = create_favorite(offer=offer2, user=user)
            # Set min price / earlier date on soft deleted stock. It should only appear as one stock
            offers_factories.EventStockFactory(offer=offer2, beginningDatetime=now, price=20, isSoftDeleted=True)
            offers_factories.EventStockFactory(offer=offer2, beginningDatetime=tomorow, price=50)
            offer3 = offers_factories.ThingOfferFactory(venue=venue)
            favorite3 = create_favorite(offer=offer3, user=user)
            # Try a stock without date
            offers_factories.ThingStockFactory(offer=offer3, price=0)
            repository.save(favorite1, favorite2, favorite3)

            # When
            # QUERY_COUNT:
            # 1: Fetch the user for auth
            # 1: Fetch the favorites
            with assert_num_queries(2):
                response = test_client.get(FAVORITES_URL)

            # Then
            assert response.status_code == 200
            favorites = response.json["favorites"]
            assert len(favorites) == 3

            assert favorites[0]["offer"]["price"] is None
            assert favorites[0]["offer"]["startPrice"] == 2000
            assert favorites[0]["offer"]["date"] is None
            assert favorites[0]["offer"]["startDate"] == yesterday.isoformat()

            assert favorites[1]["offer"]["price"] == 5000
            assert favorites[1]["offer"]["startPrice"] is None
            assert favorites[1]["offer"]["date"] == tomorow.isoformat()
            assert favorites[1]["offer"]["startDate"] is None
            assert favorites[1]["offer"]["image"]["credit"] is None
            assert favorites[1]["offer"]["image"]["url"][:41] == "http://localhost/storage/thumbs/products/"

            assert favorites[2]["offer"]["price"] == 0
            assert favorites[2]["offer"]["startPrice"] is None
            assert favorites[2]["offer"]["date"] is None
            assert favorites[2]["offer"]["startDate"] is None

    class Returns401:
        def when_user_is_not_logged_in(self, app):
            # When
            response = TestClient(app.test_client()).get(FAVORITES_URL)

            # Then
            assert response.status_code == 401


class Post:
    class Returns200:
        def when_user_creates_a_favorite(self, app):
            # Given
            user, test_client = utils.create_user_and_test_client(app)
            offerer = offers_factories.OffererFactory()
            venue = offers_factories.VenueFactory(managingOfferer=offerer)
            offer1 = offers_factories.EventOfferFactory(venue=venue)
            assert FavoriteSQLEntity.query.count() == 0

            # When
            response = test_client.post(FAVORITES_URL, json={"offerId": offer1.id})

            # Then
            assert response.status_code == 200, response.data
            assert FavoriteSQLEntity.query.count() == 1
            favorite = FavoriteSQLEntity.query.first()
            assert favorite.dateCreated
            assert favorite.userId == user.id
            assert response.json["id"] == favorite.id
            assert response.json["offer"]


class Delete:
    class Returns204:
        def when_user_delete_its_favorite(self, app):
            # Given
            user, test_client = utils.create_user_and_test_client(app)
            offerer = offers_factories.OffererFactory()
            venue = offers_factories.VenueFactory(managingOfferer=offerer)
            offer = offers_factories.ThingOfferFactory(venue=venue)
            favorite = create_favorite(offer=offer, user=user)
            assert FavoriteSQLEntity.query.count() == 1

            # When
            response = test_client.delete(f"{FAVORITES_URL}/{favorite.id}")

            # Then
            assert response.status_code == 204
            assert FavoriteSQLEntity.query.count() == 0

        def when_user_delete_another_user_favorite(self, app):
            # Given
            _, test_client = utils.create_user_and_test_client(app)
            other_user = users_factories.UserFactory()
            offerer = offers_factories.OffererFactory()
            venue = offers_factories.VenueFactory(managingOfferer=offerer)
            offer = offers_factories.ThingOfferFactory(venue=venue)
            favorite = create_favorite(offer=offer, user=other_user)
            assert FavoriteSQLEntity.query.count() == 1

            # When
            response = test_client.delete(f"{FAVORITES_URL}/{favorite.id}")

            # Then
            assert response.status_code == 404
            assert FavoriteSQLEntity.query.count() == 1

        def when_user_delete_non_existent_favorite(self, app):
            # Given
            _, test_client = utils.create_user_and_test_client(app)

            # When
            response = test_client.delete(f"{FAVORITES_URL}/1203481310")

            # Then
            assert response.status_code == 404
