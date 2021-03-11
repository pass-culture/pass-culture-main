from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_favorite
from pcapi.models import FavoriteSQLEntity
from pcapi.utils.human_ids import humanize

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
            today = datetime.now() + timedelta(hours=3)  # offset a bit to make sure it's > now()
            yesterday = today - timedelta(days=1)
            tomorow = today + timedelta(days=1)
            user, test_client = utils.create_user_and_test_client(app)
            offerer = offers_factories.OffererFactory()
            venue = offers_factories.VenueFactory(managingOfferer=offerer)

            # Event offer with 1 expired stock, 2 futures ones and a mediation
            offer1 = offers_factories.EventOfferFactory(venue=venue)
            offers_factories.MediationFactory(offer=offer1, thumbCount=1, credit="Pour hurlevent !")
            favorite1 = create_favorite(offer=offer1, user=user)
            # should be ignored because of the date in the past
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=yesterday, price=10)
            # 2 valid stocks (different dates and prices)
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=today, price=30)
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=tomorow, price=20)

            # Event offer with soft deleted stock and product's image
            offer2 = offers_factories.EventOfferFactory(venue=venue, product__thumbCount=666)
            favorite2 = create_favorite(offer=offer2, user=user)
            offers_factories.EventStockFactory(offer=offer2, beginningDatetime=today, price=20, isSoftDeleted=True)
            offers_factories.EventStockFactory(offer=offer2, beginningDatetime=tomorow, price=50)

            # Thing offer with no date
            offer3 = offers_factories.ThingOfferFactory(venue=venue)
            favorite3 = create_favorite(offer=offer3, user=user)
            offers_factories.ThingStockFactory(offer=offer3, price=10)

            # Event offer with passed reservation date
            offer4 = offers_factories.EventOfferFactory(venue=venue)
            offers_factories.MediationFactory(offer=offer4)
            favorite4 = create_favorite(offer=offer4, user=user)
            stock4 = offers_factories.EventStockFactory(
                offer=offer4, beginningDatetime=datetime.now() + timedelta(minutes=30), price=50
            )
            assert stock4.bookingLimitDatetime < datetime.now()

            # Event offer in the past
            offer5 = offers_factories.EventOfferFactory(venue=venue)
            offers_factories.MediationFactory(offer=offer5)
            favorite5 = create_favorite(offer=offer5, user=user)
            offers_factories.EventStockFactory(offer=offer5, beginningDatetime=yesterday, price=50)

            # Event offer with two times the same date / price
            offer6 = offers_factories.EventOfferFactory(venue=venue)
            favorite6 = create_favorite(offer=offer6, user=user)
            offers_factories.EventStockFactory(offer=offer6, beginningDatetime=tomorow, price=30)
            offers_factories.EventStockFactory(offer=offer6, beginningDatetime=tomorow, price=30)

            # When
            # QUERY_COUNT:
            # 1: Fetch the user for auth
            # 1: Fetch the favorites
            with assert_num_queries(2):
                response = test_client.get(FAVORITES_URL)

            # Then
            assert response.status_code == 200
            favorites = response.json["favorites"]
            assert len(favorites) == 6

            # We have 2 valid stocks with different dates/prices and one mediation
            assert favorites[5]["id"] == favorite1.id
            assert favorites[5]["offer"]["price"] is None
            assert favorites[5]["offer"]["startPrice"] == 2000
            assert favorites[5]["offer"]["date"] is None
            assert favorites[5]["offer"]["startDate"] == today.isoformat()
            assert favorites[5]["offer"]["image"]["credit"] == "Pour hurlevent !"
            assert favorites[5]["offer"]["image"]["url"] == "http://localhost/storage/thumbs/mediations/%s" % (
                humanize(offer1.activeMediation.id)
            )

            # Only stock2b is valide and product has a thumb
            assert favorites[4]["id"] == favorite2.id
            assert favorites[4]["offer"]["price"] == 5000
            assert favorites[4]["offer"]["startPrice"] is None
            assert favorites[4]["offer"]["date"] == tomorow.isoformat()
            assert favorites[4]["offer"]["startDate"] is None
            assert favorites[4]["offer"]["image"]["credit"] is None
            assert favorites[4]["offer"]["image"]["url"] == "http://localhost/storage/thumbs/products/%s" % (
                humanize(offer2.product.id)
            )

            # No date
            assert favorites[3]["id"] == favorite3.id
            assert favorites[3]["offer"]["price"] == 1000
            assert favorites[3]["offer"]["startPrice"] is None
            assert favorites[3]["offer"]["date"] is None
            assert favorites[3]["offer"]["startDate"] is None
            assert favorites[3]["offer"]["image"] is None

            # Offer in the future but past the booking limit
            assert favorites[2]["id"] == favorite4.id
            assert favorites[2]["offer"]["price"] is None
            assert favorites[2]["offer"]["startPrice"] is None
            assert favorites[2]["offer"]["date"] is None
            assert favorites[2]["offer"]["startDate"] is None
            assert favorites[2]["offer"]["image"] is None

            # Offer in the past, favorite should appear but no price/date are valid
            assert favorites[1]["id"] == favorite5.id
            assert favorites[1]["offer"]["price"] is None
            assert favorites[1]["offer"]["startPrice"] is None
            assert favorites[1]["offer"]["date"] is None
            assert favorites[1]["offer"]["startDate"] is None
            assert favorites[1]["offer"]["image"] is None

            # best price/same date twice should appear as single price/date
            assert favorites[0]["id"] == favorite6.id
            assert favorites[0]["offer"]["price"] == 3000
            assert favorites[0]["offer"]["startPrice"] is None
            assert favorites[0]["offer"]["date"] == tomorow.isoformat()
            assert favorites[0]["offer"]["startDate"] is None
            assert favorites[0]["offer"]["image"] is None

        def test_expired_offer(self, app):
            # Given
            today = datetime.now() + timedelta(hours=3)  # offset a bit to make sure it's > now()
            yesterday = today - timedelta(days=1)
            tomorow = today + timedelta(days=1)
            user, test_client = utils.create_user_and_test_client(app)
            offerer = offers_factories.OffererFactory()
            venue = offers_factories.VenueFactory(managingOfferer=offerer)

            # Event offer future stock
            offer1 = offers_factories.EventOfferFactory(venue=venue)
            favorite1 = create_favorite(offer=offer1, user=user)
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=tomorow, price=10)

            # Thing offer with no date
            offer2 = offers_factories.ThingOfferFactory(venue=venue)
            favorite2 = create_favorite(offer=offer2, user=user)
            offers_factories.ThingStockFactory(offer=offer2, price=10)

            # Thing offer with past booking stock
            offer3 = offers_factories.ThingOfferFactory(venue=venue)
            favorite3 = create_favorite(offer=offer3, user=user)
            offers_factories.ThingStockFactory(offer=offer3, bookingLimitDatetime=yesterday, price=10)

            # Event offer with stock in the future but past booking
            offer4 = offers_factories.EventOfferFactory(venue=venue)
            favorite4 = create_favorite(offer=offer4, user=user)
            offers_factories.EventStockFactory(
                offer=offer4, beginningDatetime=today, bookingLimitDatetime=yesterday, price=10
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
            assert len(favorites) == 4

            assert favorites[3]["id"] == favorite1.id
            assert favorites[3]["offer"]["isExpired"] is False
            assert favorites[2]["id"] == favorite2.id
            assert favorites[2]["offer"]["isExpired"] is False
            assert favorites[1]["id"] == favorite3.id
            assert favorites[1]["offer"]["isExpired"] is True
            assert favorites[0]["id"] == favorite4.id
            assert favorites[0]["offer"]["isExpired"] is True

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
