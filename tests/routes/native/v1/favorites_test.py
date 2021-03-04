from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.testing import assert_num_queries
from pcapi.model_creators.generic_creators import create_favorite
from pcapi.model_creators.generic_creators import create_mediation
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_from_offer
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
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
            offer1 = create_offer_with_thing_product(venue=venue, thumb_count=0)
            mediation1 = create_mediation(offer=offer1, is_active=True, idx=123)
            favorite1 = create_favorite(mediation=mediation1, offer=offer1, user=user)
            # Min price and earlier date are on diffents stocks and product thumb
            stock1a = create_stock_from_offer(offer1, beginning_datetime=tomorow, price=20)
            stock1b = create_stock_from_offer(offer1, beginning_datetime=now, price=30)
            stock1c = create_stock_from_offer(offer1, beginning_datetime=yesterday, price=40)
            offer2 = create_offer_with_thing_product(venue=venue, thumb_count=1)
            favorite2 = create_favorite(offer=offer2, user=user)
            # Set min price / earlier date on soft deleted stock. It should only appear as one stock
            stock2a = create_stock_from_offer(offer2, beginning_datetime=now, price=20, soft_deleted=True)
            stock2b = create_stock_from_offer(offer2, beginning_datetime=tomorow, price=50)
            offer3 = create_offer_with_thing_product(venue=venue, thumb_count=0)
            favorite3 = create_favorite(offer=offer3, user=user)
            # Try a stock without date
            stock3 = create_stock_from_offer(offer3, beginning_datetime=None, price=0)
            repository.save(
                offer1, offer2, stock1a, stock1b, stock1c, stock2a, stock2b, stock3, favorite1, favorite2, favorite3
            )

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
    class Returns204:
        def when_user_creates_a_favorite(self, app):
            # Given
            user, test_client = utils.create_user_and_test_client(app)
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code="29100", siret="12345678912341")
            offer1 = create_offer_with_thing_product(venue=venue, thumb_count=0)
            repository.save(offer1)
            assert FavoriteSQLEntity.query.count() == 0

            # When
            response = test_client.post(FAVORITES_URL, json={"offerId": offer1.id})

            # Then
            assert response.status_code == 204, response.data
            assert FavoriteSQLEntity.query.count() == 1
            favorite = FavoriteSQLEntity.query.first()
            assert favorite.dateCreated
            assert favorite.userId == user.id
