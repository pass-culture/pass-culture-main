from datetime import datetime
from datetime import timedelta
from decimal import Decimal

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import testing as users_testing
from pcapi.core.users.models import Favorite
from pcapi.notifications import push as push_notifications
from pcapi.notifications.push import testing as push_testing
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")

FAVORITES_URL = "/native/v1/me/favorites"
FAVORITES_COUNT_URL = "/native/v1/me/favorites/count"


class GetTest:
    class Returns200Test:
        def when_user_is_logged_in_but_has_no_favorites(self, client):
            # Given
            user = users_factories.UserFactory()

            # When
            response = client.with_token(user.email).get(FAVORITES_URL)

            # Then
            assert response.status_code == 200
            assert response.json == {"page": 1, "nbFavorites": 0, "favorites": []}

        def when_user_is_logged_in_and_has_favorite_offers(self, client):
            # Given
            today = datetime.utcnow() + timedelta(hours=3)  # offset a bit to make sure it's > now()
            yesterday = today - timedelta(days=1)
            tomorow = today + timedelta(days=1)
            user = users_factories.UserFactory()
            offerer = offerers_factories.OffererFactory()
            venue = offerers_factories.VenueFactory(managingOfferer=offerer, publicName="Le Petit Rintintin")

            # Event offer with 1 expired stock, 2 futures ones and a mediation
            offer1 = offers_factories.EventOfferFactory(venue=venue)
            offers_factories.MediationFactory(offer=offer1, thumbCount=1, credit="Pour hurlevent !")
            favorite1 = users_factories.FavoriteFactory(offer=offer1, user=user)
            # should be ignored because of the date in the past
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=yesterday, price=10)
            # 2 valid stocks (different dates and prices)
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=today, price=30)
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=tomorow, price=20)

            # Event offer with soft deleted stock and product's image
            offer2 = offers_factories.EventOfferFactory(venue=venue)
            mediation = offers_factories.MediationFactory(offer=offer2, thumbCount=666)
            favorite2 = users_factories.FavoriteFactory(offer=offer2, user=user)
            offers_factories.EventStockFactory(offer=offer2, beginningDatetime=today, price=20, isSoftDeleted=True)
            offers_factories.EventStockFactory(offer=offer2, beginningDatetime=tomorow, price=50)

            # Thing offer with no date
            offer3 = offers_factories.ThingOfferFactory(
                venue=venue, subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id
            )
            favorite3 = users_factories.FavoriteFactory(offer=offer3, user=user)
            offers_factories.ThingStockFactory(offer=offer3, price=10)

            # Event offer with passed reservation date
            offer4 = offers_factories.EventOfferFactory(venue=venue)
            offers_factories.MediationFactory(offer=offer4)
            favorite4 = users_factories.FavoriteFactory(offer=offer4, user=user)
            stock4 = offers_factories.EventStockFactory(
                offer=offer4, beginningDatetime=datetime.utcnow() + timedelta(minutes=30), price=50
            )
            assert stock4.bookingLimitDatetime < datetime.utcnow()

            # Event offer in the past
            offer5 = offers_factories.EventOfferFactory(venue=venue)
            offers_factories.MediationFactory(offer=offer5)
            favorite5 = users_factories.FavoriteFactory(offer=offer5, user=user)
            offers_factories.EventStockFactory(offer=offer5, beginningDatetime=yesterday, price=50)

            # Event offer with two times the same date / price
            offer6 = offers_factories.EventOfferFactory(venue=venue)
            favorite6 = users_factories.FavoriteFactory(offer=offer6, user=user)
            offers_factories.EventStockFactory(offer=offer6, beginningDatetime=tomorow, price=30)
            offers_factories.EventStockFactory(offer=offer6, beginningDatetime=tomorow, price=30)

            client.with_token(user.email)

            # When
            # QUERY_COUNT:
            # 1: Fetch the user for auth
            # 1: Fetch the favorites
            with assert_num_queries(2):
                response = client.get(FAVORITES_URL)

            # Then
            assert response.status_code == 200
            favorites = response.json["favorites"]
            assert len(favorites) == 6

            # We have 2 valid stocks with different dates/prices and one mediation
            assert favorites[5]["id"] == favorite1.id
            assert favorites[5]["offer"]["price"] is None
            assert favorites[5]["offer"]["startPrice"] == 2000
            assert favorites[5]["offer"]["date"] is None
            assert favorites[5]["offer"]["startDate"] == today.isoformat() + "Z"
            assert favorites[5]["offer"]["image"]["credit"] == "Pour hurlevent !"
            assert favorites[5]["offer"]["image"]["url"] == "http://localhost/storage/thumbs/mediations/%s" % (
                humanize(offer1.activeMediation.id)
            )
            assert favorites[5]["offer"]["expenseDomains"] == ["all"]
            assert favorites[5]["offer"]["subcategoryId"] == "SEANCE_CINE"
            assert favorites[5]["offer"]["venueName"] == "Le Petit Rintintin"

            # Only stock2b is valid and product has a thumb
            assert favorites[4]["id"] == favorite2.id
            assert favorites[4]["offer"]["price"] == 5000
            assert favorites[4]["offer"]["startPrice"] is None
            assert favorites[4]["offer"]["date"] == tomorow.isoformat() + "Z"
            assert favorites[4]["offer"]["startDate"] is None
            assert favorites[4]["offer"]["image"]["credit"] is None
            assert (
                favorites[4]["offer"]["image"]["url"]
                == f"http://localhost/storage/thumbs/mediations/{humanize(mediation.id)}_665"
            )
            assert favorites[4]["offer"]["expenseDomains"] == ["all"]
            assert favorites[4]["offer"]["subcategoryId"] == "SEANCE_CINE"
            assert favorites[4]["offer"]["venueName"] == "Le Petit Rintintin"

            # No date
            assert favorites[3]["id"] == favorite3.id
            assert favorites[3]["offer"]["price"] == 1000
            assert favorites[3]["offer"]["startPrice"] is None
            assert favorites[3]["offer"]["date"] is None
            assert favorites[3]["offer"]["startDate"] is None
            assert favorites[3]["offer"]["image"] is None
            assert favorites[3]["offer"]["subcategoryId"] == "SUPPORT_PHYSIQUE_FILM"
            assert set(favorites[3]["offer"]["expenseDomains"]) == {"physical", "all"}
            assert favorites[3]["offer"]["venueName"] == "Le Petit Rintintin"

            # Offer in the future but past the booking limit
            assert favorites[2]["id"] == favorite4.id
            assert favorites[2]["offer"]["price"] is None
            assert favorites[2]["offer"]["startPrice"] is None
            assert favorites[2]["offer"]["date"] is None
            assert favorites[2]["offer"]["startDate"] is None
            assert (
                favorites[2]["offer"]["image"]["url"]
                == f"http://localhost/storage/thumbs/mediations/{humanize(offer4.activeMediation.id)}"
            )
            assert favorites[2]["offer"]["expenseDomains"] == ["all"]
            assert favorites[2]["offer"]["subcategoryId"] == "SEANCE_CINE"
            assert favorites[2]["offer"]["venueName"] == "Le Petit Rintintin"

            # Offer in the past, favorite should appear but no price/date are valid
            assert favorites[1]["id"] == favorite5.id
            assert favorites[1]["offer"]["price"] is None
            assert favorites[1]["offer"]["startPrice"] is None
            assert favorites[1]["offer"]["date"] is None
            assert favorites[1]["offer"]["startDate"] is None
            assert (
                favorites[1]["offer"]["image"]["url"]
                == f"http://localhost/storage/thumbs/mediations/{humanize(offer5.activeMediation.id)}"
            )
            assert favorites[1]["offer"]["expenseDomains"] == ["all"]
            assert favorites[1]["offer"]["subcategoryId"] == "SEANCE_CINE"
            assert favorites[1]["offer"]["venueName"] == "Le Petit Rintintin"

            # best price/same date twice should appear as single price/date
            assert favorites[0]["id"] == favorite6.id
            assert favorites[0]["offer"]["price"] == 3000
            assert favorites[0]["offer"]["startPrice"] is None
            assert favorites[0]["offer"]["date"] == tomorow.isoformat() + "Z"
            assert favorites[0]["offer"]["startDate"] is None
            assert favorites[0]["offer"]["image"] is None
            assert favorites[0]["offer"]["expenseDomains"] == ["all"]
            assert favorites[0]["offer"]["subcategoryId"] == "SEANCE_CINE"
            assert favorites[0]["offer"]["venueName"] == "Le Petit Rintintin"

        def test_offer_venue_name_is_common_name_for_non_digital_offer(self, client):
            user = users_factories.UserFactory()
            offerer = offerers_factories.OffererFactory(name="Pathé Gaumont")
            venue = offerers_factories.VenueFactory(managingOfferer=offerer, publicName="Ciné Pathé")
            offer = offers_factories.EventOfferFactory(venue=venue)
            users_factories.FavoriteFactory(offer=offer, user=user)

            response = client.with_token(user.email).get(FAVORITES_URL)
            favorites = response.json["favorites"]

            assert favorites[0]["offer"]["venueName"] == "Ciné Pathé"

        def test_offer_venue_name_is_offerer_name_for_digital_offer(self, client):
            user = users_factories.UserFactory()
            offerer = offerers_factories.OffererFactory(name="Pathé Gaumont")
            venue = offerers_factories.VenueFactory(managingOfferer=offerer, publicName="Ciné Pathé")
            offer = offers_factories.DigitalOfferFactory(venue=venue)
            users_factories.FavoriteFactory(offer=offer, user=user)

            response = client.with_token(user.email).get(FAVORITES_URL)
            favorites = response.json["favorites"]

            assert favorites[0]["offer"]["venueName"] == "Pathé Gaumont"

        def test_expired_offer(self, client):
            # Given
            today = datetime.utcnow() + timedelta(hours=3)  # offset a bit to make sure it's > now()
            yesterday = today - timedelta(days=1)
            tomorow = today + timedelta(days=1)
            user = users_factories.UserFactory()
            user.add_beneficiary_role()
            users_factories.DepositGrantFactory(user=user)
            offerer = offerers_factories.OffererFactory()
            venue = offerers_factories.VenueFactory(managingOfferer=offerer)

            # Event offer future stock
            offer1 = offers_factories.EventOfferFactory(venue=venue)
            favorite1 = users_factories.FavoriteFactory(offer=offer1, user=user)
            offers_factories.EventStockFactory(offer=offer1, beginningDatetime=tomorow, price=10)

            # Thing offer with no date
            offer2 = offers_factories.ThingOfferFactory(venue=venue)
            favorite2 = users_factories.FavoriteFactory(offer=offer2, user=user)
            offers_factories.ThingStockFactory(offer=offer2, price=10)

            # Thing offer with past booking stock
            offer3 = offers_factories.ThingOfferFactory(venue=venue)
            favorite3 = users_factories.FavoriteFactory(offer=offer3, user=user)
            offers_factories.ThingStockFactory(offer=offer3, bookingLimitDatetime=yesterday, price=10)

            # Event offer with stock in the future but past booking
            offer4 = offers_factories.EventOfferFactory(venue=venue)
            favorite4 = users_factories.FavoriteFactory(offer=offer4, user=user)
            offers_factories.EventStockFactory(
                offer=offer4, beginningDatetime=today, bookingLimitDatetime=yesterday, price=10
            )

            # Deactivated event offer future stock
            offer5 = offers_factories.EventOfferFactory(venue=venue, isActive=False)
            favorite5 = users_factories.FavoriteFactory(offer=offer5, user=user)
            offers_factories.EventStockFactory(offer=offer5, beginningDatetime=tomorow, price=10)

            # Deactivated thing offer with no date
            offer6 = offers_factories.ThingOfferFactory(venue=venue, isActive=False)
            favorite6 = users_factories.FavoriteFactory(offer=offer6, user=user)
            offers_factories.ThingStockFactory(offer=offer6, price=10)

            # Event offer with soft deleted stock
            offer7 = offers_factories.EventOfferFactory(venue=venue)
            favorite7 = users_factories.FavoriteFactory(offer=offer7, user=user)
            offers_factories.EventStockFactory(
                offer=offer7, beginningDatetime=tomorow, quantity=1, price=10, isSoftDeleted=True
            )

            # Event offer with booked stock
            offer8 = offers_factories.EventOfferFactory(venue=venue)
            favorite8 = users_factories.FavoriteFactory(offer=offer8, user=user)
            stock8 = offers_factories.EventStockFactory(offer=offer8, beginningDatetime=tomorow, quantity=1, price=10)
            bookings_factories.BookingFactory(stock=stock8, user=user)

            client.with_token(user.email)

            # When
            # QUERY_COUNT:
            # 1: Fetch the user for auth
            # 1: Fetch the favorites
            with assert_num_queries(2):
                response = client.get(FAVORITES_URL)

            # Then
            assert response.status_code == 200
            favorites = response.json["favorites"]
            count = 8
            assert len(favorites) == count

            favorites.reverse()

            assert [fav["id"] for fav in favorites] == [
                favorite1.id,
                favorite2.id,
                favorite3.id,
                favorite4.id,
                favorite5.id,
                favorite6.id,
                favorite7.id,
                favorite8.id,
            ]
            assert [fav["offer"]["isExpired"] for fav in favorites] == [
                False,
                False,
                True,
                True,
                False,
                False,
                False,
                False,
            ]
            assert [fav["offer"]["isSoldOut"] for fav in favorites] == [
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                True,
            ]
            assert [fav["offer"]["isReleased"] for fav in favorites] == [
                True,
                True,
                True,
                True,
                False,
                False,
                True,
                True,
            ]

    class Returns401Test:
        def when_user_is_not_logged_in(self, client):
            # When
            response = client.get(FAVORITES_URL)

            # Then
            assert response.status_code == 401


class PostTest:
    def when_user_creates_a_favorite(self, client):
        # Given
        user = users_factories.UserFactory()
        offer = offers_factories.EventOfferFactory(
            name="This is a long event name that has a space at the sixty-first character"
        )
        earliest_stock = offers_factories.EventStockFactory(offer=offer, price=Decimal("10.1"), quantity=None)
        offers_factories.EventStockFactory(beginningDatetime=earliest_stock.beginningDatetime + timedelta(days=30))

        # When
        response = client.with_token(user.email).post(FAVORITES_URL, json={"offerId": offer.id})

        # Then
        assert response.status_code == 200, response.data
        assert Favorite.query.count() == 1
        favorite = Favorite.query.first()
        assert favorite.dateCreated
        assert favorite.userId == user.id
        assert response.json["id"] == favorite.id
        assert response.json["offer"]["price"] == 1010

        expected_push_counts = (
            1  # for user attribute update in android
            + 1  # for user attribute update in iOS
            + 1  # for favorite tracking
        )
        assert len(push_testing.requests) == expected_push_counts
        assert len(users_testing.sendinblue_requests) == 1
        sendinblue_data = users_testing.sendinblue_requests[0]
        assert sendinblue_data["attributes"]["LAST_FAVORITE_CREATION_DATE"] is not None

        favorite_creation_tracking_event = next(
            event
            for event in push_testing.requests
            if event.get("event_name") == push_notifications.BatchEvent.HAS_ADDED_OFFER_TO_FAVORITES.value
        )
        event_payload = favorite_creation_tracking_event["event_payload"]
        assert event_payload["event_date"] == earliest_stock.beginningDatetime.isoformat(timespec="seconds")
        assert event_payload["offer_name"] == "This is a long event name that has a space at the sixty-first..."
        assert all(value is not None for value in event_payload.values())

    def when_user_creates_a_favorite_twice(self, client):
        # Given
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer1 = offers_factories.EventOfferFactory(venue=venue)
        assert Favorite.query.count() == 0

        client.with_token(user.email)

        # When
        response = client.post(FAVORITES_URL, json={"offerId": offer1.id})
        assert response.status_code == 200
        response = client.post(FAVORITES_URL, json={"offerId": offer1.id})

        # Then
        assert response.status_code == 200
        assert Favorite.query.count() == 1

        expected_push_counts = (
            1  # for user attribute update in android
            + 1  # for user attribute update in iOS
            + 1  # for favorite tracking
        )
        assert len(push_testing.requests) == expected_push_counts
        assert len(users_testing.sendinblue_requests) == 1
        sendinblue_data = users_testing.sendinblue_requests[0]
        assert sendinblue_data["attributes"]["LAST_FAVORITE_CREATION_DATE"] is not None

    @override_settings(MAX_FAVORITES=1)
    def when_user_creates_one_favorite_above_the_limit(self, client):
        user = users_factories.UserFactory()
        offer = offers_factories.EventOfferFactory()
        assert Favorite.query.count() == 0

        client.with_token(user.email)

        response = client.post(FAVORITES_URL, json={"offerId": offer.id})

        assert response.status_code == 200, response.data
        assert Favorite.query.count() == 1

        response = client.post(FAVORITES_URL, json={"offerId": offer.id})

        assert response.status_code == 400, response.data
        assert response.json == {"code": "MAX_FAVORITES_REACHED"}
        assert Favorite.query.count() == 1


class DeleteTest:
    class Returns204Test:
        def when_user_delete_its_favorite(self, client):
            # Given
            user = users_factories.UserFactory()
            offerer = offerers_factories.OffererFactory()
            venue = offerers_factories.VenueFactory(managingOfferer=offerer)
            offer = offers_factories.ThingOfferFactory(venue=venue)
            favorite = users_factories.FavoriteFactory(offer=offer, user=user)
            assert Favorite.query.count() == 1

            # When
            response = client.with_token(user.email).delete(f"{FAVORITES_URL}/{favorite.id}")

            # Then
            assert response.status_code == 204
            assert Favorite.query.count() == 0

        def when_user_delete_another_user_favorite(self, client):
            # Given
            user = users_factories.UserFactory()
            other_beneficiary = users_factories.BeneficiaryGrant18Factory()
            offerer = offerers_factories.OffererFactory()
            venue = offerers_factories.VenueFactory(managingOfferer=offerer)
            offer = offers_factories.ThingOfferFactory(venue=venue)
            favorite = users_factories.FavoriteFactory(offer=offer, user=other_beneficiary)
            assert Favorite.query.count() == 1

            # When
            response = client.with_token(user.email).delete(f"{FAVORITES_URL}/{favorite.id}")

            # Then
            assert response.status_code == 404
            assert Favorite.query.count() == 1

        def when_user_delete_non_existent_favorite(self, client):
            # Given
            user = users_factories.UserFactory()

            # When
            response = client.with_token(user.email).delete(f"{FAVORITES_URL}/1203481310")

            # Then
            assert response.status_code == 404


class GetCountTest:
    class Returns200Test:
        def when_user_is_logged_in_but_has_no_favorites(self, client):
            # Given
            user = users_factories.UserFactory()

            # When
            response = client.with_token(user.email).get(FAVORITES_COUNT_URL)

            # Then
            assert response.status_code == 200
            assert response.json == {"count": 0}

        def when_user_is_logged_in_and_has_favorite_offers(self, client):
            # Given
            user = users_factories.UserFactory()
            users_factories.FavoriteFactory.create_batch(size=3, user=user)

            client.with_token(user.email)

            # When
            # QUERY_COUNT:
            # 1: Fetch the user for auth
            # 1: Fetch the favorites count
            with assert_num_queries(2):
                response = client.get(FAVORITES_COUNT_URL)

            # Then
            assert response.status_code == 200
            assert response.json == {"count": 3}
